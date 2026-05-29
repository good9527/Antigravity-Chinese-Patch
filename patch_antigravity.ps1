# patch_antigravity.ps1
# Script to patch Antigravity client with Chinese translation

$ErrorActionPreference = "Stop"

# 1. Define paths
$programDir = "C:\Users\19901\AppData\Local\Programs\antigravity"
$resourcesDir = "$programDir\resources"
$originalAsar = "$resourcesDir\app.asar"
$backupAsar = "$resourcesDir\app.asar.bak"
$patchedAsar = "C:\Users\19901\Documents\antigravity\radiant-maxwell\app.asar"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "     Antigravity Chinese Patch Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 2. Check if patched asar exists
if (-not (Test-Path $patchedAsar)) {
    Write-Error "Error: Patched app.asar not found! Run from the correct directory."
}

# 3. Ask to close Antigravity
Write-Host "Closing Antigravity client..." -ForegroundColor Yellow
$processes = Get-Process -Name "Antigravity" -ErrorAction SilentlyContinue
if ($processes) {
    Stop-Process -Name "Antigravity" -Force
    Start-Sleep -Seconds 2
}

# 4. Backup original app.asar if not already backed up
if (-not (Test-Path $backupAsar)) {
    Write-Host "Backing up original app.asar to app.asar.bak..." -ForegroundColor Green
    Copy-Item $originalAsar $backupAsar -Force
} else {
    Write-Host "Backup app.asar.bak already exists. Skipping backup." -ForegroundColor Gray
}

# 5. Overwrite with patched app.asar
Write-Host "Applying Chinese patch..." -ForegroundColor Green
Copy-Item $patchedAsar $originalAsar -Force

# 6. Restart Antigravity
Write-Host "Patch applied! Restarting Antigravity..." -ForegroundColor Green
$exePath = "$programDir\Antigravity.exe"
if (Test-Path $exePath) {
    Start-Process $exePath
} else {
    Write-Warning "Antigravity.exe not found. Please start it manually."
}

# 7. Clean up temporary files in workspace
Write-Host "Cleaning up temporary files..." -ForegroundColor Gray
if (Test-Path $patchedAsar) {
    Remove-Item -Force $patchedAsar -ErrorAction SilentlyContinue
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "     Patch successfully applied!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
