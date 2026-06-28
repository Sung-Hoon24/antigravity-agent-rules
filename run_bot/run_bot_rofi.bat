@echo off
chcp 65001 >nul
title Rofi Bot Launcher
cd /d "%~dp0"
echo [Rofi] Lofi Bot - @Taipei_Lofi_New_Bot start...
echo [INFO] This bot runs independently. Other bots will not be affected.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_bot.ps1" rofi
pause
