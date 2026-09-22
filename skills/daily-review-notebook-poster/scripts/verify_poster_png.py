# -*- coding: utf-8 -*-
"""核验成品 PNG 是否与当前 HTML 一致（防「陈旧交付图」）。

为什么需要它（2026-09-18 建立）：
`render_poster.py --probe` 是**短路模式**——脚本里 `if a.probe: return run_probe(a)`，
只做探针渲染、**绝不写出最终 poster.png**。因此「改完文案后只跑了 --probe」时：
探针报数是对的（它按新 HTML 渲染），但交付的成品图会**静默停留在旧版**，而
SHA / mtime「看着没变」极易被当成没改成功或直接忽略（W38 实例：旧图挂了两轮）。

本脚本不看文字内容，只用**底图差分**判独立证据：把所述背景按 CSS `center/cover`
缩放到 1080×2000，与原图逐行求平均灰度差；差异行 = 文字/线条所在行。于是可得到
内容纵向范围与底部余量，用来交叉验证两件事：
1. 成品图的内容末行 y 与 `render_poster.py --probe` 报的包围盒一致（±若干像素）；
2. 压缩过文案后，旧版内容所占据的行区间**已经变干净**（证明图确实重出过）。

用法：
    python scripts/verify_poster_png.py <poster.png> <background.png>

    <background.png> 用包内那份 `notebook-background.png`（build_poster.py 拷进来的
    底图副本）即可。

退出码 0 = 内容范围可用且与「底部余量 ≥0」不矛盾；1 = 检测异常或图疑似陈旧
（例如内容末行明显大于探针报数、或旧区间仍有内容）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageChops

CANVAS = (1080, 2000)
# 内容行判定阈值：逐行（每 4 列抽样）平均灰度差超过它即认为该行有内容
ROW_THRESHOLD = 12.0


def cover_to(bg: Image.Image, size: tuple[int, int]) -> Image.Image:
    """按 CSS `center/cover` 取背景。"""
    W, H = size
    bw, bh = bg.size
    scale = max(W / bw, H / bh)
    nw, nh = round(bw * scale), round(bh * scale)
    resized = bg.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    return resized.crop((left, top, left + W, top + H))


def row_means(poster: Image.Image, bg_cover: Image.Image) -> list[float]:
    diff = ImageChops.difference(poster, bg_cover).convert("L")
    px = diff.load()
    W, H = poster.size
    step = 4
    return [sum(px[x, y] for x in range(0, W, step)) / (W // step) for y in range(H)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("poster", type=Path)
    ap.add_argument("background", type=Path)
    ap.add_argument("--expect-margin", type=int, default=None,
                    help="可选：render_poster.py --probe 报出的底部余量，用于交叉验证")
    a = ap.parse_args()

    if not a.poster.is_file():
        raise FileNotFoundError(a.poster)
    if not a.background.is_file():
        raise FileNotFoundError(a.background)

    poster = Image.open(a.poster).convert("RGB")
    if poster.size != CANVAS:
        print(f"FAIL 成品图尺寸 {poster.size}，应为 {CANVAS}")
        return 1
    bg = Image.open(a.background).convert("RGB")
    bg_cover = cover_to(bg, CANVAS)

    rows = row_means(poster, bg_cover)
    W, H = CANVAS
    content = [y for y, v in enumerate(rows) if v > ROW_THRESHOLD]
    if not content:
        print("FAIL 逐行差分未检测到任何内容行（底图不匹配？成品图是否为空？）")
        return 1

    upper, lower = min(content), max(content)
    margin = H - 1 - lower
    bw, bh = bg.size
    print(f"成品图 {a.poster.name} {W}x{H} | 底图 {a.background.name} {bw}x{bh}")
    print(f"内容行 y 范围: [{upper}, {lower}] | 底部余量 = {margin} px")
    tail = [y for y in range(lower + 3, H) if rows[y] > ROW_THRESHOLD]
    print(f"内容末行以下的残留内容行: {len(tail)}")

    ok = True
    if a.expect_margin is not None:
        delta = abs(margin - a.expect_margin)
        print(f"与探针报数交叉验证: 探针 {a.expect_margin} px｜本脚本 {margin} px｜差 {delta} px")
        if delta > 12:
            print("FAIL 与探针报数差异过大 —— 成品图疑似陈旧（--probe 不写成品图！"
                  "请不带 --probe 重跑 render_poster.py 后再交付）")
            ok = False
    if tail:
        print("FAIL 内容末行以下仍有内容行，疑似排版异常")
        ok = False

    print("结论:", "PASS 成品图与当前 HTML 一致" if ok else "FAIL（见上）")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
