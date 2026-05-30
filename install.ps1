# install.ps1
# One-click Online Installer for Antigravity-Chinese-Patch
# Can be run via: iwr -useb https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$repoOwner = "good9527"
$repoName = "Antigravity-Chinese-Patch"
$rawBaseUrl = "https://raw.githubusercontent.com/$repoOwner/$repoName/main"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "     Antigravity Chinese Patch Web Installer              " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Resolve local AppData path
$programDir = "$env:LOCALAPPDATA\Programs\antigravity"
$resourcesDir = "$programDir\resources"
$originalAsar = "$resourcesDir\app.asar"
$backupAsar = "$resourcesDir\app.asar.bak"

if (-not (Test-Path $originalAsar)) {
    Write-Error "Error: Antigravity installation not found at '$programDir'. Please install the client first."
}

# 2. Terminate running Antigravity client
Write-Host "Closing Antigravity client..." -ForegroundColor Yellow
$processes = Get-Process -Name "Antigravity" -ErrorAction SilentlyContinue
if ($processes) {
    Stop-Process -Name "Antigravity" -Force
    Start-Sleep -Seconds 2
}

# 3. Create/Sync backup of original app.asar
$patchedSuccessfully = $false
$tempDir = Join-Path $env:TEMP "antigravity_web_patch"
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

# 4. Determine patch method
$downloadedPreload = Join-Path $tempDir "preload.js"
$timestamp = (Get-Date).Ticks

try {
    Write-Host "Downloading latest Chinese localization script from GitHub..." -ForegroundColor Green
    Invoke-RestMethod -Uri "$rawBaseUrl/dist/preload.js?t=$timestamp" -OutFile $downloadedPreload
    
    # Method A: Dynamic Local ASAR Injection (Requires Node.js)
    if ($nodeCheck) {
        try {
            Write-Host "Node.js detected. Performing dynamic local injection..." -ForegroundColor Green
            $asarTemp = Join-Path $tempDir "asar_extracted"
            
            Write-Host "Extracting your local app.asar..." -ForegroundColor Gray
            & npx --yes asar extract $backupAsar $asarTemp
            
            Write-Host "Injecting localized preload.js..." -ForegroundColor Gray
            $targetPreload = Join-Path $asarTemp "dist\preload.js"
            if (Test-Path $targetPreload) {
                # Load original preload.js
                $originalPreloadContent = Get-Content -Path $targetPreload -Raw
                
                # Load downloaded patch
                $downloadedContent = Get-Content -Path $downloadedPreload -Raw
                
                # Extract patch IIFE
                $patchMarker = "// Antigravity Chinese Localization Patch"
                $markerIndex = $downloadedContent.IndexOf($patchMarker)
                if ($markerIndex -ge 0) {
                    $patchCode = $downloadedContent.Substring($markerIndex)
                    
                    # Append patch code
                    $newPreloadContent = $originalPreloadContent + "`r`n`r`n" + $patchCode
                    Set-Content -Path $targetPreload -Value $newPreloadContent -Force
                    Write-Host "Successfully injected patch code into original preload.js!" -ForegroundColor Green
                } else {
                    Write-Warning "Could not find patch marker in downloaded preload.js. Falling back to direct replacement."
                    Copy-Item $downloadedPreload $targetPreload -Force
                }
            } else {
                Copy-Item $downloadedPreload $targetPreload -Force
            }
            
            Write-Host "Repacking app.asar..." -ForegroundColor Gray
            & npx --yes asar pack $asarTemp $originalAsar
            
            Write-Host "Dynamic injection applied successfully!" -ForegroundColor Green
            $patchedSuccessfully = $true
        } catch {
            Write-Warning "Dynamic local injection failed. Falling back to pre-compiled binary..."
        }
    }
} catch {
    Write-Warning "Failed to download preload.js from GitHub raw. Falling back to direct binary replacement..."
}

# Method B: Direct Binary Replacement (Download pre-compiled app.asar from GitHub Releases/Main)
if (-not $patchedSuccessfully) {
    try {
        Write-Host "Downloading precompiled Chinese app.asar from GitHub..." -ForegroundColor Green
        $downloadedAsar = Join-Path $tempDir "app.asar"
        Invoke-RestMethod -Uri "$rawBaseUrl/app.asar?t=$timestamp" -OutFile $downloadedAsar
        
        Write-Host "Applying precompiled app.asar replacement..." -ForegroundColor Green
        Copy-Item $downloadedAsar $originalAsar -Force
        $patchedSuccessfully = $true
    } catch {
        Write-Error "Error: Failed to download pre-compiled 'app.asar' from GitHub. Please check your network connection."
    }
}

# 5. Clean up temporary directory
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
}

# 6. Restart Antigravity
if ($patchedSuccessfully) {
    Write-Host "Patch successfully applied!" -ForegroundColor Green
    $exePath = Join-Path $programDir "Antigravity.exe"
    if (Test-Path $exePath) {
        Write-Host "Restarting Antigravity client..." -ForegroundColor Green
        # Use cmd /c start to completely detach the process so it won't close when PowerShell is closed
        Start-Process "cmd.exe" -ArgumentList "/c start `"`" `"$exePath`"" -WindowStyle Hidden
    } else {
        Write-Warning "Antigravity.exe not found. Please start it manually."
    }
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "     Patch successfully installed! Enjoy!                  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
