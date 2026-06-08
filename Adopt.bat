@echo off
cd /d "%~dp0"
cls
echo.
echo   The Node
echo   --------
echo.
echo   Bringing yours to life on this computer.
echo   The browser will open. Follow what you see.
echo.
if not exist ".venv\Scripts\python.exe" (
  echo   First time — installing (one minute)...
  call setup.bat
) else (
  call try.bat
)
echo.
echo   Your node is on this machine now.
echo.
pause
