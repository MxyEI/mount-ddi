@echo off
REM 一键挂载 DDI(Windows)。双击运行,或命令行 mount-ddi.bat
REM 需要 Python 3(python.org 装,勾选 Add to PATH)。首次会自动 pip 安装 pymobiledevice3。
setlocal
where python >nul 2>nul
if %errorlevel%==0 (
  python "%~dp0mount-ddi.py" %*
) else (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 "%~dp0mount-ddi.py" %*
  ) else (
    echo [!] 没找到 Python。请到 https://www.python.org/downloads/ 安装 Python 3
    echo     安装时务必勾选 "Add Python to PATH"。
  )
)
echo.
pause
