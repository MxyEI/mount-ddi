@echo off
REM ============================================================
REM  一键把 mount-ddi 打包成独立的 Windows exe(目标机免装 Python)。
REM  双击本文件即可。产物:dist\mount-ddi.exe
REM  需要:本机装有 Python 3(python.org,勾 Add to PATH)+ 联网。
REM ============================================================
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

echo ==== 打包 mount-ddi.exe ====
echo.

REM --- 1. 找 Python ---
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (
  where py >nul 2>nul && set "PY=py -3"
)
if not defined PY (
  echo [!] 没找到 Python。请安装 Python 3,并勾选 "Add Python to PATH":
  echo     https://www.python.org/downloads/
  pause & exit /b 1
)
echo [*] 使用 Python: %PY%

REM --- 2. 建打包用虚拟环境(和 .venv 隔离,避免污染)---
set "VENV=.build-venv"
if not exist "%VENV%\Scripts\python.exe" (
  echo [*] 创建虚拟环境 %VENV% ...
  %PY% -m venv "%VENV%" || ( echo [!] venv 创建失败 & pause & exit /b 1 )
)
set "VPY=%VENV%\Scripts\python.exe"

REM --- 3. 装依赖:pyinstaller + pymobiledevice3 ---
echo [*] 安装/更新依赖(pyinstaller + pymobiledevice3)...
"%VPY%" -m pip install -U pip >nul 2>nul
"%VPY%" -m pip install -U pyinstaller pymobiledevice3 || ( echo [!] 依赖安装失败,检查网络 & pause & exit /b 1 )

REM --- 4. 清理旧产物 ---
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"

REM --- 5. 打包(用 mount-ddi.spec)---
echo [*] 开始打包,过程较慢请耐心等待...
"%VPY%" -m PyInstaller --noconfirm --clean mount-ddi.spec || ( echo [!] 打包失败 & pause & exit /b 1 )

echo.
if exist "dist\mount-ddi.exe" (
  echo [OK] 打包完成!
  echo      产物:  %CD%\dist\mount-ddi.exe
  echo      拷到目标机双击即可,无需安装 Python。
) else (
  echo [!] 没生成 exe,请翻上面的日志排查。
)
echo.
pause
