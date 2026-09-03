param(
    [Parameter(Mandatory=$false)][switch]$RegisterTask,
    [Parameter(Mandatory=$false)][switch]$UnregisterTask,
    [Parameter(Mandatory=$false)][switch]$InstallDaemon,
    [Parameter(Mandatory=$false)][switch]$RemoveDaemon,
    [Parameter(Mandatory=$false)][switch]$DaemonOn,
    [Parameter(Mandatory=$false)][switch]$DaemonOff,
    [Parameter(Mandatory=$false)][ValidateSet("enable", "disable", "status", "")][string]$Daemon = "",
    [Parameter(Mandatory=$false)][switch]$Status,
    [Parameter(Mandatory=$false)][switch]$RunOnce,
    [Parameter(Mandatory=$false)][switch]$Check,
    [Parameter(Mandatory=$false)][string]$Path,
    [Parameter(Mandatory=$false)][switch]$Quiet
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "SilentlyContinue"

# 1. Constants and Cache Paths
$cacheDir = Join-Path $env:APPDATA "AntigravityChinesePatch"
$cachedPreload = Join-Path $cacheDir "preload.js"
$cachedWatcher = Join-Path $cacheDir "watcher.ps1"
$logFile = Join-Path $cacheDir "watcher.log"
$taskName = "AntigravityChinesePatchWatcher"
$regRunKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$regRunName = "AntigravityChinesePatchAutoHeal"
$patchMarker = "// Antigravity Chinese Localization Patch"

Function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
    $logLine = "[$timestamp] [$Level] $Message"
    if (-not $Quiet) {
        switch ($Level) {
            "ERROR" { Write-Host $logLine -ForegroundColor Red }
            "WARN"  { Write-Host $logLine -ForegroundColor Yellow }
            "SUCCESS" { Write-Host $logLine -ForegroundColor Green }
            default { Write-Host $logLine -ForegroundColor Gray }
        }
    }
    try {
        if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null }
        Add-Content -Path $logFile -Value $logLine -Encoding UTF8 -ErrorAction SilentlyContinue
    } catch {}
}

# 2. Smart Path Finder
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

# 3. In-Memory High-Performance C# ASAR Engine Compilation
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
            return "Unknown";
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
} catch {
    Write-Log "Failed to compile UniversalAsarEngine: $_" "WARN"
}

# 4. Resolve Local Patch Code
Function Get-PatchCode {
    # Priority 1: Cached preload.js in AppData
    if (Test-Path $cachedPreload) {
        $content = Get-Content -Path $cachedPreload -Raw -Encoding UTF8
        $idx = $content.IndexOf($patchMarker)
        if ($idx -ge 0) { return $content.Substring($idx) }
        return $content
    }

    # Priority 2: Local repository / script dist\preload.js
    $scriptRoot = $PSScriptRoot
    if (-not $scriptRoot) { $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path }
    if ($scriptRoot) {
        $localDistPreload = Join-Path (Split-Path -Parent $scriptRoot) "dist\preload.js"
        if (Test-Path $localDistPreload) {
            $content = Get-Content -Path $localDistPreload -Raw -Encoding UTF8
            $idx = $content.IndexOf($patchMarker)
            if ($idx -ge 0) { return $content.Substring($idx) }
            return $content
        }
        $directPreload = Join-Path $scriptRoot "dist\preload.js"
        if (Test-Path $directPreload) {
            $content = Get-Content -Path $directPreload -Raw -Encoding UTF8
            $idx = $content.IndexOf($patchMarker)
            if ($idx -ge 0) { return $content.Substring($idx) }
            return $content
        }
    }
    return $null
}

