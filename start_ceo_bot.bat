@echo off
setlocal
echo.
echo =============================================
echo   Factory A - START CEO Bot Supervisor
echo =============================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\ceo_bot_runtime.ps1"

echo.
pause
