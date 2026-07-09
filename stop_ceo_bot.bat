@echo off
setlocal
echo.
echo =============================================
echo   Factory A - STOP CEO Bot
echo =============================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\ceo_bot_stop.ps1"

echo.
pause