# 5. Core Test-And-Patch Logic (High Speed, Zero Disruption, Retry Backoff)
Function Test-And-Patch {
    param([string]$targetAsarPath)

    if (-not $targetAsarPath -or -not (Test-Path $targetAsarPath)) { return $false }

    # Debounce for NSIS file write completion
    Start-Sleep -Milliseconds 600

    if (-not (Test-Path $targetAsarPath)) { return $false }

    $isPatched = $false
    try {
        if (Select-String -Path $targetAsarPath -Pattern $patchMarker -Quiet) {
            $isPatched = $true
        }
    } catch {}

    if ($isPatched) {
        Write-Log "Target ASAR is already patched ($targetAsarPath)." "DEBUG"
        return $true
    }

    Write-Log "Unpatched official Google release detected at '$targetAsarPath'! Auto-healing..." "WARN"

    $patchCode = Get-PatchCode
    if (-not $patchCode) {
        Write-Log "Error: Local patch code not found in cache or script directory." "ERROR"
        return $false
    }

    # In-place injection into temp file, then atomic replacement
    $tempPatched = "$targetAsarPath.autoheal.tmp"
    $maxRetries = 5
    $applied = $false

    for ($i = 1; $i -le $maxRetries; $i++) {
        # Strategy 1: Direct in-place file stream write (bypasses Windows directory delete/rename locks while app is open)
        try {
            $applied = [UniversalAsarEngine]::InjectPreloadInPlace($targetAsarPath, $patchCode)
            if ($applied) {
                Write-Log "Auto-healing successfully applied in-place to '$targetAsarPath' (<50ms)!" "SUCCESS"
                break
            }
        } catch {
            Write-Log "In-place stream write attempt $i failed: $_. Retrying with temp file replacement..." "DEBUG"
        }

        # Strategy 2: Atomic temp file replacement fallback
        try {
            [UniversalAsarEngine]::InjectPreload($targetAsarPath, $tempPatched, $patchCode) | Out-Null
            Move-Item -Path $tempPatched -Destination $targetAsarPath -Force
            Write-Log "Auto-healing successfully applied via file replacement to '$targetAsarPath' (<50ms)!" "SUCCESS"
            $applied = $true
            break
        } catch {
            Write-Log "Attempt $i/$maxRetries to replace ASAR failed: $_" "WARN"
            Start-Sleep -Milliseconds (250 * $i)
        }
    }

    if (Test-Path $tempPatched) {
        Remove-Item -Path $tempPatched -Force -ErrorAction SilentlyContinue
    }

    return $applied
}

