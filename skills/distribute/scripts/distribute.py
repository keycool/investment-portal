#!/usr/bin/env python3
"""从博客 MDX 派生分发草稿（半自动）。

分发结构（2026-08-31 调整）：个人博客 = 中心/最终承接；雪球 = 主打引流战场（active）；
小红书引流板 = 暂停（paused，默认不产出，恢复时加 --with-xhs）。

单向降级链：博客 MDX（母版）→ 雪球「海报 + 短评」。
- 雪球 = 主图海报(2000) + 题眼/摘要/边界短评，完整长文在博客。
- 小红书 = 引流版海报(1440) + 一句话钩子（默认暂停；--with-xhs 时生成）。
题眼 / 摘要 / 边界口径逐字取自博客，不新增不改义。
产出是「草稿 + 发布核对清单」，人工逐项过目后才可发布。

用法:
  python distribute.py <mdx路径> [--date YYYYMMDD] [--out 目录] [--with-xhs]
  例: python distribute.py src/content/reviews/daily/2026-08-26.mdx
      → 在当前目录生成 xueqiu-publish-draft-20260826.md（小红书默认暂停）
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# ---- 固定文案（与 src/data/channels.ts 保持一致）----
ABOUT = "一个持续记录市场、公开判断边界并回看错误的交易学习者。完整复盘、历史归档与后续校准见博客「心猿意马的羊｜交易复盘」。"
DISCLAIMER = "本站内容仅为个人市场复盘、投资交易学习和研究记录，不构成投资建议、收益承诺、代客理财或具体买卖指令。市场有风险，任何决策都应基于独立判断并由决策者自行承担结果。"
XUEQIU_TAGS = "#A股复盘 #每日复盘 #交易复盘"
XUEQIU_TAGS_WEEKLY = "#A股复盘 #周度复盘 #交易复盘"
XHS_TAGS = "#A股 #每日复盘 #ETF #投资日记"
# 通用入口 = 个人博客（唯一引流去向）；当前为内网临时地址，真实域名上线后替换 channels.ts 的 blogUrl 并同步此处
BLOG_URL = "https://www.fupanxinyuan.com"
BLOG_INTRO = "A 股每日复盘、历史归档与判断校准的唯一入口"

def parse_mdx(text: str):
    """解析 frontmatter + 按 ## 章节分割正文。"""
    fm = {}
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    body = text[fm_match.end():] if fm_match else text
    if fm_match:
        fmtext = fm_match.group(1)
        for line in fmtext.splitlines():
            m = re.match(r"^(title|summary|date|data_as_of|type|id):\s*(.+?)\s*$", line)
            if m:
                fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
        pm = re.search(r"^poster:\s*\n\s*src:\s*(.+?)\s*$", fmtext, re.M)
        if pm:
            fm["poster_src"] = pm.group(1).strip().strip('"').strip("'")
    sections, cur = {}, None
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+)$", line)
        if m:
            cur = m.group(1).strip(); sections[cur] = []
        elif cur is not None:
            sections[cur].append(line)
    sections = {k: "\n".join(v).strip() for k, v in sections.items()}
    return fm, sections

def strip_marker(s: str) -> str:
    """去掉「**确认原文**」标记（粗体小标题行）。"""
    lines = []
    for line in s.splitlines():
        if line.strip() == "**确认原文**":
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def title_xueqiu(title: str) -> str:
    return title.replace(" / ", "，").replace("/", "，")

def build_xueqiu(fm, sec, date_stem, month_day):
    title = title_xueqiu(fm.get("title", ""))
    weekly = fm.get("type") == "weekly"
    label_kind = "周度复盘" if weekly else "每日复盘"
    label_head = "周度复盘" if weekly else "收盘复盘"
    tags = XUEQIU_TAGS_WEEKLY if weekly else XUEQIU_TAGS
    handoff_id = fm.get("id") or f"{fm.get('date','')}-daily"
    poster = Path(fm["poster_src"]).name if fm.get("poster_src") else f"poster-{date_stem}.png"
    summary = fm.get("summary", "")
    boundary = sec.get("边界与观察", "")
    return f"""# 雪球发布版 · {fm.get('date','')} {label_kind}（分发草稿）

> 状态：draft（待用户确认后发布）
> 来源：博客 MDX + `content-inbox/{handoff_id}/handoff.md`（已确认终稿）
> 用途：雪球发布 = 主图海报 + 突出重点短评（完整长文在个人博客）；题眼/摘要/边界口径逐字取自博客，不新增、不改义。
> 发布时：上传 `{poster}`（1080×2000 复盘海报）；正文尾部已附博客入口（当前为内网临时地址，真实域名上线后替换）。

---

## 标题（发帖用）

```
{month_day} {label_head}：{title}
```

## 正文（Markdown，可直接粘贴雪球长文编辑器）

---

**{month_day} {label_head}：{title}**

![复盘海报]({poster})

**{title}**

{summary}

**边界与观察**

{boundary}

---

**关于我**：{ABOUT}

**我的博客 · 心猿意马的羊｜交易复盘**：{BLOG_INTRO}
{BLOG_URL}

**免责声明**：{DISCLAIMER}

{tags}

---

## 发布核对清单（发布前逐项过）

- [ ] 标题、题眼、摘要、边界与已确认终稿一致（不新增、不改义）
- [ ] 已上传 `{poster}`（1080×2000 复盘海报）
- [ ] 数据来源标注为「公开市场数据」，未补造具体行情提供方
- [ ] 无持仓、仓位、账户金额、收益截图或具体买卖动作
- [ ] 免责声明全文与 `docs/content/site-copy.md` 第 7 节一致
- [ ] 博客入口链接无误（当前为内网临时地址 {BLOG_URL}，真实域名上线后替换）
- [ ] 发布到雪球「文章」而非「讨论」
"""

