@echo off
setlocal
echo.
echo =============================================
echo   Factory A - RESTART CEO Bot
echo =============================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\ceo_bot_restart.ps1"

echo.
pause
