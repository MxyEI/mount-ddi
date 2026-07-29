@echo off
REM ============================================================
REM  一键把 mount-ddi 打包成独立的 Windows exe(目标机免装 Python)。
REM  双击本文件即可。产物:dist\mount-ddi.exe
REM  需要:本机装有 Python 3(python.org,勾 Add to PATH)+ 联网。
REM  可选:build-windows.bat --upgrade-deps 强制更新打包依赖。
REM ============================================================
setlocal enabledelayedexpansion
chcp 65001 >nul
cd /d "%~dp0"

set "UPGRADE_DEPS="
if /i "%~1"=="--upgrade-deps" set "UPGRADE_DEPS=1"

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

REM --- 3. 首次安装依赖;后续直接复用 .build-venv ---
set "NEED_DEPS="
"%VPY%" -c "import PyInstaller, pymobiledevice3" >nul 2>nul || set "NEED_DEPS=1"
"%VPY%" -m pip check >nul 2>nul || set "NEED_DEPS=1"
if defined UPGRADE_DEPS set "NEED_DEPS=1"

if not defined NEED_DEPS (
  echo [*] 打包依赖已安装,直接复用 %VENV% ^(不会重复下载^)。
  goto deps_ready
)

echo [*] 正在探测国内 PyPI 镜像...
set "PIP_UPGRADE="
if defined UPGRADE_DEPS set "PIP_UPGRADE=--upgrade"
set "DEPS_OK="
set "PYPI_INDEX=%MOUNT_DDI_PYPI_INDEX%"
if defined PYPI_INDEX (
  echo [*] 先尝试环境变量指定的镜像: !PYPI_INDEX!
  "%VPY%" -m pip install --disable-pip-version-check --prefer-binary --timeout 30 --retries 2 --index-url "!PYPI_INDEX!" !PIP_UPGRADE! pyinstaller pymobiledevice3
  if not errorlevel 1 set "DEPS_OK=1"
)

if not defined DEPS_OK (
  for /f "usebackq delims=" %%I in (`"%VPY%" "%~dp0select-pypi-mirror.py"`) do (
    if not defined DEPS_OK (
      echo [*] 尝试 PyPI 源: %%I
      "%VPY%" -m pip install --disable-pip-version-check --prefer-binary --timeout 30 --retries 2 --index-url "%%I" !PIP_UPGRADE! pyinstaller pymobiledevice3
      if not errorlevel 1 (
        set "DEPS_OK=1"
        set "PYPI_INDEX=%%I"
      ) else (
        echo [!] 当前源安装失败,自动切换下一个源...
      )
    )
  )
)
if not defined DEPS_OK ( echo [!] 所有 PyPI 源均安装失败,请检查网络 & pause & exit /b 1 )
echo [OK] 依赖安装完成,使用源: !PYPI_INDEX!

:deps_ready

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