def build_xhs(fm, sec, date_stem, month_day):
    title = title_xueqiu(fm.get("title", ""))
    teaser = f"poster-{date_stem}-teaser.png"
    feeling = strip_marker(sec.get('个人感悟',''))
    return f"""# 小红书发布版 · {fm.get('date','')} 每日复盘（分发草稿）

> 状态：draft（待用户确认后发布）
> 来源：博客 MDX + `content-inbox/{fm.get('date','')}-daily/handoff.md`（已确认终稿）
> 用途：小红书图文发布。**只发海报 + 短文案**，不放长文（长文体验差、限流风险高）。
> 发布时：上传 `{teaser}`（1080×1440 引流版）；正文不放任何外链/二维码/微信号。

---

## 标题（三选一，建议 A/B 测两天）

- **A（信息型）**：`{title}｜{month_day} A股收盘复盘`
- **B（金句型）**：`{feeling[:24]}…｜{month_day}复盘`  ← 人工润色
- **C（悬念型）**：`{{SUSPENSE}}`  ← 人工填（如「缩量普涨，是反抽还是新起点？」）

（小红书标题 ≤ 20 字最佳，带"复盘/ETF/指数"等搜索词。）

## 正文（配图：{teaser}）

```
{month_day} 收盘复盘。

{fm.get('summary','')}

{{HOOK}}  ← 人工填一句钩子（如金句或反问）

📌 每日复盘、历史归档与后续校准见同名博客「心猿意马的羊｜交易复盘」
不荐股 · 不晒持仓 · 数据日期可见 · 原判断不覆盖
```

## 标签

`{XHS_TAGS}`

（标签 4-6 个即可；前两个必须是内容关键词。）

## 发布核对清单

- [ ] 海报为 `{teaser}`（1080×1440 引流版，非 2000 长图）
- [ ] 标题未用「抄底 / 必涨 / 翻倍 / 稳赚」等敏感词
- [ ] 正文无外链、无二维码、无微信号、无收益截图
- [ ] 正文含免责性表述（不荐股·不晒持仓）
- [ ] CTA 只用「搜索站内 / 同名博客」类引导，不写具体 URL
- [ ] 发布后 30 分钟看一次限流提示

## 定位备忘（每次发布前默读一遍）

小红书是**曝光/人设渠道**，不是转化渠道。站外链接受限，它的任务是让更多人持续看到「心猿意马的羊」在稳定、准时、可校准地做公开复盘；把读者带到完整版博客的主链路是雪球/知乎。流量慢是正常的，留存质量比瞬时流量重要。
"""

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mdx", type=Path)
    ap.add_argument("--out", type=Path, default=Path("."))
    ap.add_argument("--date", help="日期 stem（默认从 frontmatter date 提取）")
    ap.add_argument("--with-xhs", action="store_true", help="同时生成小红书草稿（默认暂停，不产出）")
    a = ap.parse_args()
    text = a.mdx.read_text(encoding="utf-8")
    fm, sec = parse_mdx(text)
    date = fm.get("date", "")
    if not date:
        print("无法从 frontmatter 提取 date", file=sys.stderr); return 2
    date_stem = (a.date or date).replace("-", "")
    month_day = f"{int(date[5:7])}/{int(date[8:10])}"
    a.out.mkdir(parents=True, exist_ok=True)
    xq = a.out / f"xueqiu-publish-draft-{date_stem}.md"
    xq.write_text(build_xueqiu(fm, sec, date_stem, month_day), encoding="utf-8")
    print(f"已生成: {xq}")
    if a.with_xhs:
        xhs = a.out / f"xhs-publish-draft-{date_stem}.md"
        xhs.write_text(build_xhs(fm, sec, date_stem, month_day), encoding="utf-8")
        print(f"已生成: {xhs}")
    else:
        print("小红书草稿：paused（2026-08-31 起暂停，加 --with-xhs 恢复生成）")
    print("注意：关键事实表「说明」列需人工补。")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
