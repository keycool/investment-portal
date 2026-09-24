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
ABOUT = "一个持续记录市场、公开判断边界并回看错误的交易学习者。"
DISCLAIMER = "本站内容仅为个人市场复盘、投资交易学习和研究记录，不构成投资建议、收益承诺、代客理财或具体买卖指令。市场有风险，任何决策都应基于独立判断并由决策者自行承担结果。"
XUEQIU_TAGS = "#A股复盘 #每日复盘 #交易复盘"
XUEQIU_TAGS_WEEKLY = "#A股复盘 #周度复盘 #交易复盘"
XHS_TAGS = "#A股 #每日复盘 #ETF #投资日记"
# 通用入口 = 个人博客（唯一引流去向）；**站点已于 2026-09-22 上线**，此处与
# `src/data/channels.ts` 的 blogUrl 保持一致（域名 fupanxinyuan.com），改域名时两处同步。
BLOG_URL = "https://www.fupanxinyuan.com"
# 2026-09-24：原「我的博客 · 心猿意马的羊｜交易复盘：A 股每日复盘、历史归档与判断校准的唯一入口」
# 一行，与 channels.ts 的 aboutText 后半句重复（都提完整复盘／历史归档／判断校准）。
# 用户拍板合并为「身份一句 + 博客地址」，故删去 BLOG_INTRO，只留下面这条桥接语。
BLOG_BRIDGE = "完整复盘见博客："

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

# ---- 雪球短评：从摘要里逐字截取三句主干（2026-09-24 改） ----
# 背景：雪球帖原先整段搬运博客摘要（360–570 字），用户反馈「下面的文字太多」。
# 规则固定为「量价（首句）+ 结构/大小盘 + 外围」，**只用原文句子、不新增不改写**；
# 命中不足时按原文顺序补足，最后按原文出现顺序排列。改规则只改这里。
DIGEST_MAX_SENTENCES = 3
DIGEST_KW_STRUCT = ("大小盘", "小盘", "大盘", "微盘", "小票", "两头", "降波")
DIGEST_KW_OUTER = ("外围", "恒指", "纳指", "标普", "道指", "港股", "美股", "隔夜")

def split_sentences(text: str):
    """按中英文句末标点切句，保留标点。"""
    parts = [p for p in re.split(r"(?<=[。！？!?])", (text or "").strip()) if p.strip()]
    if parts:
        return parts
    t = (text or "").strip()
    return [t] if t else []

def pick_digest(summary: str, max_n: int = DIGEST_MAX_SENTENCES) -> str:
    """逐字截取三句主干：首句（通常是量价）+ 结构句 + 外围句。

    **逐字**含义：只按句选取、不做句内增删改写。句子里夹带的 markdown 加粗标记
    （`**`）会被剔除——它是母稿的排版标记，不是内容。
    注意 `DIGEST_KW_STRUCT` 不要放「指数强于」这类**结论短语**：它会命中「领先指数强于上证」
    这类句子，把本该给「结构/大小盘」的顺位抢走（2026-09-23 实测踩到）。
    **也不要放裸词「结构」**（2026-09-24 实测）：它会命中「短期**均线结构**转弱」这种
    *均线*结构句，同样抢走顺位；结构/大小盘用「大小盘/小盘/大盘/微盘/小票」等具体词。
    """
    sents = split_sentences(summary)
    if len(sents) <= max_n:
        return "".join(sents).replace("**", "")
    picked = [0]
    for kws in (DIGEST_KW_STRUCT, DIGEST_KW_OUTER):
        for i, s in enumerate(sents):
            if i in picked:
                continue
            if any(k in s for k in kws):
                picked.append(i)
                break
    for i in range(len(sents)):
        if len(picked) >= max_n:
            break
        if i not in picked:
            picked.append(i)
    picked = sorted(set(picked))[:max_n]
    return "".join(sents[i] for i in picked).replace("**", "")

def bullets_to_plain(block: str) -> str:
    """markdown 无序列表（- **X**：Y）→ 纯文本「· X：Y」，并去掉加粗标记。"""
    out = []
    for line in (block or "").splitlines():
        s = line.strip()
        if not s:
            continue
        s = re.sub(r"^[-*]\s+", "", s).replace("**", "")
        out.append("· " + s)
    return "\n".join(out)

def build_xueqiu(fm, sec, date_stem, month_day):
    title = title_xueqiu(fm.get("title", ""))
    weekly = fm.get("type") == "weekly"
    label_kind = "周度复盘" if weekly else "每日复盘"
    # 标题前缀。2026-09-24 用户反馈「9/23 收盘复盘」里的「收盘」是多余的
    # （题眼本身已含行情描述），故统一收敛为「复盘」/「周度复盘」。
    label_head = "周度复盘" if weekly else "复盘"
    tags = XUEQIU_TAGS_WEEKLY if weekly else XUEQIU_TAGS
    handoff_id = fm.get("id") or f"{fm.get('date','')}-daily"
    poster = Path(fm["poster_src"]).name if fm.get("poster_src") else f"poster-{date_stem}.png"
    digest = pick_digest(fm.get("summary", ""))
    boundary = bullets_to_plain(sec.get("边界与观察", ""))
    head = f"{month_day} {label_head}：{title}"
    # 2026-09-24 用户反馈：草稿文件头（状态/来源/用途/说明等元信息）不必显示，
    # 直接给「可直接使用的正文」。故文件体例收敛为「标题行 + 纯文本正文 + 核对清单」三块。
    return f"""{head}

〔此处插入海报：上传 {poster} 后删掉这一行〕

{title}

{digest}

边界与观察
{boundary}

关于我：{ABOUT}{BLOG_BRIDGE}
{BLOG_URL}

免责声明：{DISCLAIMER}

{tags}

---

## 发布核对清单（发布前逐项过）

- [ ] 标题、题眼、短评、边界与已确认终稿一致（不新增、不改义）
- [ ] 短评只含母版原文句子（脚本自动截取三句主干，未改写）
- [ ] 已上传 `{poster}`（1080×2000 复盘海报），并已删掉正文里的「此处插入海报」占位行
- [ ] 正文里无残留 markdown 标记（`**` / `![` / 行首 `-` / `---`）
- [ ] 数据来源标注为「公开市场数据」，未补造具体行情提供方
- [ ] 无持仓、仓位、账户金额、收益截图或具体买卖动作
- [ ] 免责声明全文与 `docs/content/site-copy.md` 第 7 节一致
- [ ] 博客入口链接无误（站点已上线：{BLOG_URL}）
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
