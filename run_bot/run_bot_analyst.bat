@echo off
chcp 65001 >nul
title Analyst Bot Launcher
cd /d "%~dp0"
echo [Analyst] YouTube Analyst Bot - @Taipey_LofiBot start...
echo [INFO] This bot runs independently. Other bots will not be affected.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_bot.ps1" analyst
pause
