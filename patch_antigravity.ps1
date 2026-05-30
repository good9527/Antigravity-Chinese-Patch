# patch_antigravity.ps1
# A premium, interactive, generic script to patch/manage Antigravity client localization.
# Features a beautiful selection menu, backups manager, status check, and dynamic injection.

$ErrorActionPreference = "Stop"

# Define dynamic paths
$programDir = "$env:LOCALAPPDATA\Programs\antigravity"
$resourcesDir = "$programDir\resources"
$originalAsar = "$resourcesDir\app.asar"
$backupAsar = "$resourcesDir\app.asar.bak"

# Resolve script directory dynamically
$scriptDir = $PSScriptRoot
if (-not $scriptDir) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
if (-not $scriptDir) {
    $scriptDir = Get-Location
}

$localPreloadJs = Join-Path $scriptDir "dist\preload.js"
$localPatchedAsar = Join-Path $scriptDir "app.asar"

Function Stop-Client {
    Write-Host "Closing Antigravity client..." -ForegroundColor Yellow
    $processes = Get-Process -Name "Antigravity" -ErrorAction SilentlyContinue
    if ($processes) {
        Stop-Process -Name "Antigravity" -Force
        Start-Sleep -Seconds 2
    }
}

Function Start-Client {
    $exePath = Join-Path $programDir "Antigravity.exe"
    if (Test-Path $exePath) {
        Write-Host "Restarting Antigravity client..." -ForegroundColor Green
        # Use cmd /c start to completely detach the process so it won't close when PowerShell is closed
        Start-Process "cmd.exe" -ArgumentList "/c start `"`" `"$exePath`"" -WindowStyle Hidden
    } else {
        Write-Warning "Antigravity.exe not found. Please start it manually."
    }
}

Function Show-Menu {
    Clear-Host
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "     Antigravity Chinese Patch Elite Toolkit v2.0         " -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  1. 🚀 Install/Update Chinese Patch (一键极速汉化/更新) " -ForegroundColor Green
    Write-Host "  2. 🛡️ Restore Original Backup (一键恢复官方原装)" -ForegroundColor Yellow
    Write-Host "  3. 🔍 Check Status & Client Version (检查当前版本状态)" -ForegroundColor Blue
    Write-Host "  4. 🚪 Exit (退出)" -ForegroundColor Gray
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host ""
    $choice = Read-Host "Please select an option [1-4] (请输入选项 [1-4])"
    return $choice
}

Function Apply-Patch {
    Clear-Host
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "     Applying Chinese Localization Patch  " -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    if (-not (Test-Path $originalAsar)) {
        Write-Error "Error: Antigravity installation not found at '$programDir'."
        Read-Host "Press Enter to return to menu..."
        return
    }
    
    Stop-Client
    
    # Create/Sync Backup of original app.asar
    $patchedSuccessfully = $false
    $tempDir = Join-Path $env:TEMP "antigravity_asar_temp"
    if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

    $isCurrentPatched = $false
    $nodeCheck = Get-Command npx -ErrorAction SilentlyContinue
    if ($nodeCheck -and (Test-Path $originalAsar)) {
        try {
            $checkTemp = Join-Path $tempDir "check_extract"
            & npx --yes asar extract $originalAsar $checkTemp
            $checkPreload = Join-Path $checkTemp "dist\preload.js"
            if (Test-Path $checkPreload) {
                $preloadText = Get-Content -Path $checkPreload -Raw
                if ($preloadText -like "*Antigravity Chinese Localization Patch*") {
                    $isCurrentPatched = $true
                }
            }
            if (Test-Path $checkTemp) { Remove-Item -Recurse -Force $checkTemp -ErrorAction SilentlyContinue }
        } catch {
            # Fallback if check extraction fails
        }
    }

    if (-not $isCurrentPatched) {
        Write-Host "Fresh/unpatched Antigravity client detected. Updating backup..." -ForegroundColor Green
        Copy-Item $originalAsar $backupAsar -Force
    } else {
        Write-Host "Patched Antigravity client detected. Keeping existing backup." -ForegroundColor Yellow
    }

    # Apply Patch
    if (Test-Path $localPreloadJs) {
        if ($nodeCheck) {
            try {
                Write-Host "Node.js detected. Performing dynamic injection to keep your client updated..." -ForegroundColor Green
                $asarTemp = Join-Path $tempDir "asar_extracted"
                
                Write-Host "Extracting local app.asar..." -ForegroundColor Gray
                & npx --yes asar extract $backupAsar $asarTemp
                
                Write-Host "Injecting Chinese preload.js..." -ForegroundColor Gray
                $targetPreload = Join-Path $asarTemp "dist\preload.js"
                if (Test-Path $targetPreload) {
                    $originalPreloadContent = Get-Content -Path $targetPreload -Raw
                    $localContent = Get-Content -Path $localPreloadJs -Raw
                    $patchMarker = "// Antigravity Chinese Localization Patch"
                    $markerIndex = $localContent.IndexOf($patchMarker)
                    if ($markerIndex -ge 0) {
                        $patchCode = $localContent.Substring($markerIndex)
                        $newPreloadContent = $originalPreloadContent + "`r`n`r`n" + $patchCode
                        Set-Content -Path $targetPreload -Value $newPreloadContent -Force
                        Write-Host "Successfully injected patch code into original preload.js!" -ForegroundColor Green
                    } else {
                        Write-Warning "Could not find patch marker. Falling back to direct replacement."
                        Copy-Item $localPreloadJs $targetPreload -Force
                    }
                } else {
                    Copy-Item $localPreloadJs $targetPreload -Force
                }
                
                Write-Host "Repacking app.asar..." -ForegroundColor Gray
                & npx --yes asar pack $asarTemp $originalAsar
                
                if (Test-Path $asarTemp) { Remove-Item -Recurse -Force $asarTemp -ErrorAction SilentlyContinue }
                Write-Host "Dynamic injection applied successfully!" -ForegroundColor Green
                $patchedSuccessfully = $true
            } catch {
                Write-Warning "Dynamic injection failed. Falling back to direct replacement..."
            }
        }
    }

    if (-not $patchedSuccessfully) {
        if (Test-Path $localPatchedAsar) {
            Write-Host "Applying patch via direct app.asar replacement..." -ForegroundColor Green
            Copy-Item $localPatchedAsar $originalAsar -Force
            $patchedSuccessfully = $true
        } else {
            Write-Error "Error: No pre-compiled 'app.asar' or 'dist/preload.js' found."
            Read-Host "Press Enter to return to menu..."
            return
        }
    }
    
    if ($patchedSuccessfully) {
        Write-Host "Patch successfully applied!" -ForegroundColor Green
        Start-Client
    }
    
    Write-Host ""
    Read-Host "Press Enter to return to menu... (按回车返回主菜单...)"
}

