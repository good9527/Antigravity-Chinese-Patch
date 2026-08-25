# patch_antigravity.ps1
# Interactive Elite Toolkit Console for Antigravity-Chinese-Patch
# Universal, zero-dependency, in-place ASAR patcher & management console

$ErrorActionPreference = "Stop"

# 1. Resolve Script Directory
$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Get-Location }

$localPreloadJs = Join-Path $scriptDir "dist\preload.js"

# 2. Smart Path Resolver
Function Find-AntigravityPath {
    $proc = Get-Process -Name "Antigravity" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($proc -and $proc.Path) {
        $dir = Split-Path -Parent $proc.Path
        if (Test-Path (Join-Path $dir "resources\app.asar")) { return $dir }
    }

    $userPath = "$env:LOCALAPPDATA\Programs\antigravity"
    if (Test-Path (Join-Path $userPath "resources\app.asar")) { return $userPath }

    $pfPath = "$env:ProgramFiles\Antigravity"
    if (Test-Path (Join-Path $pfPath "resources\app.asar")) { return $pfPath }
    
    $pfx86Path = "${env:ProgramFiles(x86)}\Antigravity"
    if (Test-Path (Join-Path $pfx86Path "resources\app.asar")) { return $pfx86Path }

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
    $programDir = "$env:LOCALAPPDATA\Programs\antigravity"
}

$resourcesDir = "$programDir\resources"
$originalAsar = "$resourcesDir\app.asar"
$backupAsar = "$resourcesDir\app.asar.bak"

# 3. Compile Native Zero-Dependency ASAR Patcher in memory
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

    public static string ReadPackageVersion(string inputAsar) {
        try {
            byte[] asarBytes = File.ReadAllBytes(inputAsar);
            uint jsonSize = BitConverter.ToUInt32(asarBytes, 12);
            string headerJson = Encoding.UTF8.GetString(asarBytes, 16, (int)jsonSize);
            long dataStart = 16 + jsonSize;
            var root = JsonNode.Parse(headerJson).AsObject();
            var pkgNode = root["files"]["package.json"].AsObject();
            long offset = long.Parse(pkgNode["offset"].ToString());
            long size = long.Parse(pkgNode["size"].ToString());
            byte[] pkgBytes = new byte[size];
            Array.Copy(asarBytes, dataStart + offset, pkgBytes, 0, (int)size);
            string pkgJson = Encoding.UTF8.GetString(pkgBytes);
            using (var doc = JsonDocument.Parse(pkgJson)) {
                return doc.RootElement.GetProperty("version").GetString();
            }
        } catch {
            return "Unknown";
        }
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
    # Type already defined
}

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
        Start-Process "cmd.exe" -ArgumentList "/c start `"`" `"$exePath`"" -WindowStyle Hidden
    } else {
        Write-Warning "Antigravity.exe not found at '$exePath'. Please start it manually."
    }
}

