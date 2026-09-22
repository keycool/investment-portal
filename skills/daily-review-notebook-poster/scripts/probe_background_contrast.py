#!/usr/bin/env python3
"""底图对比度探针：检查所选背景在各文字段落上的可读性（WCAG 对比度）。

为什么需要它：3:4 画布（1086x1448）cover 到 1080x2000 会放大约 1.381x，其
设计安全区通常只到画布 y≈1492，而模板内容一直排到 y1960 —— 页脚（来源 +
免责声明，10px 小字）容易落进底图暗部而不可读（2026-09-14 雾海微明实例：
页脚对比度仅 1.2-2.1:1）。内容高度探针只查「有没有溢出」，查不出「看不看得
清」，两者必须都跑。

本脚本按 CSS `center/cover` 逻辑取背景并缩放到 1080x2000，按模板纵向分段，
段内取亮度均值作为背景，算出各前景色（模板 CSS 变量的 WCAG 等效灰度）对它的
WCAG 对比度；同时打印段内 p5 / min 亮度供参考。

用法:
    python probe_background_contrast.py <background.png> [--dark]

    --dark  深底画布（配 build_poster.py --theme dark 的浅色字），不指定则按
            浅底画布（默认 paper 主题的深色字）计算。

退出码 0 = 全部段落达标；1 = 存在不足段落。

注：BANDS 的 y 区间与 notebook-poster-template.html 的当前布局绑定，模板改版后
需同步更新（区间取的是各段的文字实占纵向范围，略留余量）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

CANVAS_W, CANVAS_H = 1080, 2000
TEXT_BOX = (132, 976)  # 模板 .sheet 的水平范围

# 模板 CSS 变量对应的前景色的 **WCAG 等效灰度**（不是简单灰度换算：暗红 #a61f1f
# 的等效灰度约 85，若按 0xA6=166 直算会把标题强调色误报成不足）。
FG = {
    "paper": {"正文": 20, "强调": 85, "页脚": 87},
    "dark": {"正文": 238, "强调": 223, "页脚": 199},
}

# (段落名, y0, y1, {前景色: 最低要求})
# 阈值按该段在模板里的实际字号取：10-19px 常规文本 4.5:1；>=24px 粗体大文本 3:1；
# 页脚属辅助信息，取 3.5:1（本 Skill 工程口径，低于 AA 严格值，故显式记录）。
# 只对每段真正会出现的前景色判定，避免「页脚色」在正文段误报。
BANDS = [
    ("标题/导语", 150, 345, {"正文": 4.5, "强调": 3.0}),    # 标题第二段 38px 大字
    ("事实/指标", 345, 625, {"正文": 4.5, "强调": 3.0}),    # 四指标数字 30px
    ("三栏结构", 625, 905, {"正文": 4.5, "强调": 4.5}),     # 栏标题 21px + 行文本 16px
    ("判断栏", 905, 1305, {"正文": 4.5, "强调": 4.5}),      # 圆形编号 16px + 正文
    ("验证/总结", 1305, 1650, {"正文": 4.5, "强调": 4.5}),  # 验证正文 15px / 总结 17px
    ("感悟(大字)", 1720, 1800, {"强调": 3.0}),              # 24px 粗体
    ("页脚(小字)", 1925, 1970, {"页脚": 3.5}),              # 10px，只有灰字
]
EDGE_RATIO = 0.9  # 达到阈值的 90% 记「边缘」，不算失败（避免历史已验收成品的噪声）


def rel_lum_gray(v: int) -> float:
    c = v / 255.0
    c = c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return c


def contrast(fg_gray: int, bg_gray: int) -> float:
    a, b = rel_lum_gray(fg_gray), rel_lum_gray(bg_gray)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def cover_canvas(path: Path) -> Image.Image:
    im = Image.open(path).convert("L")
    s = max(CANVAS_W / im.width, CANVAS_H / im.height)
    nw, nh = int(im.width * s + 0.5), int(im.height * s + 0.5)
    im = im.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - CANVAS_W) // 2, (nh - CANVAS_H) // 2
    return im.crop((left, top, left + CANVAS_W, top + CANVAS_H))


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("background", type=Path)
    ap.add_argument("--dark", action="store_true", help="深底画布（浅色字）")
    a = ap.parse_args()

    bg_path = a.background.resolve()
    if not bg_path.exists():
        print(f"背景文件不存在: {bg_path}", file=sys.stderr)
        return 2

    canvas = cover_canvas(bg_path)
    px = canvas.load()
    theme = "dark（浅色字）" if a.dark else "paper（深色字）"
    fgs = FG["dark" if a.dark else "paper"]
    x0, x1 = TEXT_BOX

    print(f"背景 {bg_path.name} -> cover 到 {CANVAS_W}x{CANVAS_H} | 主题 {theme}")
    print(f"文字框 x[{x0},{x1}]；背景取段内亮度均值，前景色用 WCAG 等效灰度近似\n")

    header = f"{'段落':<12}{'y区间':<13}{'背景 mean/p5/min':<20}" + "".join(
        f"{k + '对比度':<14}" for k in fgs
    )
    print(header)
    print("-" * len(header))

    fails, edges = [], []
    for name, y0, y1, spec in BANDS:
        vals = []
        for y in range(y0, y1, 3):
            for x in range(x0, x1, 3):
                vals.append(px[x, y])
        if not vals:
            continue
        vals.sort()
        n = len(vals)
        mean = sum(vals) / n
        p5 = vals[int(n * 0.05)]
        # 背景代表值取段内均值：文字是稀疏笔画，其落点是平滑背景区；p5/min 是
        # 最暗像素，会被纸面模板的装饰笔画（钢笔/木桌边）拖出假警报，仅作参考。
        bg = int(round(mean))
        cells = []
        for k, fg in fgs.items():
            if k not in spec:
                cells.append("-")
                continue
            need = spec[k]
            r = contrast(fg, bg)
            if r >= need:
                tag = ""
            elif r >= need * EDGE_RATIO:
                tag = "  ~边缘"
                edges.append((name, k, r, need))
            else:
                tag = "  <<<不足"
                fails.append((name, k, r, need))
            cells.append(f"{r:.2f}{tag}")
        print(
            f"{name:<12}{f'{y0}-{y1}':<13}{f'{mean:.0f}/{p5}/{vals[0]}':<20}"
            + "".join(f"{c:<14}" for c in cells)
        )

    print()
    for name, k, r, need in edges:
        print(f"边缘：{name} 的{k} {r:.2f}:1（阈值 {need}，达 {r / need * 100:.0f}%）")

    if fails:
        print("结论：NOT PASS")
        for name, k, r, need in fails:
            print(f"  - {name} 的{k}仅 {r:.2f}:1（需 >= {need}:1）")
        print("  修法（都需用户确认，不得擅自执行）：")
        print("   1) 底图下段渐变提亮（画布 y1500 起与纯白 alpha 0→0.72 线性混合，会洗淡底图）")
        print("   2) 模板 footer 加浅色衬底（不动底图，跨背景通用）")
        return 1

    print("结论：PASS —— 各段落对比度均达标" + ("（含边缘项，见上）" if edges else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