Function Restore-Backup {
    Clear-Host
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "     Restoring Original Backup Client     " -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not (Test-Path $backupAsar)) {
        Write-Host "Error: No backup file 'app.asar.bak' found. Cannot restore." -ForegroundColor Red
        Write-Host ""
        Read-Host "Press Enter to return to menu... (按回车返回主菜单...)"
        return
    }
    
    Stop-Client
    
    try {
        Write-Host "Restoring original app.asar..." -ForegroundColor Green
        Copy-Item $backupAsar $originalAsar -Force
        Write-Host "Successfully restored original client!" -ForegroundColor Green
        Start-Client
    } catch {
        Write-Host "Error: Failed to restore backup file: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Read-Host "Press Enter to return to menu... (按回车返回主菜单...)"
}

Function Check-Status {
    Clear-Host
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "     Antigravity Client Status Inspector   " -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Program Directory: $programDir"
    
    if (Test-Path $originalAsar) {
        $size = (Get-Item $originalAsar).Length
        $sizeMB = [Math]::Round($size / 1MB, 2)
        Write-Host "Active app.asar Size: $sizeMB MB ($size Bytes)" -ForegroundColor Gray
        
        # Check if patched
        $isPatched = "Unpatched (原装未汉化)"
        $patchedColor = "Green"
        $nodeCheck = Get-Command npx -ErrorAction SilentlyContinue
        if ($nodeCheck) {
            try {
                $tempDir = Join-Path $env:TEMP "antigravity_inspect_temp"
                if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue }
                & npx --yes asar extract $originalAsar $tempDir
                $preloadPath = Join-Path $tempDir "dist\preload.js"
                $packagePath = Join-Path $tempDir "package.json"
                
                if (Test-Path $packagePath) {
                    $pkg = Get-Content $packagePath | ConvertFrom-Json
                    Write-Host "Client Version: $($pkg.version)" -ForegroundColor White
                }
                
                if (Test-Path $preloadPath) {
                    $preloadText = Get-Content -Path $preloadPath -Raw
                    if ($preloadText -like "*Antigravity Chinese Localization Patch*") {
                        $isPatched = "Patched (已汉化)"
                        $patchedColor = "Cyan"
                    }
                }
                if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue }
            } catch {
                $isPatched = "Unknown (Check failed)"
                $patchedColor = "Yellow"
            }
        }
        Write-Host "Patch Status: $isPatched" -ForegroundColor $patchedColor
    } else {
        Write-Host "Active app.asar: NOT FOUND (未找到)" -ForegroundColor Red
    }
    
    if (Test-Path $backupAsar) {
        $bSize = (Get-Item $backupAsar).Length
        $bSizeMB = [Math]::Round($bSize / 1MB, 2)
        Write-Host "Original Backup (app.asar.bak): EXISTS ($bSizeMB MB)" -ForegroundColor Green
    } else {
        Write-Host "Original Backup (app.asar.bak): NOT FOUND (无备份)" -ForegroundColor Yellow
    }
    
    $nodeCheck = Get-Command npx -ErrorAction SilentlyContinue
    if ($nodeCheck) {
        Write-Host "Node.js/npx Environment: Detected (已检测到)" -ForegroundColor Green
    } else {
        Write-Host "Node.js/npx Environment: NOT DETECTED (未安装)" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Read-Host "Press Enter to return to menu... (按回车返回主菜单...)"
}

# Main Loop
do {
    $choice = Show-Menu
    switch ($choice) {
        "1" { Apply-Patch }
        "2" { Restore-Backup }
        "3" { Check-Status }
        "4" { break }
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
} while ($choice -ne "4")

Clear-Host
Write-Host "Goodbye! Enjoy Antigravity Chinese Patch!" -ForegroundColor Green
