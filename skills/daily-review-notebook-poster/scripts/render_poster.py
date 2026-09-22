#!/usr/bin/env python3
"""Render a fixed 1080x2000 HTML poster with a Chromium-family browser."""
from __future__ import annotations
import argparse, os, shutil, struct, subprocess, sys, tempfile, time
from pathlib import Path
WIDTH=1080; HEIGHT=2000
PROBE_HEIGHT=2600   # 探针画布高度：高于 2000 以便量出溢出量，不会被画布裁切误报
PROBE_INK_THRESHOLD=246  # 亮度低于该值视为「内容像素」（白底扫描）

def candidates():
    values=[]
    if os.environ.get("CHROME_PATH"): values.append(os.environ["CHROME_PATH"])
    for name in ("google-chrome","google-chrome-stable","chromium","chromium-browser","chrome","msedge"):
        found=shutil.which(name)
        if found: values.append(found)
    if sys.platform=="win32": values += [r"C:\Program Files\Google\Chrome\Application\chrome.exe",r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
    elif sys.platform=="darwin": values += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","/Applications/Chromium.app/Contents/MacOS/Chromium"]
    result=[]
    for value in values:
        path=str(Path(value).expanduser())
        if Path(path).is_file() and path not in result: result.append(path)
    return result

def dimensions(path):
    with path.open("rb") as f: header=f.read(24)
    if len(header)!=24 or header[:8]!=b"\x89PNG\r\n\x1a\n" or header[12:16]!=b"IHDR": raise ValueError(f"not a valid PNG: {path}")
    return struct.unpack(">II",header[16:24])

# 减少 Chrome 残留子进程（GPU/crashpad/后台网络），降低 profile 文件句柄占用，让临时目录能被干净删除
_EXTRA_ARGS=["--disable-background-networking","--disable-component-update","--disable-crash-reporter","--no-first-run","--no-default-browser-check","--disable-sync","--metrics-recording-only"]

def _terminate_tree(pid: int) -> None:
    """终止 Chrome 进程树。Chrome 是多进程架构，主进程退出后 renderer/GPU/utility
    子进程可能仍存活并持有 profile 与截图句柄（Windows 下句柄延迟释放是垃圾文件根源），
    显式杀树可让临时目录与半成品截图能被干净删除。"""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, timeout=10)
        else:
            subprocess.run(["pkill", "-P", str(pid)], capture_output=True, timeout=10)
    except Exception:
        pass

def _clean_profile(profile: str) -> None:
    """删除临时 profile。主进程退出后子进程会延迟释放文件句柄，Windows 下被占用文件无法删除，
    故重试；最终仍失败时打 stderr 警告而非静默忽略，便于发现与定期清理残留。"""
    for _ in range(20):
        try:
            shutil.rmtree(profile)
            return
        except PermissionError:
            time.sleep(0.5)
    try:
        shutil.rmtree(profile)
    except Exception as e:
        print(f"警告: 临时 profile 未能删除，已残留（可手工清理）: {profile} ({e})", file=sys.stderr)

def _render(html_path, png_path, browser, width, height, timeout):
    profile=tempfile.mkdtemp(prefix="review-poster-profile-")
    proc=None
    try:
        command=[browser,"--headless=new","--disable-gpu","--hide-scrollbars","--allow-file-access-from-files","--force-device-scale-factor=1","--run-all-compositor-stages-before-draw",*_EXTRA_ARGS,f"--user-data-dir={profile}",f"--window-size={width},{height}",f"--screenshot={png_path}",html_path.as_uri()]
        proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _terminate_tree(proc.pid)
            try: proc.kill()
            except Exception: pass
            proc.communicate()
            if png_path.exists():
                try: png_path.unlink()
                except OSError: pass
            raise RuntimeError(f"browser render timed out after {timeout}s; 已清理残留子进程与半成品截图")
        return proc
    finally:
        if proc is not None and proc.poll() is None:
            _terminate_tree(proc.pid)
            try: proc.kill()
            except Exception: pass
        _clean_profile(profile)

_PROBE_BG = {"light": "#ffffff", "dark": "#000000"}

def _probe_style(bg: str) -> str:
    return (
        '<style id="probe-override">'
        'html{height:auto!important;overflow:visible!important}'
        f'body{{height:auto!important;overflow:visible!important;background:{bg} none!important}}'
        '</style>'
    )

def _probe_html(html_text: str, bg: str) -> str:
    """注入探针样式：纯色底、解除 2000px 裁切，使内容自然高度可被量出。
    bg='light' 配深色文字海报（白底扫暗像素）；bg='dark' 配浅色文字海报（黑底扫亮像素）。"""
    style = _probe_style(_PROBE_BG[bg])
    if "</head>" in html_text:
        return html_text.replace("</head>", style + "</head>", 1)
    return style + html_text

