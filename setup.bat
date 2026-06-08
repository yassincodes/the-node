@echo off
cd /d "%~dp0"
echo.
echo   Setting up your node...
echo.
python --version >nul 2>&1
if errorlevel 1 (
  echo   Python is required. Install from https://www.python.org/downloads/
  echo   Check "Add Python to PATH" during install, then run Adopt again.
  pause
  exit /b 1
)
if not exist ".venv" python -m venv .venv
.venv\Scripts\pip install -q -r requirements.txt
.venv\Scripts\python main.py activate
echo.
echo   Done. Run Adopt again anytime.
pause
