@echo off
title ADAS Mobile Web Server
cd /d "%~dp0"
echo ============================================================
echo ADAS Mobile Server Starting...
echo ============================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server.ps1"
pause
