@echo off
chcp 65001 >nul
title Antigravity 中文汉化管理面板 (Elite Toolkit v3.0)

:MENU
cls
echo ======================================================================
echo           Antigravity 中文汉化管理面板 (Elite Toolkit v3.0)
echo           永久自愈 · 零依赖原生注入 · 跨版本无损热补丁
echo ======================================================================
echo.
echo   [1] 一键安装 / 更新汉化补丁 (In-place Hot Patch)
echo   [2] 运行环境与健康状态诊断 (Health Diagnostics)
echo   [3] 开启 / 关闭后台自动守护 (Toggle Auto-Heal Daemon)
echo   [4] 一键恢复官方原版备份 (One-Click Rollback)
echo   [5] 退出 (Exit)
echo.
echo ======================================================================
set /p choice=请输入选项 [1-5]: 

if "%choice%"=="1" goto OPTION_1
if "%choice%"=="2" goto OPTION_2
if "%choice%"=="3" goto OPTION_3
if "%choice%"=="4" goto OPTION_4
if "%choice%"=="5" goto OPTION_5
if "%choice%"=="" goto MENU

echo.
echo 无效选项，请重新输入 [1-5]...
timeout /t 2 >nul
goto MENU

:OPTION_1
cls
echo ======================================================================
echo           [1] 一键安装 / 更新汉化补丁 (In-place Hot Patch)
echo ======================================================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0patch_antigravity.ps1" -Install
echo.
echo 操作完成，按任意键返回主菜单...
pause >nul
goto MENU

:OPTION_2
cls
echo ======================================================================
echo           [2] 运行环境与健康状态诊断 (Health Diagnostics)
echo ======================================================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" -Check
echo.
echo 诊断完成，按任意键返回主菜单...
pause >nul
goto MENU

:OPTION_3
cls
echo ======================================================================
echo           [3] 开启 / 关闭后台自动守护 (Toggle Auto-Heal Daemon)
echo ======================================================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $st = & '%~dp0install.ps1' -Daemon status; Write-Host ''; if ($st) { Write-Host '当前守护状态: [已开启 (ENABLED)]' -ForegroundColor Green; $ans = Read-Host '是否需要关闭后台自动守护? (y/n)'; if ($ans -match '^[yY]') { & '%~dp0install.ps1' -Daemon disable } } else { Write-Host '当前守护状态: [未开启 (DISABLED)]' -ForegroundColor Yellow; $ans = Read-Host '是否开启后台自动守护? (y/n)'; if ($ans -match '^[yY]' -or $ans -eq '') { & '%~dp0install.ps1' -Daemon enable } } }"
echo.
echo 操作完成，按任意键返回主菜单...
pause >nul
goto MENU

:OPTION_4
cls
echo ======================================================================
echo           [4] 一键恢复官方原版备份 (One-Click Rollback)
echo ======================================================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" -Restore
echo.
echo 操作完成，按任意键返回主菜单...
pause >nul
goto MENU

:OPTION_5
cls
echo 感谢使用 Antigravity 中文汉化补丁！祝您使用愉快！
timeout /t 1 >nul
exit /b 0