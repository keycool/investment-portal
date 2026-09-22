#!/usr/bin/env python3
"""Build a notebook-style review poster HTML from validated JSON."""
from __future__ import annotations
import argparse, html, json, os, re, shutil
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; ASSETS=ROOT/"assets"; TEMPLATE=ASSETS/"notebook-poster-template.html"; DIRECTIONS={"red","green","neutral"}

# 日稿与周稿共用同一模板，类型字样由输入 JSON 的 type 决定（缺省 daily）。
# 2026-09-12 修正：此前「日复盘」字样写死在模板里，周稿成品会被误标成「日复盘」（W36 已受影响）。
POSTER_KIND = {
    "daily": {"kind": "日复盘笔记本海报", "page": "A股日复盘｜笔记本海报", "section1": "今天发生了什么？"},
    "weekly": {"kind": "周复盘笔记本海报", "page": "A股周复盘｜笔记本海报", "section1": "本周发生了什么？"},
}

# 深底画布（如「星云随笔」深靛蓝底）需要把文字翻成浅色系，否则模板默认深色字不可读。
# 沿用 2026-09-09 星云版定版配色，逐字一致，不要临场调。
THEME_PAPER = {
    ":root{--ink:#171411;--red:#a61f1f;--green:#197458;--muted:#5f554b;--rule:#81766b}":
    ":root{--ink:#F5EEDD;--red:#F2DDB4;--green:#A8D8C4;--muted:#C9C2E8;--rule:#8D84B0}",
    "background:#b8814f url(":
    "background:#202C50 url(",
}

def apply_theme(output: str, theme: str) -> str:
    """theme='dark' 时为深底画布翻浅色系；找不到目标串即报错，不静默跳过。"""
    if theme != "dark":
        return output
    for old, new in THEME_PAPER.items():
        if old not in output:
            raise ValueError(f"theme=dark 替换目标未命中，模板可能已变，请核对: {old[:48]}...")
        output = output.replace(old, new)
    return output

def _default_background() -> Path:
    """背景从画布库 notebook-paper 包读取（唯一权威源），支持 CANVAS_LIB 环境变量。"""
    env = os.environ.get("CANVAS_LIB")
    if env:
        return Path(env) / "notebook-paper" / "background.png"
    # scripts/ → skills/ → investment-portal/ → shared/assets/canvases/notebook-paper/
    return Path(__file__).resolve().parents[4] / "assets" / "canvases" / "notebook-paper" / "background.png"

def required(value, field):
    if not isinstance(value,str) or not value.strip(): raise ValueError(f"{field} must be a non-empty string")
    return value.strip()
def esc(value, field): return html.escape(required(value,field),quote=True).replace("\n","<br>")
def items(data, field, exact=None):
    value=data.get(field)
    if not isinstance(value,list): raise ValueError(f"{field} must be a list")
    if exact is not None and len(value)!=exact: raise ValueError(f"{field} must contain exactly {exact} items")
    return value
def direction(value, field):
    value=required(value,field)
    if value not in DIRECTIONS: raise ValueError(f"{field} must be one of {sorted(DIRECTIONS)}")
    return value

