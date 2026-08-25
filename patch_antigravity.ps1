[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
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

# 3. Compile Universal Standard C# ASAR Engine in memory
$csharpPatcher = @"
using System;
using System.IO;
using System.Text;
using System.Collections.Generic;

public class UniversalAsarEngine {
    public class SimpleJson {
        public static object Parse(string json) {
            int index = 0;
            return ParseValue(json, ref index);
        }

        private static void SkipWhite(string s, ref int idx) {
            while (idx < s.Length && char.IsWhiteSpace(s[idx])) idx++;
        }

        private static object ParseValue(string s, ref int idx) {
            SkipWhite(s, ref idx);
            if (idx >= s.Length) return null;
            char c = s[idx];
            if (c == '{') return ParseObject(s, ref idx);
            if (c == '[') return ParseArray(s, ref idx);
            if (c == '"') return ParseString(s, ref idx);
            if (char.IsDigit(c) || c == '-') return ParseNumber(s, ref idx);
            if (s.Substring(idx).StartsWith("true")) { idx += 4; return true; }
            if (s.Substring(idx).StartsWith("false")) { idx += 5; return false; }
            if (s.Substring(idx).StartsWith("null")) { idx += 4; return null; }
            throw new Exception("Unexpected char at " + idx + ": " + c);
        }

        private static Dictionary<string, object> ParseObject(string s, ref int idx) {
            var dict = new Dictionary<string, object>();
            idx++;
            while (true) {
                SkipWhite(s, ref idx);
                if (idx >= s.Length) break;
                if (s[idx] == '}') { idx++; break; }
                string key = ParseString(s, ref idx);
                SkipWhite(s, ref idx);
                if (s[idx] == ':') idx++;
                object val = ParseValue(s, ref idx);
                dict[key] = val;
                SkipWhite(s, ref idx);
                if (s[idx] == ',') idx++;
                else if (s[idx] == '}') { idx++; break; }
            }
            return dict;
        }

        private static List<object> ParseArray(string s, ref int idx) {
            var list = new List<object>();
            idx++;
            while (true) {
                SkipWhite(s, ref idx);
                if (idx >= s.Length) break;
                if (s[idx] == ']') { idx++; break; }
                object val = ParseValue(s, ref idx);
                list.Add(val);
                SkipWhite(s, ref idx);
                if (s[idx] == ',') idx++;
                else if (s[idx] == ']') { idx++; break; }
            }
            return list;
        }

        private static string ParseString(string s, ref int idx) {
            SkipWhite(s, ref idx);
            if (s[idx] != '"') throw new Exception("Expected string quotes at " + idx);
            idx++;
            var sb = new StringBuilder();
            while (idx < s.Length) {
                char c = s[idx++];
                if (c == '"') break;
                if (c == '\\' && idx < s.Length) {
                    char esc = s[idx++];
                    if (esc == '"') sb.Append('"');
                    else if (esc == '\\') sb.Append('\\');
                    else if (esc == '/') sb.Append('/');
                    else if (esc == 'b') sb.Append('\b');
                    else if (esc == 'f') sb.Append('\f');
                    else if (esc == 'n') sb.Append('\n');
                    else if (esc == 'r') sb.Append('\r');
                    else if (esc == 't') sb.Append('\t');
                    else if (esc == 'u' && idx + 4 <= s.Length) {
                        string hex = s.Substring(idx, 4);
                        sb.Append((char)Convert.ToInt32(hex, 16));
                        idx += 4;
                    }
                } else {
                    sb.Append(c);
                }
            }
            return sb.ToString();
        }

        private static double ParseNumber(string s, ref int idx) {
            int start = idx;
            if (s[idx] == '-') idx++;
            while (idx < s.Length && (char.IsDigit(s[idx]) || s[idx] == '.' || s[idx] == 'e' || s[idx] == 'E' || s[idx] == '+' || s[idx] == '-')) idx++;
            return double.Parse(s.Substring(start, idx - start), System.Globalization.CultureInfo.InvariantCulture);
        }

        public static string Serialize(object obj) {
            var sb = new StringBuilder();
            SerializeValue(obj, sb);
            return sb.ToString();
        }

        private static void SerializeValue(object obj, StringBuilder sb) {
            if (obj == null) sb.Append("null");
            else if (obj is string) {
                sb.Append('"');
                foreach (char c in (string)obj) {
                    if (c == '"') sb.Append("\\\"");
                    else if (c == '\\') sb.Append("\\\\");
                    else if (c == '\b') sb.Append("\\b");
                    else if (c == '\f') sb.Append("\\f");
                    else if (c == '\n') sb.Append("\\n");
                    else if (c == '\r') sb.Append("\\r");
                    else if (c == '\t') sb.Append("\\t");
                    else sb.Append(c);
                }
                sb.Append('"');
            } else if (obj is bool) {
                sb.Append((bool)obj ? "true" : "false");
            } else if (obj is double || obj is float || obj is int || obj is long) {
                sb.Append(Convert.ToString(obj, System.Globalization.CultureInfo.InvariantCulture));
            } else if (obj is Dictionary<string, object>) {
                sb.Append('{');
                bool first = true;
                foreach (var kvp in (Dictionary<string, object>)obj) {
                    if (!first) sb.Append(',');
                    first = false;
                    SerializeValue(kvp.Key, sb);
                    sb.Append(':');
                    SerializeValue(kvp.Value, sb);
                }
                sb.Append('}');
            } else if (obj is List<object>) {
                sb.Append('[');
                bool first = true;
                foreach (var item in (List<object>)obj) {
                    if (!first) sb.Append(',');
                    first = false;
                    SerializeValue(item, sb);
                }
                sb.Append(']');
            }
        }
    }

    public class FileEntry {
        public string Path;
        public Dictionary<string, object> Node;
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

        var root = (Dictionary<string, object>)SimpleJson.Parse(headerJson);
        var allEntries = new List<FileEntry>();
        Collect((Dictionary<string, object>)root["files"], "", allEntries);

        FileEntry preloadEntry = allEntries.Find(e => e.Path.EndsWith("dist/preload.js") || e.Path.EndsWith("dist\\preload.js"));
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
        preloadEntry.Node["size"] = (double)preloadEntry.Size;
        
        if (preloadEntry.Node.ContainsKey("integrity")) {
            preloadEntry.Node.Remove("integrity");
        }

        allEntries.Sort((a, b) => a.OldOffset.CompareTo(b.OldOffset));
        long currentOffset = 0;
        foreach (var entry in allEntries) {
            if (entry.IsUnpacked) continue;
            entry.Node["offset"] = currentOffset.ToString();
            currentOffset += entry.Size;
        }

        string newJsonStr = SimpleJson.Serialize(root);
        byte[] newJsonBytes = Encoding.UTF8.GetBytes(newJsonStr);
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
            var root = (Dictionary<string, object>)SimpleJson.Parse(headerJson);
            var files = (Dictionary<string, object>)root["files"];
            var pkgNode = (Dictionary<string, object>)files["package.json"];
            long offset = long.Parse(pkgNode["offset"].ToString());
            long size = (long)Convert.ToDouble(pkgNode["size"]);
            byte[] pkgBytes = new byte[size];
            Array.Copy(asarBytes, dataStart + offset, pkgBytes, 0, (int)size);
            string pkgJson = Encoding.UTF8.GetString(pkgBytes);
            var pkgObj = (Dictionary<string, object>)SimpleJson.Parse(pkgJson);
            return pkgObj["version"].ToString();
        } catch {
            return "Active";
        }
    }

    private static void Collect(Dictionary<string, object> filesNode, string currentPath, List<FileEntry> list) {
        foreach (var kvp in filesNode) {
            string name = kvp.Key;
            var val = (Dictionary<string, object>)kvp.Value;
            string subPath = string.IsNullOrEmpty(currentPath) ? name : currentPath + "/" + name;
            if (val.ContainsKey("files")) {
                Collect((Dictionary<string, object>)val["files"], subPath, list);
            } else {
                bool isUnpacked = val.ContainsKey("unpacked") && val["unpacked"] is bool && (bool)val["unpacked"] == true;
                long offset = val.ContainsKey("offset") ? long.Parse(val["offset"].ToString()) : 0;
                long size = val.ContainsKey("size") ? (long)Convert.ToDouble(val["size"]) : 0;
                list.Add(new FileEntry { Path = subPath, Node = val, OldOffset = offset, Size = size, IsUnpacked = isUnpacked });
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

Function Show-Menu {
    Clear-Host
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "     Antigravity Chinese Patch Elite Toolkit v3.0         " -ForegroundColor Cyan
    Write-Host "     (Universal In-Place Hot Patch Engine)                " -ForegroundColor DarkCyan
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

    # Create / Sync Backup of original app.asar
    $isCurrentPatched = $false
    if (Test-Path $originalAsar) {
        if (Select-String -Path $originalAsar -Pattern "Antigravity Chinese Localization Patch" -Quiet) {
            $isCurrentPatched = $true
        }
    }

    if (-not $isCurrentPatched) {
        Write-Host "Fresh/unpatched Antigravity client detected. Creating backup..." -ForegroundColor Green
        Copy-Item $originalAsar $backupAsar -Force
    } else {
        if (-not (Test-Path $backupAsar)) {
            Write-Warning "Client is already patched and no original backup was found. Creating backup..."
            Copy-Item $originalAsar $backupAsar -Force
        } else {
            Write-Host "Backup file 'app.asar.bak' is verified." -ForegroundColor Green
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

    # Perform Hot In-Place Patch
    $tempDir = Join-Path $env:TEMP "antigravity_local_patch"
    if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue }
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    $tempPatchedAsar = Join-Path $tempDir "app.asar.patched"
    $sourceAsar = if (Test-Path $backupAsar) { $backupAsar } else { $originalAsar }

    $patchedSuccessfully = $false
    try {
        Write-Host "Performing ultra-fast native in-place ASAR injection..." -ForegroundColor Green
        [UniversalAsarEngine]::InjectPreload($sourceAsar, $tempPatchedAsar, $patchCode) | Out-Null
        Copy-Item $tempPatchedAsar $originalAsar -Force
        Write-Host "Dynamic injection applied successfully!" -ForegroundColor Green
        $patchedSuccessfully = $true
    } catch {
        Write-Error "Failed to apply patch: $_"
    }

    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue

    if ($patchedSuccessfully) {
        Write-Host ""
        Write-Host "🎉 汉化补丁安装成功！" -ForegroundColor Green
        Write-Host "💡 无需退出软件！若反重力软件正在运行中，在软件窗口按 [Ctrl + R] 即可立即生效！" -ForegroundColor Yellow
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
    
    try {
        Write-Host "Restoring original app.asar..." -ForegroundColor Green
        Copy-Item $backupAsar $originalAsar -Force
        Write-Host "Successfully restored original client!" -ForegroundColor Green
        Write-Host "若软件正在运行中，按 [Ctrl + R] 即可刷新恢复原版界面。" -ForegroundColor Yellow
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
        
        $version = [UniversalAsarEngine]::ReadPackageVersion($originalAsar)
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
    
    Write-Host "Engine: Universal In-Place Native Engine (无需 Node.js / 0 外部依赖)" -ForegroundColor Green
    
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
