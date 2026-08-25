# install.ps1
# One-click Universal Online Web Installer for Antigravity-Chinese-Patch
# PowerShell: iwr -useb https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "     Antigravity Chinese Patch Universal Web Installer    " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Fast CDN Multi-Mirror Downloader
$repoOwner = "good9527"
$repoName = "Antigravity-Chinese-Patch"
$timestamp = (Get-Date).Ticks

Function Get-CdnFile($relativePath, $destinationPath) {
    $mirrors = @(
        "https://fastly.jsdelivr.net/gh/$repoOwner/$repoName@main/$relativePath`?t=$timestamp",
        "https://testingcf.jsdelivr.net/gh/$repoOwner/$repoName@main/$relativePath`?t=$timestamp",
        "https://ghfast.top/https://raw.githubusercontent.com/$repoOwner/$repoName/main/$relativePath`?t=$timestamp",
        "https://raw.githubusercontent.com/$repoOwner/$repoName/main/$relativePath`?t=$timestamp"
    )
    
    foreach ($url in $mirrors) {
        try {
            Write-Host "Connecting to mirror: $url ..." -ForegroundColor Gray
            Invoke-RestMethod -Uri $url -OutFile $destinationPath -TimeoutSec 10
            if ((Test-Path $destinationPath) -and (Get-Item $destinationPath).Length -gt 100) {
                Write-Host "Successfully downloaded from mirror!" -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Warning "Mirror connection failed or timed out. Trying next mirror..."
        }
    }
    return $false
}

# 2. Smart Path Resolver (Active Process -> Registry -> Default Folders)
Function Find-AntigravityPath {
    # 2.1 Check active process
    $proc = Get-Process -Name "Antigravity" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($proc -and $proc.Path) {
        $dir = Split-Path -Parent $proc.Path
        if (Test-Path (Join-Path $dir "resources\app.asar")) { return $dir }
    }

    # 2.2 Check default user directory
    $userPath = "$env:LOCALAPPDATA\Programs\antigravity"
    if (Test-Path (Join-Path $userPath "resources\app.asar")) { return $userPath }

    # 2.3 Check Program Files
    $pfPath = "$env:ProgramFiles\Antigravity"
    if (Test-Path (Join-Path $pfPath "resources\app.asar")) { return $pfPath }
    
    $pfx86Path = "${env:ProgramFiles(x86)}\Antigravity"
    if (Test-Path (Join-Path $pfx86Path "resources\app.asar")) { return $pfx86Path }

    # 2.4 Check Windows Registry Uninstall entries
    $regRoots = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    foreach ($root in $regRoots) {
        $apps = Get-ItemProperty $root -ErrorAction SilentlyContinue
        foreach ($app in $apps) {
            if ($app.DisplayName -like "*Antigravity*" -and $app.InstallLocation) {
                if (Test-Path (Join-Path $app.InstallLocation "resources\app.asar")) {
                    return $app.InstallLocation
                }
            }
        }
    }
    return $null
}

$programDir = Find-AntigravityPath
if (-not $programDir) {
    Write-Host "Antigravity installation was not found in standard directories." -ForegroundColor Yellow
    $programDir = Read-Host "Please enter your Antigravity installation folder path (e.g. C:\Users\xxx\AppData\Local\Programs\antigravity)"
}

if (-not (Test-Path "$programDir\resources\app.asar")) {
    Write-Error "Error: Antigravity installation not found at '$programDir'. Please make sure Antigravity is installed."
}

$resourcesDir = "$programDir\resources"
$originalAsar = "$resourcesDir\app.asar"
$backupAsar = "$resourcesDir\app.asar.bak"

Write-Host "Found Antigravity at: $programDir" -ForegroundColor Green

# 3. Terminate running Antigravity client
Write-Host "Closing running Antigravity client..." -ForegroundColor Yellow
$processes = Get-Process -Name "Antigravity" -ErrorAction SilentlyContinue
if ($processes) {
    Stop-Process -Name "Antigravity" -Force
    Start-Sleep -Seconds 2
}

# 4. Create / Verify Backup
$isCurrentPatched = $false
if (Test-Path $originalAsar) {
    if (Select-String -Path $originalAsar -Pattern "Antigravity Chinese Localization Patch" -Quiet) {
        $isCurrentPatched = $true
    }
}

if (-not $isCurrentPatched) {
    Write-Host "Original unpatched Antigravity detected. Creating fresh backup..." -ForegroundColor Green
    Copy-Item $originalAsar $backupAsar -Force
} else {
    if (-not (Test-Path $backupAsar)) {
        Write-Warning "Client is already patched and no original backup was found. Creating temporary backup..."
        Copy-Item $originalAsar $backupAsar -Force
    } else {
        Write-Host "Backup file 'app.asar.bak' is ready." -ForegroundColor Green
    }
}

# 5. Compile Native Zero-Dependency ASAR Patcher in memory
$csharpPatcher = @"
using System;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Collections.Generic;

public class NativeAsarEngine {
    public class Entry {
        public string Path;
        public JsonObject Node;
        public long OldOffset;
        public long Size;
        public bool IsUnpacked;
        public byte[] OverriddenData;
    }

    public static bool InjectPreload(string inputAsar, string outputAsar, string patchCode) {
        byte[] asarBytes = File.ReadAllBytes(inputAsar);
        uint jsonSize = BitConverter.ToUInt32(asarBytes, 12);
        string headerJson = Encoding.UTF8.GetString(asarBytes, 16, (int)jsonSize);
        long dataStart = 16 + jsonSize;

        var root = JsonNode.Parse(headerJson).AsObject();
        var allEntries = new List<Entry>();
        Collect(root["files"].AsObject(), "", allEntries);

        Entry preloadEntry = allEntries.Find(e => e.Path.EndsWith("dist/preload.js") || e.Path.EndsWith("dist\\preload.js"));
        if (preloadEntry == null) throw new Exception("dist/preload.js not found in app.asar");

        byte[] oldPreloadBytes = new byte[preloadEntry.Size];
        Array.Copy(asarBytes, dataStart + preloadEntry.OldOffset, oldPreloadBytes, 0, (int)preloadEntry.Size);
        string oldPreload = Encoding.UTF8.GetString(oldPreloadBytes);

        string patchMarker = "// Antigravity Chinese Localization Patch";
        int markerIdx = oldPreload.IndexOf(patchMarker);
        if (markerIdx >= 0) {
            oldPreload = oldPreload.Substring(0, markerIdx).TrimEnd();
        }

        string newPreload = oldPreload + "\r\n\r\n" + patchCode;
        byte[] newPreloadBytes = Encoding.UTF8.GetBytes(newPreload);
        preloadEntry.OverriddenData = newPreloadBytes;
        preloadEntry.Size = newPreloadBytes.Length;
        preloadEntry.Node["size"] = preloadEntry.Size;

        allEntries.Sort((a, b) => a.OldOffset.CompareTo(b.OldOffset));
        long currentOffset = 0;
        foreach (var entry in allEntries) {
            if (entry.IsUnpacked) continue;
            entry.Node["offset"] = currentOffset.ToString();
            currentOffset += entry.Size;
        }

        byte[] newJsonBytes = Encoding.UTF8.GetBytes(root.ToJsonString());
        uint newJsonSize = (uint)newJsonBytes.Length;

        using (var fsOut = File.Create(outputAsar))
        using (var bw = new BinaryWriter(fsOut)) {
            bw.Write((uint)4);
            bw.Write((uint)(newJsonSize + 8));
            bw.Write((uint)(newJsonSize + 4));
            bw.Write((uint)newJsonSize);
            bw.Write(newJsonBytes);

            foreach (var entry in allEntries) {
                if (entry.IsUnpacked) continue;
                if (entry.OverriddenData != null) {
                    bw.Write(entry.OverriddenData);
                } else {
                    bw.Write(asarBytes, (int)(dataStart + entry.OldOffset), (int)entry.Size);
                }
            }
        }
        return true;
    }

    private static void Collect(JsonObject filesNode, string currentPath, List<Entry> list) {
        foreach (var kvp in filesNode) {
            string name = kvp.Key;
            var val = kvp.Value.AsObject();
            string subPath = string.IsNullOrEmpty(currentPath) ? name : currentPath + "/" + name;
            if (val.ContainsKey("files")) {
                Collect(val["files"].AsObject(), subPath, list);
            } else {
                bool isUnpacked = val.ContainsKey("unpacked") && val["unpacked"].GetValue<bool>() == true;
                long offset = val.ContainsKey("offset") ? long.Parse(val["offset"].ToString()) : 0;
                long size = val.ContainsKey("size") ? long.Parse(val["size"].ToString()) : 0;
                list.Add(new Entry { Path = subPath, Node = val, OldOffset = offset, Size = size, IsUnpacked = isUnpacked });
            }
        }
    }
}
"@

try {
    Add-Type -TypeDefinition $csharpPatcher -Language CSharp
} catch {
    # Type might already be loaded in current session
}

# 6. Download latest preload.js patch code
$tempDir = Join-Path $env:TEMP "antigravity_web_patch_$timestamp"
if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

$downloadedPreload = Join-Path $tempDir "preload.js"
Write-Host "Downloading latest Chinese localization engine..." -ForegroundColor Green
$downloadOk = Get-CdnFile "dist/preload.js" $downloadedPreload

if (-not $downloadOk) {
    Write-Error "Failed to download localization patch from CDN mirrors. Please check your internet connection."
}

# 7. Extract patch code
$fullContent = Get-Content -Path $downloadedPreload -Raw -Encoding UTF8
$patchMarker = "// Antigravity Chinese Localization Patch"
$markerIndex = $fullContent.IndexOf($patchMarker)
if ($markerIndex -ge 0) {
    $patchCode = $fullContent.Substring($markerIndex)
} else {
    $patchCode = $fullContent
}

# 8. Apply In-Place Native ASAR Patch
Write-Host "Applying dynamic in-place ASAR injection (0.05s ultra-fast)..." -ForegroundColor Green
$tempPatchedAsar = Join-Path $tempDir "app.asar.patched"

$sourceAsar = if (Test-Path $backupAsar) { $backupAsar } else { $originalAsar }

try {
    [NativeAsarEngine]::InjectPreload($sourceAsar, $tempPatchedAsar, $patchCode)
    Copy-Item $tempPatchedAsar $originalAsar -Force
    Write-Host "Universal ASAR in-place patch successfully applied!" -ForegroundColor Green
} catch {
    Write-Warning "Native C# patcher encountered an issue: $_. Falling back to Node.js/npx if available..."
    $npxCmd = Get-Command npx -ErrorAction SilentlyContinue
    if ($npxCmd) {
        $asarTemp = Join-Path $tempDir "asar_extracted"
        & npx --yes asar extract $sourceAsar $asarTemp
        $targetPreload = Join-Path $asarTemp "dist\preload.js"
        $orig = Get-Content $targetPreload -Raw -Encoding UTF8
        $mIdx = $orig.IndexOf($patchMarker)
        if ($mIdx -ge 0) { $orig = $orig.Substring(0, $mIdx).Trim() }
        Set-Content -Path $targetPreload -Value ($orig + "`r`n`r`n" + $patchCode) -Encoding UTF8
        & npx --yes asar pack $asarTemp $originalAsar --unpack-dir "**/chrome-devtools-mcp"
        Write-Host "Applied fallback injection successfully via npx asar!" -ForegroundColor Green
    } else {
        Write-Error "Failed to patch ASAR file. Error: $_"
    }
}

# 9. Clean up temporary files
Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue

# 10. Restart Antigravity
$exePath = Join-Path $programDir "Antigravity.exe"
if (Test-Path $exePath) {
    Write-Host "Restarting Antigravity client..." -ForegroundColor Green
    Start-Process "cmd.exe" -ArgumentList "/c start `"`" `"$exePath`"" -WindowStyle Hidden
} else {
    Write-Host "Patch complete! Please start Antigravity manually." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "     Patch successfully installed! Enjoy!                  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
