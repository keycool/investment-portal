#!/usr/bin/env python3
"""Render an HTML poster with a Chromium-family browser and verify pixel size.

通用渲染脚本：支持任意 --width/--height（引流版 1080×1440、复盘海报 1080×2000）。
"""
from __future__ import annotations
import argparse, os, shutil, struct, subprocess, sys, tempfile, time
from pathlib import Path

def candidates():
    values = []
    if os.environ.get("CHROME_PATH"):
        values.append(os.environ["CHROME_PATH"])
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            values.append(found)
    if sys.platform == "win32":
        values += [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                   r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
    elif sys.platform == "darwin":
        values += ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                   "/Applications/Chromium.app/Contents/MacOS/Chromium"]
    result = []
    for value in values:
        path = str(Path(value).expanduser())
        if Path(path).is_file() and path not in result:
            result.append(path)
    return result

def dimensions(path):
    with path.open("rb") as f:
        header = f.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"not a valid PNG: {path}")
    return struct.unpack(">II", header[16:24])

# 减少 Chrome 残留子进程（GPU/crashpad/后台网络），降低 profile 文件句柄占用，让临时目录能被干净删除
_EXTRA_ARGS = ["--disable-background-networking", "--disable-component-update",
               "--disable-crash-reporter", "--no-first-run", "--no-default-browser-check",
               "--disable-sync", "--metrics-recording-only"]

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
    profile = tempfile.mkdtemp(prefix="review-poster-profile-")
    proc = None
    try:
        command = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                   "--allow-file-access-from-files", "--force-device-scale-factor=1",
                   "--run-all-compositor-stages-before-draw", *_EXTRA_ARGS,
                   f"--user-data-dir={profile}", f"--window-size={width},{height}",
                   f"--screenshot={png_path}", html_path.as_uri()]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _terminate_tree(proc.pid)
            try:
                proc.kill()
            except Exception:
                pass
            proc.communicate()
            if png_path.exists():
                try:
                    png_path.unlink()
                except OSError:
                    pass
            raise RuntimeError(f"browser render timed out after {timeout}s; 已清理残留子进程与半成品截图")
        return proc
    finally:
        if proc is not None and proc.poll() is None:
            _terminate_tree(proc.pid)
            try:
                proc.kill()
            except Exception:
                pass
        _clean_profile(profile)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("html", type=Path)
    p.add_argument("png", type=Path)
    p.add_argument("--width", type=int, default=1080)
    p.add_argument("--height", type=int, default=2000)
    p.add_argument("--browser", type=Path)
    p.add_argument("--force", action="store_true")
    p.add_argument("--timeout", type=int, default=60)
    a = p.parse_args()

    html_path = a.html.resolve()
    png_path = a.png.resolve()
    if not html_path.is_file():
        raise FileNotFoundError(html_path)
    if png_path.exists() and not a.force:
        raise FileExistsError(f"refusing to overwrite {png_path}; use --force deliberately")
    png_path.parent.mkdir(parents=True, exist_ok=True)

    browser = str(a.browser.resolve()) if a.browser else (candidates()[0] if candidates() else "")
    if not browser or not Path(browser).is_file():
        raise RuntimeError("No Chrome/Chromium/Edge found. Set CHROME_PATH or pass --browser.")

    result = _render(html_path, png_path, browser, a.width, a.height, a.timeout)
    if result.returncode != 0:
        if png_path.exists():
            try:
                png_path.unlink()
            except OSError:
                pass
        raise RuntimeError(f"browser render failed ({result.returncode})\n{result.stdout}\n{result.stderr}")
    if not png_path.is_file():
        raise RuntimeError(f"browser did not create {png_path}")
    size = dimensions(png_path)
    if size != (a.width, a.height):
        raise RuntimeError(f"expected {a.width}x{a.height}, got {size[0]}x{size[1]}")
    print(f"{png_path} {size[0]}x{size[1]}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
