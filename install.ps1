param(
    [Parameter(Mandatory=$false)][Alias("i")][switch]$Install,
    [Parameter(Mandatory=$false)][Alias("u")][switch]$Uninstall,
    [Parameter(Mandatory=$false)][Alias("c")][switch]$Check,
    [Parameter(Mandatory=$false)][Alias("r")][switch]$Restore,
    [Parameter(Mandatory=$false)][ValidateSet("enable", "disable", "status", "")][string]$Daemon = "",
    [Parameter(Mandatory=$false)][switch]$DaemonOn,
    [Parameter(Mandatory=$false)][switch]$DaemonOff,
    [Parameter(Mandatory=$false)][Alias("q")][switch]$Quiet,
    [Parameter(Mandatory=$false)][switch]$Silent,
    [Parameter(Mandatory=$false)][Alias("p")][string]$Path,
    [Parameter(Mandatory=$false)][switch]$Json
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Stop"

if ($Silent) { $Quiet = $true }

# 1. Global Paths and Constants
$repoOwner = "good9527"
$repoName = "Antigravity-Chinese-Patch"
$cacheDir = Join-Path $env:APPDATA "AntigravityChinesePatch"
$cachedPreload = Join-Path $cacheDir "preload.js"
$cachedWatcher = Join-Path $cacheDir "watcher.ps1"
$patchMarker = "// Antigravity Chinese Localization Patch"
$taskName = "AntigravityChinesePatchWatcher"
$regRunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$regRunName = "AntigravityChinesePatchAutoHeal"

$scriptDir = $PSScriptRoot
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }

Function Write-Msg {
    param([string]$Message, [string]$Color = "White")
    if (-not $Quiet) {
        Write-Host $Message -ForegroundColor $Color
    }
}