def _ink_bbox(png_path: Path, threshold: int, bg: str):
    """返回内容像素包围盒 (left, upper, right, lower)；无内容返回 None。
    浅底扫暗于 255-threshold 的像素；深底扫亮于 threshold 反向的像素（对称口径）。"""
    from PIL import Image
    if bg == "dark":
        fn = lambda v: 255 if v > 255 - threshold else 0
    else:
        fn = lambda v: 255 if v < threshold else 0
    with Image.open(png_path) as image:
        gray = image.convert("L").point(fn)
        return gray.getbbox()

def run_probe(a) -> int:
    html_path = a.html.resolve()
    if not html_path.is_file(): raise FileNotFoundError(html_path)
    height = a.probe_height
    bg = a.probe_bg
    browser = str(a.browser.resolve()) if a.browser else (candidates()[0] if candidates() else "")
    if not browser or not Path(browser).is_file(): raise RuntimeError("No Chrome/Chromium/Edge found. Set CHROME_PATH or pass --browser.")
    with tempfile.TemporaryDirectory(prefix="review-poster-probe-") as tmp:
        tmpdir = Path(tmp)
        staged = tmpdir / "probe.html"
        staged.write_text(_probe_html(html_path.read_text(encoding="utf-8"), bg), encoding="utf-8", newline="\n")
        # 底图相对路径在临时目录失效，从原 HTML 所在目录复制进来
        for asset in html_path.parent.glob("*.png"):
            shutil.copy2(asset, tmpdir / asset.name)
        shot = tmpdir / "probe.png"
        result = _render(staged, shot, browser, WIDTH, height, a.timeout)
        if result.returncode != 0 or not shot.is_file():
            raise RuntimeError(f"probe render failed ({result.returncode})\n{result.stdout}\n{result.stderr}")
        box = _ink_bbox(shot, PROBE_INK_THRESHOLD, bg)
    if box is None:
        print("probe: 未检测到任何内容像素（纯底色）"); return 0
    left, upper, right, lower = box
    margin = HEIGHT - int(lower)
    print(f"probe: 底色调 {bg} | 内容包围盒 x[{left},{right}] y[{upper},{lower}] | 画布 {WIDTH}x{HEIGHT}")
    print(f"probe: lowest non-bg y: {lower} | 底部余量 (canvas - lowest): {margin}")
    print(f"probe: {'PASS' if margin >= 0 else 'FAIL'} | 目标 ≥0（建议留 20-40px 视觉留白）")
    return 0 if margin >= 0 else 1

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("html",type=Path); p.add_argument("png",type=Path); p.add_argument("--browser",type=Path); p.add_argument("--force",action="store_true"); p.add_argument("--timeout",type=int,default=60)
    p.add_argument("--probe",action="store_true",help="内容高度探针模式：纯色底 + 解除裁切，在 %dpx 高画布渲染并报告最底内容像素" % PROBE_HEIGHT)
    p.add_argument("--probe-height",type=int,default=PROBE_HEIGHT)
    p.add_argument("--probe-bg",choices=["light","dark"],default="light",help="探针底色调：light=深色文字海报（白底）；dark=浅色文字海报（黑底，配星云等深底画布）")
    a=p.parse_args()
    if a.probe: return run_probe(a)
    html_path=a.html.resolve(); png_path=a.png.resolve()
    if not html_path.is_file(): raise FileNotFoundError(html_path)
    if png_path.exists() and not a.force: raise FileExistsError(f"refusing to overwrite {png_path}; use --force deliberately")
    png_path.parent.mkdir(parents=True,exist_ok=True)
    browser=str(a.browser.resolve()) if a.browser else (candidates()[0] if candidates() else "")
    if not browser or not Path(browser).is_file(): raise RuntimeError("No Chrome/Chromium/Edge found. Set CHROME_PATH or pass --browser.")
    result=_render(html_path,png_path,browser,WIDTH,HEIGHT,a.timeout)
    if result.returncode!=0:
        if png_path.exists():
            try: png_path.unlink()
            except OSError: pass
        raise RuntimeError(f"browser render failed ({result.returncode})\n{result.stdout}\n{result.stderr}")
    if not png_path.is_file(): raise RuntimeError(f"browser did not create {png_path}")
    size=dimensions(png_path)
    if size!=(WIDTH,HEIGHT): raise RuntimeError(f"expected {WIDTH}x{HEIGHT}, got {size[0]}x{size[1]}")
    print(f"{png_path} {size[0]}x{size[1]}"); return 0
if __name__=="__main__": raise SystemExit(main())
