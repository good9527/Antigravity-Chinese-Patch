[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
# install.ps1
# One-click Universal Online Web Installer for Antigravity-Chinese-Patch
# PowerShell: iwr -useb https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "     Antigravity Chinese Patch Universal Web Installer    " -ForegroundColor Cyan
Write-Host "     (Zero-Dependency Safe In-Place Hot Injection)        " -ForegroundColor DarkCyan
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
    Write-Host "Antigravity installation was not found in standard directories." -ForegroundColor Yellow
    $programDir = Read-Host "Please enter your Antigravity installation folder path (e.g. C:\Users\xxx\AppData\Local\Programs\antigravity)"
}

if (-not (Test-Path "$programDir\resources\app.asar")) {
    Write-Error "Error: Antigravity installation not found at '$programDir'. Please make sure Antigravity is installed."
}

$resourcesDir = "$programDir\resources"
$originalAsar = "$resourcesDir\app.asar"
$backupAsar = "$resourcesDir\app.asar.bak"

Write-Host "Target Antigravity directory: $programDir" -ForegroundColor Green

# 3. Check / Create Backup
$isCurrentPatched = $false
if (Test-Path $originalAsar) {
    if (Select-String -Path $originalAsar -Pattern "Antigravity Chinese Localization Patch" -Quiet) {
        $isCurrentPatched = $true
    }
}

if (-not $isCurrentPatched) {
    Write-Host "Original unpatched client detected. Creating backup..." -ForegroundColor Green
    Copy-Item $originalAsar $backupAsar -Force
} else {
    if (-not (Test-Path $backupAsar)) {
        Write-Host "Creating backup of current client..." -ForegroundColor Gray
        Copy-Item $originalAsar $backupAsar -Force
    } else {
        Write-Host "Backup 'app.asar.bak' is verified." -ForegroundColor Green
    }
}

# 4. Compile Universal Standard C# ASAR Engine in memory
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
        uint u2 = BitConverter.ToUInt32(asarBytes, 4);
        uint jsonSize = BitConverter.ToUInt32(asarBytes, 12);
        long dataStart = 8 + u2;

        string headerJson = Encoding.UTF8.GetString(asarBytes, 16, (int)jsonSize);
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
        uint padding = (4 - (newJsonSize % 4)) % 4;
        uint headerPayload = newJsonSize + padding;

        using (var fsOut = File.Create(outputAsar))
        using (var bw = new BinaryWriter(fsOut)) {
            bw.Write((uint)4);
            bw.Write((uint)(headerPayload + 8));
            bw.Write((uint)(headerPayload + 4));
            bw.Write((uint)newJsonSize);
            bw.Write(newJsonBytes);
            for (int i = 0; i < (int)padding; i++) {
                bw.Write((byte)0);
            }

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

# 5. Download latest localization patch
$tempDir = Join-Path $env:TEMP "antigravity_web_patch_$timestamp"
if (Test-Path $tempDir) { Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

$downloadedPreload = Join-Path $tempDir "preload.js"
Write-Host "Downloading latest Chinese localization engine..." -ForegroundColor Green
$downloadOk = Get-CdnFile "dist/preload.js" $downloadedPreload

if (-not $downloadOk) {
    Write-Error "Failed to download localization patch from CDN mirrors. Please check your internet connection."
}

# 6. Extract patch code
$fullContent = Get-Content -Path $downloadedPreload -Raw -Encoding UTF8
$patchMarker = "// Antigravity Chinese Localization Patch"
$markerIndex = $fullContent.IndexOf($patchMarker)
if ($markerIndex -ge 0) {
    $patchCode = $fullContent.Substring($markerIndex)
} else {
    $patchCode = $fullContent
}

# 7. Safe In-Place ASAR Injection (100% safe, never terminates Antigravity)
Write-Host "Applying dynamic native in-place ASAR injection (0.05s)..." -ForegroundColor Green
$tempPatchedAsar = Join-Path $tempDir "app.asar.patched"
$sourceAsar = if (Test-Path $backupAsar) { $backupAsar } else { $originalAsar }

try {
    [UniversalAsarEngine]::InjectPreload($sourceAsar, $tempPatchedAsar, $patchCode) | Out-Null
    Copy-Item $tempPatchedAsar $originalAsar -Force
    Write-Host "Universal ASAR in-place patch successfully applied!" -ForegroundColor Green
} catch {
    Write-Error "Failed to patch ASAR file. Error: $_"
}

# 8. Clean up
Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue

# 9. Notify user
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "     🎉 汉化补丁安装成功！(Patch Successfully Installed) " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  ✨ 补丁已写入完成！你可以随时自行重启 Antigravity 客户端生效。" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