Function Show-Menu {
    Clear-Host
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "     Antigravity Chinese Patch Elite Toolkit v3.0         " -ForegroundColor Cyan
    Write-Host "     (Universal In-Place Native Patch Engine)             " -ForegroundColor DarkCyan
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
        Write-Host "Antigravity not found at '$programDir'." -ForegroundColor Yellow
        $programDir = Read-Host "Please enter your Antigravity installation folder"
        $script:programDir = $programDir
        $script:resourcesDir = "$programDir\resources"
        $script:originalAsar = "$resourcesDir\app.asar"
        $script:backupAsar = "$resourcesDir\app.asar.bak"
        if (-not (Test-Path $originalAsar)) {
            Write-Error "Error: Antigravity installation not found at '$programDir'."
            Read-Host "Press Enter to return to menu..."
            return
        }
    }
    
    if (-not (Test-Path $localPreloadJs)) {
        Write-Error "Error: Localization file 'dist\preload.js' not found in script directory."
        Read-Host "Press Enter to return to menu..."
        return
    }

    Stop-Client
    
    # Create / Sync Backup of original app.asar
    $isCurrentPatched = $false
    if (Test-Path $originalAsar) {
        if (Select-String -Path $originalAsar -Pattern "Antigravity Chinese Localization Patch" -Quiet) {
            $isCurrentPatched = $true
        }
    }

    if (-not $isCurrentPatched) {
        Write-Host "Fresh/unpatched Antigravity client detected. Updating backup..." -ForegroundColor Green
        Copy-Item $originalAsar $backupAsar -Force
    } else {
        if (-not (Test-Path $backupAsar)) {
            Write-Warning "Client is already patched and no original backup was found. Creating temporary backup..."
            Copy-Item $originalAsar $backupAsar -Force
        } else {
            Write-Host "Backup file 'app.asar.bak' is ready." -ForegroundColor Green
        }
    }

    # Extract patch code
    $localContent = Get-Content -Path $localPreloadJs -Raw -Encoding UTF8
    $patchMarker = "// Antigravity Chinese Localization Patch"
    $markerIndex = $localContent.IndexOf($patchMarker)
    if ($markerIndex -ge 0) {
        $patchCode = $localContent.Substring($markerIndex)
    } else {
        $patchCode = $localContent
    }

    # Perform In-Place Patch
    $tempDir = Join-Path $env:TEMP "antigravity_local_patch"
    if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    $tempPatchedAsar = Join-Path $tempDir "app.asar.patched"
    $sourceAsar = if (Test-Path $backupAsar) { $backupAsar } else { $originalAsar }

    $patchedSuccessfully = $false
    try {
        Write-Host "Performing ultra-fast native in-place ASAR injection..." -ForegroundColor Green
        [NativeAsarEngine]::InjectPreload($sourceAsar, $tempPatchedAsar, $patchCode)
        Copy-Item $tempPatchedAsar $originalAsar -Force
        Write-Host "Dynamic injection applied successfully!" -ForegroundColor Green
        $patchedSuccessfully = $true
    } catch {
        Write-Warning "Native patcher encountered an issue: $_. Trying fallback via npx asar..."
        $nodeCheck = Get-Command npx -ErrorAction SilentlyContinue
        if ($nodeCheck) {
            $asarTemp = Join-Path $tempDir "asar_extracted"
            & npx --yes asar extract $sourceAsar $asarTemp
            $targetPreload = Join-Path $asarTemp "dist\preload.js"
            $orig = Get-Content $targetPreload -Raw -Encoding UTF8
            $mIdx = $orig.IndexOf($patchMarker)
            if ($mIdx -ge 0) { $orig = $orig.Substring(0, $mIdx).Trim() }
            Set-Content -Path $targetPreload -Value ($orig + "`r`n`r`n" + $patchCode) -Encoding UTF8
            & npx --yes asar pack $asarTemp $originalAsar --unpack-dir "**/chrome-devtools-mcp"
            Write-Host "Dynamic injection applied via npx asar fallback!" -ForegroundColor Green
            $patchedSuccessfully = $true
        } else {
            Write-Error "Failed to apply patch: $_"
        }
    }

    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue

    if ($patchedSuccessfully) {
        Write-Host "Patch successfully installed!" -ForegroundColor Green
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
        
        $isPatched = "Unpatched (原装未汉化)"
        $patchedColor = "Green"
        if (Select-String -Path $originalAsar -Pattern "Antigravity Chinese Localization Patch" -Quiet) {
            $isPatched = "Patched (已汉化)"
            $patchedColor = "Cyan"
        }
        
        $version = [NativeAsarEngine]::ReadPackageVersion($originalAsar)
        Write-Host "Client Version: $version" -ForegroundColor White
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
        Write-Host "Node.js/npx Environment: Not required (纯原生 Native 引擎模式)" -ForegroundColor Green
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
