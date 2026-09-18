@echo off
REM One-click mount DDI on Windows. Double-click or run: mount-ddi.bat
REM Requires Python 3 from python.org with Add to PATH. First run auto-installs pymobiledevice3.
setlocal
where python >nul 2>nul
if %errorlevel%==0 (
  python "%~dp0mount-ddi.py" %*
) else (
  where py >nul 2>nul
  if %errorlevel%==0 (
    py -3 "%~dp0mount-ddi.py" %*
  ) else (
    echo [!] Python not found. Install Python 3 from https://www.python.org/downloads/
    echo     Check Add Python to PATH during setup.
  )
)
echo.
pause
