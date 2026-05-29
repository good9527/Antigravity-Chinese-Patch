# patch_antigravity.ps1
# A generic script to patch Antigravity client with Chinese translation.
# Works for any Windows user without hardcoded paths.

$ErrorActionPreference = "Stop"

# 1. Resolve dynamic paths
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

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "     Antigravity Chinese Patch Script      " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Script Directory: $scriptDir"
Write-Host "Antigravity Path: $programDir"

# 2. Check if Antigravity is installed
if (-not (Test-Path $originalAsar)) {
    Write-Error "Error: Antigravity installation not found at '$programDir'."
}

# 3. Terminate running Antigravity processes
Write-Host "Closing Antigravity client..." -ForegroundColor Yellow
$processes = Get-Process -Name "Antigravity" -ErrorAction SilentlyContinue
if ($processes) {
    Stop-Process -Name "Antigravity" -Force
    Start-Sleep -Seconds 2
}

# 4. Create/Sync Backup of original app.asar
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

# 5. Apply Patch
# Method A: Dynamic Patching (if local preload.js exists and Node is installed)
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
                # Load original preload.js
                $originalPreloadContent = Get-Content -Path $targetPreload -Raw
                
                # Load local patch preload.js
                $localContent = Get-Content -Path $localPreloadJs -Raw
                
                # Extract patch IIFE
                $patchMarker = "// Antigravity Chinese Localization Patch"
                $markerIndex = $localContent.IndexOf($patchMarker)
                if ($markerIndex -ge 0) {
                    $patchCode = $localContent.Substring($markerIndex)
                    
                    # Append patch code
                    $newPreloadContent = $originalPreloadContent + "`r`n`r`n" + $patchCode
                    Set-Content -Path $targetPreload -Value $newPreloadContent -Force
                    Write-Host "Successfully injected patch code into original preload.js!" -ForegroundColor Green
                } else {
                    Write-Warning "Could not find patch marker in local preload.js. Falling back to direct replacement."
                    Copy-Item $localPreloadJs $targetPreload -Force
                }
            } else {
                Copy-Item $localPreloadJs $targetPreload -Force
            }
            
            Write-Host "Repacking app.asar..." -ForegroundColor Gray
            & npx --yes asar pack $asarTemp $originalAsar
            
            # Clean temp
            if (Test-Path $asarTemp) { Remove-Item -Recurse -Force $asarTemp -ErrorAction SilentlyContinue }
            
            Write-Host "Dynamic injection applied successfully!" -ForegroundColor Green
            $patchedSuccessfully = $true
        } catch {
            Write-Warning "Dynamic injection failed. Falling back to direct replacement..."
        }
    }
}

# Method B: Direct Replacement (Fallback or if precompiled app.asar exists)
if (-not $patchedSuccessfully) {
    if (Test-Path $localPatchedAsar) {
        Write-Host "Applying patch via direct app.asar replacement..." -ForegroundColor Green
        Copy-Item $localPatchedAsar $originalAsar -Force
        $patchedSuccessfully = $true
    } else {
        Write-Error "Error: No pre-compiled 'app.asar' or 'dist/preload.js' found in the script directory."
    }
}

# 6. Restart Antigravity
if ($patchedSuccessfully) {
    Write-Host "Patch applied! Restarting Antigravity..." -ForegroundColor Green
    $exePath = Join-Path $programDir "Antigravity.exe"
    if (Test-Path $exePath) {
        Start-Process $exePath
    } else {
        Write-Warning "Antigravity.exe not found. Please start it manually."
    }
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "     Patch successfully applied!           " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
