@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
python setup_form.py
if errorlevel 1 (
  echo.
  echo [ERROR] setup failed. Make sure python is installed and in PATH.
)
echo.
pause
