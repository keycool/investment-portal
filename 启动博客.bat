@echo off
setlocal enabledelayedexpansion
chcp 936 >nul 2>&1
title 心猿意马的羊 - 本地博客服务

rem ============================================================
rem  心猿意马的羊 | 交易复盘 博客  --  本地一键启动
rem  双击本文件即可。脚本会自动：找 Node、补依赖、清缓存、起服务。
rem  只想检查环境、不启动服务：在本文件夹空白处 Shift+右键 ->
rem  在此处打开 PowerShell，输入： .\启动博客.bat check
rem ============================================================

set "PROJECT=D:\CC\shared\investment-portal"
set "PORT_BASE=4321"

echo.
echo ============================================================
echo    心猿意马的羊  ^|  交易复盘   本地启动
echo ============================================================
echo.

rem ---------- 1/6 项目目录 ----------
if not exist "%PROJECT%\package.json" (
  echo [X] 找不到项目：%PROJECT%
  echo     请确认 D 盘项目目录完整，或修改本文件开头的 PROJECT 变量。
  echo.
  pause
  exit /b 1
)
echo [1/6] 项目目录 : %PROJECT%

rem ---------- 2/6 找 Node（三路回退） ----------
set "NODE_DIR="
set "NODE_FROM="

rem 2a. 系统 PATH 上的 node（自己装的 Node 走这里）
for /f "delims=" %%N in ('where node 2^>nul') do (
  if not defined NODE_DIR (
    if exist "%%~dpNnpm.cmd" (
      set "TMPD=%%~dpN"
      set "TMPD=!TMPD:~0,-1!"
      set "NODE_DIR=!TMPD!"
      set "NODE_FROM=系统 PATH"
    )
  )
)

rem 2b. WorkBuddy 托管 node（版本目录名随更新变化，用通配扫描）
if not defined NODE_DIR (
  for /d %%D in ("%USERPROFILE%\.workbuddy\binaries\node\versions\*") do (
    if not defined NODE_DIR (
      if exist "%%~fD\node.exe" (
        if exist "%%~fD\npm.cmd" (
          set "NODE_DIR=%%~fD"
          set "NODE_FROM=WorkBuddy 托管"
        )
      )
    )
  )
)

rem 2c. 常见安装位置兜底
if not defined NODE_DIR (
  for %%P in (
    "C:\Program Files\nodejs"
    "C:\Program Files (x86)\nodejs"
    "%LOCALAPPDATA%\Programs\nodejs"
  ) do (
    if not defined NODE_DIR (
      if exist "%%~P\node.exe" (
        if exist "%%~P\npm.cmd" (
          set "NODE_DIR=%%~P"
          set "NODE_FROM=常见安装位置"
        )
      )
    )
  )
)

if not defined NODE_DIR (
  echo [X] 本机没有找到 Node.js。
  echo.
  echo     请先安装，任选一种：
  echo       1^) 打开 https://nodejs.org 下载 LTS 版安装
  echo       2^) 命令行执行： winget install OpenJS.NodeJS.LTS
  echo     装完再双击本文件即可。
  echo.
  pause
  exit /b 1
)

set "NODE_VER="
for /f "delims=" %%V in ('"%NODE_DIR%\node.exe" -v 2^>nul') do set "NODE_VER=%%V"
if not defined NODE_VER set "NODE_VER=v0.0.0"
set "MAJ="
for /f "tokens=1 delims=." %%A in ("%NODE_VER%") do set "MAJ=%%A"
set "MAJ=%MAJ:v=%"
if "%MAJ%"=="" set "MAJ=0"

echo [2/6] Node.js  : %NODE_DIR%
echo        版本 %NODE_VER%   ^(来源：!NODE_FROM!^)
if %MAJ% LSS 18 (
  echo        警告：版本偏低。本项目需要 Node 18.20.8+ / 20.3+ / 22+，
  echo              否则可能启动失败，建议装 LTS 版。
)

rem ---------- 3/6 依赖 ----------
if not exist "%PROJECT%\node_modules\astro" (
  echo [3/6] 依赖缺失，正在安装（首次需要几分钟，请勿关闭窗口）...
  pushd "%PROJECT%"
  call "%NODE_DIR%\npm.cmd" install
  if errorlevel 1 (
    echo [X] 依赖安装失败，请检查网络后重试。
    popd
    echo.
    pause
    exit /b 1
  )
  popd
  echo        依赖安装完成。
) else (
  echo [3/6] 依赖     : 已就绪
)

rem ---------- 4/6 清缓存（避免上次异常退出的残留） ----------
if exist "%PROJECT%\.astro\dev.json" del /q "%PROJECT%\.astro\dev.json" >nul 2>&1
if exist "%PROJECT%\node_modules\.vite" rmdir /s /q "%PROJECT%\node_modules\.vite" >nul 2>&1
echo [4/6] 缓存     : 已清理

rem ---------- 5/6 找一个空闲端口 ----------
rem 说明：先把 LISTENING 端口清单落盘，再逐个端口查文件。
rem 这样是为了避开「在嵌套括号块里写管道」的 cmd 转义坑（会被当成普通参数传给 netstat）。
set "SCANFILE=%TEMP%\blog-port-scan.tmp"
netstat -ano | findstr LISTENING > "%SCANFILE%" 2>nul
set "PORT="
for /l %%P in (%PORT_BASE%,1,4335) do (
  if not defined PORT (
    findstr /c:":%%P " "%SCANFILE%" >nul 2>&1
    if errorlevel 1 set "PORT=%%P"
  )
)
del /q "%SCANFILE%" >nul 2>&1
if not defined PORT set "PORT=%PORT_BASE%"
echo [5/6] 端口     : %PORT%
if not "%PORT%"=="%PORT_BASE%" echo        ^(%PORT_BASE% 已被占用，自动改用 %PORT%^)

rem ---------- 6/6 打印访问地址 ----------
set "LANIP="
for /f "tokens=2 delims=:" %%I in ('ipconfig ^| findstr IPv4') do (
  if not defined LANIP (
    set "RAW=%%I"
    set "RAW=!RAW: =!"
    set "LANIP=!RAW!"
  )
)

echo [6/6] 访问地址 :
echo.
echo        本机   : http://localhost:%PORT%/
if defined LANIP echo        局域网 : http://!LANIP!:%PORT%/    ^(同一个 WiFi 下的平板 / 手机^)
echo.
echo ------------------------------------------------------------
echo   启动后请保持本窗口开着。关窗口或按 Ctrl+C 即停止服务。
echo   改了 md 内容后，网页会自动刷新。
echo ------------------------------------------------------------
echo.

if /i "%~1"=="check" (
  echo [自检模式] 环境检查通过，没有真正启动服务。
  echo            直接双击本文件（不带参数）即可启动。
  echo.
  pause
  exit /b 0
)

cd /d "%PROJECT%"
rem 关掉 npm / Astro / Vite 的 ANSI 颜色码：GBK 控制台不认 VT 转义，会显示成一串乱码
set "NO_COLOR=1"
set "FORCE_COLOR=0"
echo 正在启动 Astro 开发服务器...
echo.
call "%NODE_DIR%\npm.cmd" run dev -- --host 0.0.0.0 --port %PORT%
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo 服务已停止。可以关闭本窗口。
) else (
  echo 服务已停止，返回码 %RC%
  echo 如果启动过程中报错，先试试把下面这个文件夹整个删掉，再双击本文件重跑：
  echo   %PROJECT%\node_modules
)
echo.
pause
