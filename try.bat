@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo   Run Adopt first.
  pause
  exit /b 1
)
.venv\Scripts\python tools\try.py
pause
