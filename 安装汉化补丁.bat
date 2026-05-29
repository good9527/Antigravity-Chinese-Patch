@echo off
title Antigravity Chinese Patch Installer
echo ============================================================
echo      Antigravity Chinese Patch Installer (中文汉化工具)
echo ============================================================
echo.
echo Running installer via PowerShell. Please wait...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0patch_antigravity.ps1"
echo.
echo ------------------------------------------------------------
echo Done! Press any key to exit...
pause >nul
