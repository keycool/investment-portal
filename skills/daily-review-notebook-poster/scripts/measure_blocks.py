"""测量笔记本海报各内容块的实际行数，用于定位探针余量被谁吃掉。

用法：
    python scripts/measure_blocks.py <poster.html> [--browser <chrome.exe>]

背景：`render_poster.py --probe` 只报一个「底部余量」总数，不告诉你哪一块在吃高度。
本脚本在临时副本里注入测量脚本、用 headless Chrome 求出各块的行数，一次看清
「标题几行 / 导语几行 / 两条事实几行 / 三栏每格几行（含是否折行）/ 判断栏几行 /
总结几行 / 金句几行 / 三项验证几行」。属诊断工具，不产出交付物。

注意（2026-09-15 实测）：
- Chrome 路径与渲染脚本的 `candidates()` 同源，优先读 CHROME_PATH。
- `getBoundingClientRect()` 返回的是**含 .sheet scale(1.18) 的值**，本脚本已按 1.18 还原。
- 三栏逐项会额外打印 rect 明细（x 区间 + y）。同一 y 的多个 rect 属同一行；
  出现第二个 y 即说明该格折行（0917 实例：`领先指数` 值超列内可用宽 192px，末字成孤儿）。
- 已知各块上限：标题第二行 ≤10 字；判断栏每格 body ≤3 行；总结 ≤2 行；
  三栏每格 ≤5 行；事实每条 2–3 行；金句 1–2 行。
- 金句含 `<br>`（双行）时，`<br>` 会额外产生一个 width=0 的 rect。本脚本已过滤零宽
  rect（2026-09-18 修），否则 W38 的 2 行金句会被误报成 3 行、看起来超出 1–2 行上限。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SHEET_SCALE = 1.18

PROBE_JS = """
<script>
window.addEventListener('load', () => {
  function rects(el) {
    const r = document.createRange();
    r.selectNodeContents(el);
    // 过滤零宽 rect：<br> 会在行尾产生一个 width=0 的空 rect，
    // 不过滤会把「双行金句」误计成 3 行（2026-09-18 实测）。
    return Array.from(r.getClientRects()).filter(x => x.width > 0.5);
  }
  function lines(el) { return rects(el).length; }
  const out = {};
  const h1 = document.querySelector('h1');
  out.h1_lines = Math.round(h1.getBoundingClientRect().height / SHEET_SCALE / 47.5 * 100) / 100;
  out.lead = document.querySelector('.lead') ? lines(document.querySelector('.lead')) : 0;
  out.facts = Array.from(document.querySelectorAll('.bullets li')).map(lines);
  out.cols = Array.from(document.querySelectorAll('.note-col')).map(
    c => Array.from(c.querySelectorAll('li')).map(lines));
  out.cols_rects = Array.from(document.querySelectorAll('.note-col')).map(
    c => Array.from(c.querySelectorAll('li')).map(li => rects(li).map(
      x => Math.round(x.left) + '..' + Math.round(x.right) + '@' + Math.round(x.top))));
  out.judg = Array.from(document.querySelectorAll('.judgment')).map(
    j => [lines(j.querySelector('b')), lines(j.querySelector('p'))]);
  out.summary = document.querySelector('.summary p') ? lines(document.querySelector('.summary p')) : 0;
  out.quote = document.querySelector('.quote') ? lines(document.querySelector('.quote')) : 0;
  out.watches = Array.from(document.querySelectorAll('.watch p')).map(lines);
  document.documentElement.setAttribute('data-measure', JSON.stringify(out));
});
</script>
""".replace("SHEET_SCALE", str(SHEET_SCALE))


def candidates() -> list[str]:
    values: list[str] = []
    if os.environ.get("CHROME_PATH"):
        values.append(os.environ["CHROME_PATH"])
    for name in ("google-chrome", "google-chrome-stable", "chromium",
                 "chromium-browser", "chrome", "msedge"):
        values.append(name)
    if sys.platform == "win32":
        values += [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
    elif sys.platform == "darwin":
        values += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                   "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    return values


def resolve_browser(explicit: str | None) -> str:
    if explicit:
        return explicit
    for v in candidates():
        if Path(v).is_file():
            return v
    return ""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("html", type=Path)
    p.add_argument("--browser", type=str, default=None)
    p.add_argument("--timeout", type=int, default=120)
    a = p.parse_args()

    html_path = a.html.resolve()
    if not html_path.is_file():
        print(f"not found: {html_path}")
        return 1
    browser = resolve_browser(a.browser)
    if not browser:
        print("No Chrome/Chromium/Edge found. Set CHROME_PATH or pass --browser.")
        return 1

    src = html_path.read_text(encoding="utf-8")
    staged = Path(tempfile.mkdtemp(prefix="measure-blocks-")) / "measure.html"
    staged.write_text(src.replace("</body>", PROBE_JS + "</body>"), encoding="utf-8")
    cmd = [
        browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--allow-file-access-from-files", "--force-device-scale-factor=1",
        "--no-first-run", "--no-default-browser-check",
        "--virtual-time-budget=3000", "--dump-dom", staged.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                         errors="replace", timeout=a.timeout)
    m = re.search(r'data-measure="(.*?)"\s*>', res.stdout or "", re.S)
    if not m:
        print("measurement not found; dump head:")
        print((res.stdout or "")[:1000])
        print("stderr:", (res.stderr or "")[:1000])
        return 1

    raw = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
           .replace("&lt;", "<").replace("&gt;", ">"))
    d = json.loads(raw)

    print(f"browser: {browser}")
    print(f"h1 高度(未缩放) = {d['h1_lines'] * 47.5:.1f}px -> {d['h1_lines']} 行")
    print(f"lead     {d['lead']}")
    print(f"facts    {d['facts']}")
    print(f"cols     {d['cols']}")
    print(f"judg     {d['judg']}   [标题行数, 正文行数]")
    print(f"summary  {d['summary']}")
    print(f"quote    {d['quote']}")
    print(f"watches  {d['watches']}")

    print("--- 三栏逐项 rect（同一 y = 同一行；出现第二个 y 即折行）---")
    for ci, col in enumerate(d["cols_rects"], 1):
        for ii, rects in enumerate(col, 1):
            tops = {r.split("@")[1] for r in rects}
            flag = "  <-- 折行" if len(tops) > 1 else ""
            print(f"  列{ci} 项{ii}: {rects}{flag}")

    print(f"\n(诊断副本留在 {staged.parent} ，可自行清理)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