# 2. In-Memory Standard C# ASAR Engine Compilation
$csharpPatcher = @'
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
        if (asarBytes.Length < 16) throw new Exception("ASAR file too small");
        uint magic = BitConverter.ToUInt32(asarBytes, 0);
        if (magic != 4) throw new Exception("Invalid ASAR magic number");

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

    public static bool InjectPreloadInPlace(string targetAsar, string patchCode) {
        byte[] asarBytes;
        using (var fsIn = new FileStream(targetAsar, FileMode.Open, FileAccess.Read, FileShare.ReadWrite)) {
            asarBytes = new byte[fsIn.Length];
            int totalRead = 0;
            while (totalRead < asarBytes.Length) {
                int r = fsIn.Read(asarBytes, totalRead, asarBytes.Length - totalRead);
                if (r <= 0) break;
                totalRead += r;
            }
        }

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

        using (var fsOut = new FileStream(targetAsar, FileMode.Open, FileAccess.Write, FileShare.ReadWrite)) {
            fsOut.SetLength(0);
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
        }
        return true;
    }

    public static string ReadPackageVersion(string inputAsar) {
        try {
            byte[] asarBytes = File.ReadAllBytes(inputAsar);
            if (asarBytes.Length < 16) return "Unknown";
            uint u2 = BitConverter.ToUInt32(asarBytes, 4);
            uint jsonSize = BitConverter.ToUInt32(asarBytes, 12);
            string headerJson = Encoding.UTF8.GetString(asarBytes, 16, (int)jsonSize);
            long dataStart = 8 + u2;
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
'@

try {
    if (-not ([System.Management.Automation.PSTypeName]'UniversalAsarEngine').Type) {
        Add-Type -TypeDefinition $csharpPatcher -Language CSharp
    }
} catch {}

# 3. Multi-Mirror CDN Waterfall Downloader
Function Get-CdnFile($relativePath, $destinationPath) {
    $timestamp = (Get-Date).Ticks
    $mirrors = @(
        "https://fastly.jsdelivr.net/gh/$repoOwner/$repoName@main/$relativePath`?t=$timestamp",
        "https://testingcf.jsdelivr.net/gh/$repoOwner/$repoName@main/$relativePath`?t=$timestamp",
        "https://ghfast.top/https://raw.githubusercontent.com/$repoOwner/$repoName/main/$relativePath`?t=$timestamp",
        "https://cdn.jsdelivr.net/gh/$repoOwner/$repoName@main/$relativePath`?t=$timestamp",
        "https://raw.githubusercontent.com/$repoOwner/$repoName/main/$relativePath`?t=$timestamp"
    )
    
    foreach ($url in $mirrors) {
        try {
            Write-Msg "Connecting to mirror: $url ..." "Gray"
            Invoke-RestMethod -Uri $url -OutFile $destinationPath -TimeoutSec 5
            if ((Test-Path $destinationPath) -and (Get-Item $destinationPath).Length -gt 50) {
                Write-Msg "Successfully downloaded from mirror!" "Green"
                return $true
            }
        } catch {
            Write-Msg "Mirror timeout or error. Falling back to next mirror..." "Yellow"
        }
    }
    return $false
}

# 4. Smart Path Resolver
Function Find-AntigravityPath {
    if ($Path -and (Test-Path (Join-Path $Path "resources\app.asar"))) {
        return $Path
    }

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

# 5. Offline Cache Synchronizer
Function Sync-OfflineCache($preloadSourcePath) {
    if (-not (Test-Path $cacheDir)) {
        New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
    }

    if ($preloadSourcePath -and (Test-Path $preloadSourcePath)) {
        Copy-Item -Path $preloadSourcePath -Destination $cachedPreload -Force
    }

    # Cache watcher.ps1
    $watcherSrc = $null
    if ($scriptDir -and (Test-Path (Join-Path $scriptDir "watcher\watcher.ps1"))) {
        $watcherSrc = Join-Path $scriptDir "watcher\watcher.ps1"
    } elseif ($scriptDir -and (Test-Path (Join-Path $scriptDir "watcher.ps1"))) {
        $watcherSrc = Join-Path $scriptDir "watcher.ps1"
    }

    if ($watcherSrc -and (Test-Path $watcherSrc)) {
        Copy-Item -Path $watcherSrc -Destination $cachedWatcher -Force
    }
}

# 6. Daemon Controller
Function Set-DaemonState($action) {
    if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null }
    
    # Check if watcher.ps1 is in cache
    if (-not (Test-Path $cachedWatcher)) {
        Sync-OfflineCache $cachedPreload
    }

    if ($action -eq "enable") {
        try {
            $taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$cachedWatcher`""
            $taskTrigger = New-ScheduledTaskTrigger -AtLogOn
            $taskSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0 -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
            $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
            Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Principal $principal -Force | Out-Null
            
            Set-ItemProperty -Path $regRunKey -Name $regRunName -Value "powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$cachedWatcher`"" -ErrorAction SilentlyContinue
            Write-Msg "Auto-healing daemon enabled (Scheduled Task: $taskName + Run Key)." "Green"
        } catch {
            Set-ItemProperty -Path $regRunKey -Name $regRunName -Value "powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$cachedWatcher`"" -ErrorAction SilentlyContinue
            Write-Msg "Auto-healing daemon enabled via HKCU Run key." "Yellow"
        }

        # Immediately spawn active background watcher process if not currently running
        try {
            $runningWatcher = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { 
                ($_.CommandLine -like "*$cachedWatcher*" -or $_.CommandLine -like "*watcher.ps1*") -and $_.ProcessId -ne $PID 
            }
            if (-not $runningWatcher) {
                Start-Process -FilePath "powershell.exe" -ArgumentList "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$cachedWatcher`"" -WindowStyle Hidden
                Write-Msg "Active background watcher process spawned (<10ms)." "Green"
            }
        } catch {}

        # Configure launcher pre-check hook if launcher script exists
        $launcherCmd = "$env:APPDATA\Antigravity\launch-antigravity-with-proxy.cmd"
        if (Test-Path $launcherCmd) {
            try {
                $cmdLines = Get-Content -Path $launcherCmd -Raw -Encoding UTF8
                if ($cmdLines -notmatch "watcher\.ps1") {
                    $hookBlock = "`r`n:: [Auto-Healing Guard] Pre-launch self-healing check`r`npowershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"`%APPDATA`%\\AntigravityChinesePatch\\watcher.ps1`" -RunOnce -Quiet`r`n"
                    $newCmd = $cmdLines.Replace("start `"", $hookBlock + "start `"")
                    Set-Content -Path $launcherCmd -Value $newCmd -Encoding UTF8
                    Write-Msg "Injected pre-launch zero-latency auto-heal guard into launcher." "Green"
                }
            } catch {}
        }
        return $true
    } elseif ($action -eq "disable") {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
        Remove-ItemProperty -Path $regRunKey -Name $regRunName -ErrorAction SilentlyContinue
        Write-Msg "Auto-healing daemon disabled." "Yellow"
        return $true
    } elseif ($action -eq "status") {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        $runVal = (Get-ItemProperty -Path $regRunKey -ErrorAction SilentlyContinue).$regRunName
        $active = ($null -ne $task) -or ($null -ne $runVal)
        $statusColor = if ($active) { "Green" } else { "Yellow" }
        $statusText = if ($active) { "ENABLED" } else { "DISABLED" }
        if (-not $Quiet) {
            Write-Host "Daemon Status: $statusText" -ForegroundColor $statusColor
        }
        return $active
    }
}

# 7. Action: Check / Diagnostics
Function Invoke-CheckDiagnostics {
    $progDir = Find-AntigravityPath
    $resDir = if ($progDir) { Join-Path $progDir "resources" } else { $null }
    $asar = if ($resDir) { Join-Path $resDir "app.asar" } else { $null }
    $bak = if ($resDir) { Join-Path $resDir "app.asar.bak" } else { $null }

    $asarExists = ($asar -and (Test-Path $asar))
    $bakExists = ($bak -and (Test-Path $bak))
    $isPatched = $false
    $clientVersion = "Unknown"

    if ($asarExists) {
        try {
            $clientVersion = [UniversalAsarEngine]::ReadPackageVersion($asar)
            if (Select-String -Path $asar -Pattern $patchMarker -Quiet) {
                $isPatched = $true
            }
        } catch {}
    }

    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    $runVal = (Get-ItemProperty -Path $regRunKey -ErrorAction SilentlyContinue).$regRunName
    $daemonEnabled = ($null -ne $task) -or ($null -ne $runVal)
    $healthy = $asarExists -and $isPatched -and $bakExists

    if ($Json) {
        $out = @{
            path = $progDir
            asar_exists = $asarExists
            version = $clientVersion
            is_patched = $isPatched
            backup_exists = $bakExists
            daemon_enabled = $daemonEnabled
            healthy = $healthy
        }
        return ($out | ConvertTo-Json -Compress)
    }

    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "     Antigravity Chinese Patch Health Diagnostics         " -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  Installation Directory : $(if ($progDir) { $progDir } else { 'NOT FOUND' })"
    $patchedColor = if ($isPatched) { "Green" } else { "Yellow" }
    $bakColor = if ($bakExists) { "Green" } else { "Yellow" }
    $daemonColor = if ($daemonEnabled) { "Green" } else { "Gray" }
    $verdictColor = if ($healthy) { "Green" } else { "Yellow" }
    $verdictText = if ($healthy) { "HEALTHY (100% Operational & Self-Healing Enabled)" } else { "ATTENTION REQUIRED (Client unpatched or missing backup)" }

    Write-Host "  Active ASAR Status     : $(if ($isPatched) { 'PATCHED [OK]' } else { 'UNPATCHED / MISSING' })" -ForegroundColor $patchedColor
    Write-Host "  Original Clean Backup  : $(if ($bakExists) { 'PRESENT [OK]' } else { 'NOT FOUND' })" -ForegroundColor $bakColor
    Write-Host "  Auto-Healing Daemon    : $(if ($daemonEnabled) { 'ENABLED [OK]' } else { 'DISABLED' })" -ForegroundColor $daemonColor
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  Verdict: $verdictText" -ForegroundColor $verdictColor
    Write-Host "==========================================================" -ForegroundColor Cyan

    return $(if ($healthy) { 0 } else { 1 })
}

# 8. Action: Restore
Function Invoke-RestoreBackup {
    $progDir = Find-AntigravityPath
    if (-not $progDir) {
        Write-Error "Antigravity installation directory not found."
    }
    $asar = Join-Path $progDir "resources\app.asar"
    $bak = Join-Path $progDir "resources\app.asar.bak"

    if (-not (Test-Path $bak)) {
        Write-Error "Backup file 'app.asar.bak' not found. Cannot restore."
    }

    Write-Msg "Restoring official Google binary from backup..." "Yellow"
    Copy-Item -Path $bak -Destination $asar -Force
    Write-Msg "Successfully restored pristine official client binary!" "Green"
}

# 9. Action: Uninstall
Function Invoke-UninstallPatch {
    Invoke-RestoreBackup
    Set-DaemonState "disable"
    if (Test-Path $cacheDir) {
        Remove-Item -Recurse -Force $cacheDir -ErrorAction SilentlyContinue
    }
    Write-Msg "Antigravity Chinese Patch has been completely uninstalled." "Green"
}

# 10. Action: Install (In-Place Zero Disruption Hot Patch)
Function Invoke-InstallPatch {
    Write-Msg "==========================================================" "Cyan"
    Write-Msg "     Antigravity Chinese Patch Universal Installer        " "Cyan"
    Write-Msg "     (In-Place ASAR Hot Patch + Auto-Healing Daemon)      " "DarkCyan"
    Write-Msg "==========================================================" "Cyan"

    $progDir = Find-AntigravityPath
    if (-not $progDir) {
        if (-not $Quiet) {
            Write-Host "Antigravity installation was not found automatically." -ForegroundColor Yellow
            $progDir = Read-Host "Please enter your Antigravity folder path"
        }
        if (-not $progDir -or -not (Test-Path "$progDir\resources\app.asar")) {
            Write-Error "Antigravity installation not found at '$progDir'."
        }
    }

    $resourcesDir = Join-Path $progDir "resources"
    $originalAsar = Join-Path $resourcesDir "app.asar"
    $backupAsar = Join-Path $resourcesDir "app.asar.bak"

    Write-Msg "Target directory: $progDir" "Green"

    # Step 1: Backup handling
    $isPatched = $false
    try {
        if (Select-String -Path $originalAsar -Pattern $patchMarker -Quiet) {
            $isPatched = $true
        }
    } catch {}

    if (-not $isPatched) {
        Write-Msg "Creating pristine official backup (app.asar.bak)..." "Green"
        Copy-Item -Path $originalAsar -Destination $backupAsar -Force
    } else {
        if (-not (Test-Path $backupAsar)) {
            Write-Msg "Creating backup of current client..." "Yellow"
            Copy-Item -Path $originalAsar -Destination $backupAsar -Force
        } else {
            Write-Msg "Backup file app.asar.bak is verified." "Green"
        }
    }

    # Step 2: Resolve patch code (Local file -> Cache -> CDN Waterfall)
    $preloadCode = $null
    $localDist = if ($scriptDir) { Join-Path $scriptDir "dist\preload.js" } else { $null }
    
    if ($localDist -and (Test-Path $localDist)) {
        Write-Msg "Loading patch engine from local package..." "Green"
        $preloadCode = Get-Content -Path $localDist -Raw -Encoding UTF8
        Sync-OfflineCache $localDist
    } elseif (Test-Path $cachedPreload) {
        Write-Msg "Loading patch engine from offline cache..." "Green"
        $preloadCode = Get-Content -Path $cachedPreload -Raw -Encoding UTF8
    } else {
        # Download from CDN
        $tempDir = Join-Path $env:TEMP ("antigravity_dl_" + (Get-Date).Ticks)
        New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
        $dlPreload = Join-Path $tempDir "preload.js"
        Write-Msg "Downloading latest Chinese localization patch via CDN..." "Green"
        $dlOk = Get-CdnFile "dist/preload.js" $dlPreload
        if ($dlOk) {
            $preloadCode = Get-Content -Path $dlPreload -Raw -Encoding UTF8
            Sync-OfflineCache $dlPreload
        }
        Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    }

    if (-not $preloadCode) {
        Write-Error "Failed to obtain localization patch engine. Please check your network connection."
    }

    # Extract patch body starting from marker
    $markerIdx = $preloadCode.IndexOf($patchMarker)
    $patchSnippet = if ($markerIdx -ge 0) { $preloadCode.Substring($markerIdx) } else { $preloadCode }

    # Step 3: Fast Native In-Place ASAR Injection (<50ms, Zero Session Disruption)
    Write-Msg "Applying zero-disruption in-place ASAR injection..." "Green"
    $tempPatched = Join-Path $resourcesDir "app.asar.patched"
    $sourceAsar = $originalAsar

    $maxRetries = 5
    $patchedOk = $false
    for ($i = 1; $i -le $maxRetries; $i++) {
        # Method 1: Direct in-place stream write (works even while Antigravity is open!)
        try {
            $patchedOk = [UniversalAsarEngine]::InjectPreloadInPlace($originalAsar, $patchSnippet)
            if ($patchedOk) {
                Write-Msg "In-place ASAR stream injection succeeded (<50ms)!" "Green"
                break
            }
        } catch {
            Write-Msg "In-place stream attempt $i failed: $_. Trying file replacement fallback..." "Yellow"
        }

        # Method 2: Atomic temp file replacement fallback
        try {
            [UniversalAsarEngine]::InjectPreload($sourceAsar, $tempPatched, $patchSnippet) | Out-Null
            Copy-Item -Path $tempPatched -Destination $originalAsar -Force
            $patchedOk = $true
            break
        } catch {
            Write-Msg "Attempt $i/$maxRetries to replace ASAR failed (file busy). Retrying..." "Yellow"
            Start-Sleep -Milliseconds (300 * $i)
        }
    }

    if (Test-Path $tempPatched) { Remove-Item -Path $tempPatched -Force -ErrorAction SilentlyContinue }

    if (-not $patchedOk) {
        Write-Error "Failed to patch ASAR file."
    }

    Write-Msg "ASAR file successfully patched in-place!" "Green"

    # Step 4: Setup Auto-Healing Daemon
    Set-DaemonState "enable"

    Write-Msg ""
    Write-Msg "==========================================================" "Cyan"
    Write-Msg ("     [+] "+([char]0x6c49)+([char]0x5316)+([char]0x8865)+([char]0x4e01)+([char]0x5b89)+([char]0x88c5)+([char]0x6210)+([char]0x529f)+([char]0xff01)+"(Patch Successfully Installed) ") "Green"
    Write-Msg "==========================================================" "Cyan"
    Write-Msg ("  [*] "+([char]0x96f6)+([char]0x8fdb)+([char]0x7a0b)+([char]0x4e2d)+([char]0x65ad)+([char]0x5b8c)+([char]0x6210)+([char]0x6c49)+([char]0x5316)+([char]0xff0c)+([char]0x5df2)+([char]0x5f00)+([char]0x542f)+([char]0x5b98)+([char]0x65b9)+([char]0x66f4)+([char]0x65b0)+([char]0x81ea)+([char]0x52a8)+([char]0x8ddf)+([char]0x968f)+([char]0x5b88)+([char]0x62a4)+([char]0xff01)) "Yellow"
    Write-Msg ("  [*] "+([char]0x5237)+([char]0x65b0)+([char]0x754c)+([char]0x9762)+" (Ctrl+R) "+([char]0x6216)+([char]0x91cd)+([char]0x542f)+" Antigravity "+([char]0x5373)+([char]0x53ef)+([char]0x67e5)+([char]0x770b)+([char]0x5b8c)+([char]0x6574)+([char]0x6c49)+([char]0x5316)+([char]0x3002)) "Green"
    Write-Msg "==========================================================" "Cyan"
}

# 11. Parameter Routing Dispatcher
if ($Check) {
    $res = Invoke-CheckDiagnostics
    if ($Json) {
        Write-Output $res
        $isHealthy = ($res -match 'healthy.*true')
        if ($isHealthy) { exit 0 } else { exit 1 }
    } else {
        exit $res
    }
}

if ($Restore) {
    Invoke-RestoreBackup
    exit 0
}

if ($Uninstall) {
    Invoke-UninstallPatch
    exit 0
}

if ($DaemonOn -or ($Daemon -eq 'enable')) {
    Set-DaemonState 'enable'
    exit 0
}

if ($DaemonOff -or ($Daemon -eq 'disable')) {
    Set-DaemonState 'disable'
    exit 0
}

if ($Daemon -eq 'status') {
    $st = Set-DaemonState 'status'
    if ($st) { exit 0 } else { exit 1 }
}

# Default action: Install
Invoke-InstallPatch