# 6. Daemon / Scheduled Task Management
Function Register-WatcherTask {
    Write-Log "Registering Windows Scheduled Task '$taskName'..." "INFO"
    
    # Ensure cache directory and cached script exist
    if (-not (Test-Path $cacheDir)) { New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null }
    
    $scriptSource = $MyInvocation.MyCommand.Path
    if ($scriptSource -and (Test-Path $scriptSource) -and ($scriptSource -ne $cachedWatcher)) {
        Copy-Item -Path $scriptSource -Destination $cachedWatcher -Force
    }

    try {
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$cachedWatcher`""
        $trigger = New-ScheduledTaskTrigger -AtLogOn
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0 -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
        
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
        
        # Also set HKCU Run as secondary persistence hook
        Set-ItemProperty -Path $regRunKey -Name $regRunName -Value "powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$cachedWatcher`"" -ErrorAction SilentlyContinue
        
        Write-Log "Scheduled Task '$taskName' and HKCU Run hook successfully enabled!" "SUCCESS"
    } catch {
        Write-Log "Notice during scheduled task registration: $_" "WARN"
        Set-ItemProperty -Path $regRunKey -Name $regRunName -Value "powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$cachedWatcher`"" -ErrorAction SilentlyContinue
    }

    # Immediately spawn active background watcher process if not currently running
    try {
        $runningWatcher = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { 
            ($_.CommandLine -like "*$cachedWatcher*" -or $_.CommandLine -like "*watcher.ps1*") -and $_.ProcessId -ne $PID 
        }
        if (-not $runningWatcher) {
            Start-Process -FilePath "powershell.exe" -ArgumentList "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File `"$cachedWatcher`"" -WindowStyle Hidden
            Write-Log "Background auto-healing watcher process spawned successfully!" "SUCCESS"
        } else {
            Write-Log "Background auto-healing watcher is already actively running." "INFO"
        }
    } catch {
        Write-Log "Notice: Could not spawn immediate background process: $_" "WARN"
    }
    return $true
}

Function Unregister-WatcherTask {
    Write-Log "Unregistering Windows Scheduled Task '$taskName'..." "INFO"
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $regRunKey -Name $regRunName -ErrorAction SilentlyContinue
        Write-Log "Scheduled Task and HKCU Run hook successfully removed." "SUCCESS"
        return $true
    } catch {
        Write-Log "Error during unregistration: $_" "WARN"
        return $false
    }
}

Function Get-DaemonStatus {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    $runVal = (Get-ItemProperty -Path $regRunKey -ErrorAction SilentlyContinue).$regRunName
    
    $isTaskRegistered = ($null -ne $task)
    $isRunRegistered = ($null -ne $runVal)
    
    $statusObj = @{
        TaskRegistered = $isTaskRegistered
        TaskState      = if ($task) { $task.State.ToString() } else { "None" }
        RunHookEnabled = $isRunRegistered
        DaemonActive   = ($isTaskRegistered -or $isRunRegistered)
    }

    $taskColor = if ($isTaskRegistered) { "Green" } else { "Gray" }
    $runColor = if ($isRunRegistered) { "Green" } else { "Gray" }
    $activeColor = if ($statusObj.DaemonActive) { "Green" } else { "Yellow" }
    $taskText = if ($isTaskRegistered) { "Registered (" + $task.State + ")" } else { "Not Registered" }
    $runText = if ($isRunRegistered) { "Enabled" } else { "Disabled" }
    $activeText = if ($statusObj.DaemonActive) { "ENABLED" } else { "DISABLED" }

    if (-not $Quiet) {
        Write-Host "Auto-Healing Daemon Status:" -ForegroundColor Cyan
        Write-Host "  - Scheduled Task ($taskName): $taskText" -ForegroundColor $taskColor
        Write-Host "  - HKCU Run Hook: $runText" -ForegroundColor $runColor
        Write-Host "  - Overall Status: $activeText" -ForegroundColor $activeColor
    }
    return $statusObj
}

# 7. Real-Time FileSystemWatcher Service Loop
Function Start-WatcherService {
    $progDir = Find-AntigravityPath
    if (-not $progDir) {
        Write-Log "Antigravity installation not found. Exiting watcher loop." "WARN"
        return
    }

    $resourcesDir = Join-Path $progDir "resources"
    $targetAsar = Join-Path $resourcesDir "app.asar"
    $pendingUpdateDir = "$env:LOCALAPPDATA\antigravity-updater\pending"

    Write-Log "Starting Real-Time FileSystemWatcher on '$resourcesDir'..." "INFO"

    # Initial check on startup
    Test-And-Patch -targetAsarPath $targetAsar

    # Watch resources folder for app.asar changes
    $fswResources = New-Object System.IO.FileSystemWatcher
    $fswResources.Path = $resourcesDir
    $fswResources.Filter = "*.*"
    $fswResources.IncludeSubdirectories = $false
    $fswResources.EnableRaisingEvents = $true

    $actionBlock = {
        param($source, $eventArgs)
        $changedPath = $eventArgs.FullPath
        if ($changedPath -like "*app.asar*") {
            Test-And-Patch -targetAsarPath $changedPath
        }
    }

    Register-ObjectEvent -InputObject $fswResources -EventName "Changed" -Action $actionBlock | Out-Null
    Register-ObjectEvent -InputObject $fswResources -EventName "Created" -Action $actionBlock | Out-Null
    Register-ObjectEvent -InputObject $fswResources -EventName "Renamed" -Action $actionBlock | Out-Null

    # Watch pending updater directory if exists or created
    if (Test-Path $pendingUpdateDir) {
        try {
            $fswUpdater = New-Object System.IO.FileSystemWatcher
            $fswUpdater.Path = $pendingUpdateDir
            $fswUpdater.Filter = "*.*"
            $fswUpdater.EnableRaisingEvents = $true
            Register-ObjectEvent -InputObject $fswUpdater -EventName "Created" -Action {
                Start-Sleep -Seconds 1
                Test-And-Patch -targetAsarPath $targetAsar
            } | Out-Null
        } catch {}
    }

    Write-Log "Watcher active and monitoring. Entering background heartbeat loop..." "SUCCESS"

    # Heartbeat loop: periodic check every 30 minutes with ultra-low CPU impact
    while ($true) {
        Start-Sleep -Seconds 1800
        Test-And-Patch -targetAsarPath $targetAsar
    }
}

# 8. Command Dispatcher
if ($RegisterTask -or $InstallDaemon -or $DaemonOn -or ($Daemon -eq "enable")) {
    Register-WatcherTask
    exit 0
}

if ($UnregisterTask -or $RemoveDaemon -or $DaemonOff -or ($Daemon -eq "disable")) {
    Unregister-WatcherTask
    exit 0
}

if ($Status -or ($Daemon -eq "status")) {
    Get-DaemonStatus
    exit 0
}

if ($RunOnce -or $Check) {
    $progDir = Find-AntigravityPath
    if ($progDir) {
        $res = Test-And-Patch -targetAsarPath (Join-Path $progDir "resources\app.asar")
        if ($res) { exit 0 } else { exit 1 }
    }
    exit 1
}

# Default execution: run real-time background watcher
Start-WatcherService
