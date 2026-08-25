﻿@echo off
chcp 65001 >nul
title Antigravity 中文汉化管理面板 (Elite Toolkit)
echo ============================================================
echo      Antigravity 中文汉化管理面板 (Elite Toolkit)
echo ============================================================
echo.
echo 正在启动汉化管理器，请稍候...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0patch_antigravity.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 执行过程中发生错误，请按任意键退出...
    pause >nul
)