@echo off
chcp 65001 >nul
title Aura Bot Launcher
cd /d "%~dp0"
echo [Aura] Wellness Bot - @rubia_smart_bot start...
echo [INFO] This bot runs independently. Other bots will not be affected.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_bot.ps1" aura
pause
