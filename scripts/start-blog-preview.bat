@echo off
setlocal
cd /d "D:\CC\shared\investment-portal"
set LOG=scripts\preview-build.log
echo [%date% %time%] build start >> "%LOG%"
call npm run build:preview >> "%LOG%" 2>&1
echo [%date% %time%] build done code %errorlevel% >> "%LOG%"
netstat -ano | findstr ":4321 " >nul
if %errorlevel%==0 (
  echo [%date% %time%] server already on 4321, skip >> "%LOG%"
) else (
  echo [%date% %time%] starting http.server 4321 >> "%LOG%"
  start "" /b python -m http.server 4321 --bind 127.0.0.1 --directory "D:\CC\shared\investment-portal\dist-preview" >> "%LOG%" 2>&1
)
endlocal