def render(data, theme="paper"):
    iso=required(data.get("date"),"date"); date.fromisoformat(iso)
    poster_type=required(data.get("type","daily"),"type")
    if poster_type not in POSTER_KIND: raise ValueError(f"type must be one of {sorted(POSTER_KIND)}")
    kind=POSTER_KIND[poster_type]
    titles=items(data,"title",2); tags=items(data,"section_taglines",4); facts=items(data,"facts",2); metrics=items(data,"metrics",4); columns=items(data,"columns",3); judgments=items(data,"judgments",4); watches=items(data,"watches",3)
    facts_html="".join(f"<li>{esc(x,'facts[]')}</li>" for x in facts)
    metric_html=[]
    for i,x in enumerate(metrics,1):
        if not isinstance(x,dict): raise ValueError(f"metrics[{i}] must be an object")
        css=direction(x.get("direction"),f"metrics[{i}].direction")
        metric_html.append(f'<div class="metric {css}"><strong>{esc(x.get("value"),"metric value")}</strong><span>{esc(x.get("label"),"metric label")}<br>{esc(x.get("meaning"),"metric meaning")}</span></div>')
    column_html=[]
    for i,column in enumerate(columns,1):
        if not isinstance(column,dict): raise ValueError(f"columns[{i}] must be an object")
        rows=items(column,"items")
        if not 3<=len(rows)<=5: raise ValueError(f"columns[{i}].items must contain 3 to 5 items")
        row_html=[]
        for j,row in enumerate(rows,1):
            if not isinstance(row,dict): raise ValueError(f"columns[{i}].items[{j}] must be an object")
            css=direction(row.get("direction"),"column direction")
            row_html.append(f'<li><span>{esc(row.get("label"),"column label")}</span> <b class="{css}">{esc(row.get("value"),"column value")}</b></li>')
        column_html.append(f'<div class="note-col"><h3>{esc(column.get("title"),"column title")}</h3><ul>{"".join(row_html)}</ul></div>')
    judgment_html=[]
    for i,x in enumerate(judgments,1):
        if not isinstance(x,dict): raise ValueError(f"judgments[{i}] must be an object")
        judgment_html.append(f'<div class="judgment" data-no="{i}"><b>{esc(x.get("title"),"judgment title")}</b><p>{esc(x.get("body"),"judgment body")}</p></div>')
    watch_html=[]
    for i,x in enumerate(watches,1):
        if not isinstance(x,dict): raise ValueError(f"watches[{i}] must be an object")
        watch_html.append(f'<div class="watch"><b>{esc(x.get("title"),"watch title")}</b><p>{esc(x.get("body"),"watch body")}</p></div>')
    values={"PAGE_TITLE":f"{iso} {kind['page']}","POSTER_KIND":kind["kind"],"SECTION1_TITLE":kind["section1"],"ISSUE":esc(data.get("issue"),"issue"),"TITLE_1":esc(titles[0],"title[0]"),"TITLE_2":esc(titles[1],"title[1]"),"DISPLAY_DATE":esc(data.get("display_date"),"display_date"),"AUTHOR":esc(data.get("author","心猿意马的羊"),"author"),"LEAD":esc(data.get("lead"),"lead"),"TAGLINE_1":esc(tags[0],"tagline 1"),"TAGLINE_2":esc(tags[1],"tagline 2"),"TAGLINE_3":esc(tags[2],"tagline 3"),"TAGLINE_4":esc(tags[3],"tagline 4"),"FACTS_HTML":facts_html,"METRICS_HTML":"".join(metric_html),"COLUMNS_HTML":"".join(column_html),"JUDGMENTS_HTML":"".join(judgment_html),"WATCHES_HTML":"".join(watch_html),"SUMMARY":esc(data.get("summary"),"summary"),"QUOTE":esc(data.get("quote"),"quote"),"SOURCE_TEXT":esc(data.get("source_text"),"source_text"),"DISCLAIMER":esc(data.get("disclaimer"),"disclaimer"),"DATE_ISO":iso}
    output=TEMPLATE.read_text(encoding="utf-8")
    for key,value in values.items(): output=output.replace("{{"+key+"}}",value)
    remaining=sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}",output)))
    if remaining: raise ValueError(f"unresolved placeholders: {remaining}")
    return apply_theme(output, theme)

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("input",type=Path); p.add_argument("--output-dir",type=Path,required=True); p.add_argument("--stem",required=True); p.add_argument("--background",type=Path,default=_default_background()); p.add_argument("--theme",choices=["paper","dark"],default="paper",help="paper=浅底画布（默认深色字）；dark=深底画布（翻浅色字，配星云等）"); p.add_argument("--force",action="store_true"); a=p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9._-]+",a.stem): raise ValueError("invalid --stem")
    data=json.loads(a.input.read_text(encoding="utf-8"));
    if not isinstance(data,dict): raise ValueError("input JSON root must be an object")
    out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True); html_path=out/f"{a.stem}.html"; background_path=out/"notebook-background.png"
    for path in (html_path,background_path):
        if path.exists() and not a.force: raise FileExistsError(f"refusing to overwrite {path}; use --force deliberately")
    html_path.write_text(render(data,a.theme),encoding="utf-8",newline="\n"); shutil.copy2(a.background.resolve(),background_path); print(html_path); print(background_path); return 0
if __name__=="__main__": raise SystemExit(main())

