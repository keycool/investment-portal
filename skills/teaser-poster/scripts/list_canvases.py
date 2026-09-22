#!/usr/bin/env python3
"""List available canvas packs in the shared canvas library.

数据驱动：扫描画布库（默认 D:\\CC\\shared\\assets\\canvases\\），读取每个包的
canvas.json + variants.json，打印选择表：pack / variant / 尺寸 / 安全区 / SHA /
mood / 描述。新包只要符合 canvas-library.md 的最小准入标准，无需改代码。

用法:
  python list_canvases.py                     # 打印全部可选背景
  python list_canvases.py --mood playful      # 按 mood 过滤
  python list_canvases.py --json              # JSON 输出（供脚本消费）
  CANVAS_LIB=<path> python list_canvases.py   # 指定库路径
"""
from __future__ import annotations
import argparse, json, os, struct, sys
from pathlib import Path

DEFAULT_LIB = Path(r"D:\CC\shared\assets\canvases")
USAGE_NAMES = ("USAGE.md", "USAGE", "usage.md", "usage")

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"__error__": str(e)}

def png_size(path: Path):
    try:
        with path.open("rb") as f:
            h = f.read(24)
        if h[:8] == b"\x89PNG\r\n\x1a\n" and h[12:16] == b"IHDR":
            return struct.unpack(">II", h[16:24])
    except Exception:
        pass
    return None

def collect(lib: Path):
    rows, errors = [], []
    for pack_dir in sorted(lib.glob("*")):
        if not pack_dir.is_dir() or pack_dir.name.startswith("."):
            continue
        canvas_path = pack_dir / "canvas.json"
        variants_path = pack_dir / "variants.json"
        canvas = read_json(canvas_path) if canvas_path.is_file() else {}
        variants = read_json(variants_path) if variants_path.is_file() else {}
        usage = next((pack_dir / n for n in USAGE_NAMES if (pack_dir / n).is_file()), None)
        if canvas.get("__error__"):
            errors.append({"pack": pack_dir.name, "file": "canvas.json", "message": canvas["__error__"]}); continue
        if variants_path.is_file() and variants.get("__error__"):
            errors.append({"pack": pack_dir.name, "file": "variants.json", "message": variants["__error__"]}); continue

        pack_mood = canvas.get("mood", [])
        # variants 列表：有 variants.json 用其 variants；否则退化为单变体（canvas.json）
        vlist = variants.get("variants") if variants.get("variants") else [{
            "id": canvas.get("id", pack_dir.name),
            "file": canvas.get("file"),
            "metadata_file": "canvas.json",
            "description": canvas.get("visual_elements") or canvas.get("visual_language") or "",
        }]
        for v in vlist:
            if not isinstance(v, dict):
                continue
            fname = v.get("file")
            fpath = pack_dir / fname if fname else None
            rows.append({
                "pack": pack_dir.name,
                "variant": v.get("id") or fname,
                "file": fname,
                "name_cn": v.get("name_cn") or canvas.get("name_cn") or pack_dir.name,
                "native_size": v.get("native_size") or canvas.get("native_size"),
                "text_area": v.get("recommended_text_area") or canvas.get("recommended_text_area"),
                "sha256": v.get("sha256") or canvas.get("sha256"),
                "mood": v.get("mood") or pack_mood,
                "description": v.get("description", ""),
                "png_actual_size": png_size(fpath) if fpath and fpath.is_file() else None,
                "usage": usage.name if usage else None,
            })
    return rows, errors

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lib", type=Path, default=Path(os.environ.get("CANVAS_LIB", DEFAULT_LIB)))
    ap.add_argument("--mood", help="按 mood 过滤（如 professional / playful / dreamy）")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    a = ap.parse_args()

    if not a.lib.is_dir():
        print(f"画布库不存在: {a.lib}", file=sys.stderr); return 2
    rows, errors = collect(a.lib)
    if a.mood:
        rows = [r for r in rows if a.mood in (r.get("mood") or [])]

    if a.json:
        print(json.dumps({"library": str(a.lib), "backgrounds": rows, "errors": errors},
                         ensure_ascii=False, indent=2))
        return 0

    print(f"画布库: {a.lib}")
    print(f"可选背景: {len(rows)} 个" + (f"（mood 过滤: {a.mood}）" if a.mood else ""))
    print("-" * 96)
    for r in rows:
        area, size = r["text_area"], r["native_size"]
        sa = f"x{area['x']},y{area['y']},{area['width']}x{area['height']}" if area else "?"
        sz = f"{size[0]}x{size[1]}" if size else "?"
        mood = ",".join(r["mood"]) if r["mood"] else "-"
        flag = "" if r["usage"] else "  ⚠️缺USAGE"
        print(f"[{r['pack']}] {r['name_cn']}（{r['variant']}）  {sz}  安全区:{sa}  mood:{mood}{flag}")
        if r.get("sha256"):
            print(f"    SHA {r['sha256']}")
        if r.get("description"):
            print(f"    {r['description']}")
        if r.get("png_actual_size") and r["png_actual_size"] != tuple(size or ()):
            print(f"    ⚠️ PNG实际尺寸 {r['png_actual_size'][0]}x{r['png_actual_size'][1]} 与元数据不一致")
    if errors:
        print("-" * 96)
        for e in errors:
            print(f"❌ [{e['pack']}] {e['file']}: {e['message']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
