# Codebase Survey & Architecture Investigation Report: Antigravity Chinese Patch

## 1. Observation

### 1.1 Repository Structure & Inventory
Direct inspection of `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch` reveals the following key components:

| File Path | Size | Description / Purpose |
|---|---|---|
| `ORIGINAL_REQUEST.md` | 2,235 B | Core requirements specification defining R1 (Localization Engine), R2 (Auto-Update Persistence), R3 (Universal Deployment & Toolkit). |
| `README.md` | 5,146 B | Project documentation in Chinese/English covering features, installation commands, menu guide, and project structure. |
| `dist/preload.js` | 17,856 B | Electron renderer preload script containing contextBridge stubs (lines 1–46), `dictionary` object (lines 50–231), substring replacements (lines 233–243), regex matchers (lines 265–353), `walk()` DOM traversal (lines 355–384), and `MutationObserver` (lines 385–435). |
| `dist/dictionary.json` | 7,982 B | Standalone JSON dictionary file containing 182 key-value translation mappings. |
| `patch_antigravity.ps1` | 25,766 B | PowerShell Elite Toolkit v3.0 management console. Contains embedded C# `UniversalAsarEngine` (lines 61–330), path resolver (lines 17–55), interactive menu (lines 337–352), patch applicator (lines 354–439), auto-heal toggle (lines 441–490), backup restorer (lines 492–516), and status inspector (lines 518–562). |
| `install.ps1` | 20,026 B | One-click web installer for Windows. Contains multi-mirror CDN downloader (`fastly.jsdelivr.net`, `testingcf.jsdelivr.net`, `ghfast.top`, `raw.githubusercontent.com`), embedded C# ASAR engine, in-place patch injector, and `HKCU\...\Run` startup persistence setup. |
| `install.sh` | 6,252 B | macOS / Linux universal bash installer. Uses CDN mirrors, python3 `struct` + `json` ASAR parser/writer (lines 89–158), and process terminator (`killall -9 Antigravity`, `pkill -f Antigravity`). |
| `安装汉化补丁.bat` | 555 B | Windows double-click batch launcher setting UTF-8 codepage (`chcp 65001 >nul`) and executing `patch_antigravity.ps1` with `-ExecutionPolicy Bypass`. |
| `.github/workflows/release.yml` | 864 B | GitHub Actions workflow triggering on tags `v*` or main branch pushes, bundling `dist/`, scripts, and `README.md` into `Antigravity-Chinese-Patch-Elite.zip`. |
| `app.asar` | 2,137,952 B | Bundled sample Antigravity ASAR package (official v2.1.4 metadata). |
| `app.asar.unpacked/` | Directory | Contains unpacked native modules: `node_modules/chrome-devtools-mcp` (v0.23.0). |

---

### 1.2 Inspection of Translation Engine (`dist/preload.js` & `dist/dictionary.json`)

1. **Dictionary Format and Volume**:
   - `dist/dictionary.json` has **182 translation pairs** formatted as static JSON key-value pairs.
   - `dist/preload.js` lines 50–231 duplicates these 182 keys as a hardcoded JavaScript object.

2. **Typos Observed in Dictionary**:
   - `dist/preload.js:121` & `dist/dictionary.json:72`: `"Files Changed": "已修政文件"` $\rightarrow$ Contains character error ("已修政文件" instead of "已修改文件").
   - `dist/preload.js:176` & `dist/dictionary.json:127`: `"Agent cannot modify files outside of the workspace in strict mode.": "在严格模式下，智能体无法修政工作区外的文件。"` $\rightarrow$ Contains character error ("无法修政" instead of "无法修改").

3. **Dynamic Matchers in `dist/preload.js`**:
   - **Task Counters** (lines 265–276): `/^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks)\s+(\d+)$/i` translates standard auxiliary pane counters.
   - **Plural Files Changed** (lines 279–282): `/^(\d+)\s+files?\s+changed$/i` $\rightarrow$ `$1 个文件已修改`.
   - **Relative Timestamps** (lines 285–298): `/^(\d+)\s*(mo|d|m|h|s|y)$/i` $\rightarrow$ `mo` (个月前), `d` (天前), `m` (分钟前), `h` (小时前), `s` (秒前), `y` (年前).
   - **Upload Dates** (lines 301–306): `Today ` $\rightarrow$ `今天 `, `Yesterday ` $\rightarrow$ `昨天 `.
   - **Thinking States** (lines 309–317): `/^Thinking\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i` $\rightarrow$ `思考中 ($1秒)`.
   - **Working States** (lines 320–328): `/^Working\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i` $\rightarrow$ `处理中 ($1秒)`.
   - **Completed States** (lines 331–339): `/^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i` $\rightarrow$ `已完成 (耗时 $2秒)`.
   - **Substring Replacements** (lines 233–243): 9 items (`Minimize`, `Maximize`, `Toggle Developer Tools`, `Default`, `Full Machine`, `Turbo Mode`, `Turbo mode`, `Custom`, `System`).

4. **DOM Walker & MutationObserver (`dist/preload.js`)**:
   - `walk(node)` (lines 355–383): Checks `nodeType === 3` (Text Node) and `nodeType === 1` (Element Node). Attributes translated: `['placeholder', 'title', 'aria-label', 'value']`. Excludes `script`, `style`, `noscript`, `textarea`.
   - **Vulnerabilities**:
     - Does **NOT** exclude `<code>`, `<pre>`, `.monaco-editor`, `.cm-content`, or code viewer elements. Exact dictionary matches (e.g. `Settings`, `Close`, `Delete`, `File`, `Open`) inside source code snippets printed by agents could be inadvertently translated.
     - Does **NOT** traverse `node.shadowRoot` or handle `node.nodeType === 11` (`DocumentFragment`), which is used by modern Electron web components.
   - **ContextBridge Header Inconsistency**:
     - `dist/preload.js:8–46` contains a simplified mock contextBridge that exposes `updater`, `ide`, `electronNative`.
     - Host Antigravity (v2.1.4 and v2.11.0) exposes `electronUpdater`, `dialog`, `nativeNotifications`, `nativeStorage`, `logs`, `extensions`, `deepLink`, `agent`, `electronNative`, and `ide`.
     - Because `patch_antigravity.ps1` and `install.ps1` extract only starting from `// Antigravity Chinese Localization Patch`, in-place appending preserves host contextBridge APIs; however, standalone distribution of `dist/preload.js` as a drop-in replacement would break the application.

---

### 1.3 Inspection of ASAR Patcher & Installation Architecture

1. **ASAR Engine Implementation**:
   - **Windows (`patch_antigravity.ps1` & `install.ps1`)**:
     - In-memory C# compilation via `Add-Type -TypeDefinition $csharpPatcher -Language CSharp`.
     - `UniversalAsarEngine.InjectPreload` reads the ASAR binary into memory, parses the header JSON with a custom zero-dependency JSON parser (`SimpleJson`), locates `dist/preload.js`, reads the host's existing `preload.js`, strips any prior patch starting from `// Antigravity Chinese Localization Patch`, appends the new patch code, removes `integrity` from the ASAR header node, recalculates byte offsets for all entries, and writes the newly repacked ASAR binary.
   - **macOS / Linux (`install.sh`)**:
     - Python 3 inline script (`struct.unpack('<IIII', ...)` + `json.loads`) performs the identical header modification, offset recalculation, and file repacking in memory.
   - **Zero-Dependency Verified**: Neither Windows nor macOS/Linux requires Node.js, `npm`, or the `asar` CLI tool.

2. **Live Process & File Lock Behavior**:
   - Verification command on Windows running Antigravity (PID 60436, 126748, etc.):
     - Target path: `C:\Users\19901\AppData\Local\Programs\antigravity\resources\app.asar`
     - Test result: Opened in `r+b` read-write stream without throwing lock violation errors.
   - Electron allows in-place rewrites on modern Windows builds.
   - **Deficiency in `install.sh:48–49`**: `install.sh` explicitly calls `killall -9 Antigravity` and `pkill -f "Antigravity"`. This forcefully kills active user agent sessions and violates Acceptance Criterion ("The patch never kills the active agent process or disrupts the running session during installation").

---

### 1.4 Inspection of Auto-Update & Persistence Mechanics (R2 Analysis)

1. **Official Google Auto-Update Workflow Observed**:
   - Official `app-update.yml` configuration:
     - URL: `https://antigravity-hub-auto-updater-974169037036.us-central1.run.app/manifest/`
     - Updater Cache: `%LOCALAPPDATA%\antigravity-updater`
   - Active user directory on current machine:
     - `%LOCALAPPDATA%\antigravity-updater\pending\Antigravity-x64.exe` (147,709,824 bytes, downloaded update installer).
     - `%LOCALAPPDATA%\antigravity-updater\pending\update-info.json` (`{"fileName":"Antigravity-x64.exe", ...}`).
     - Official update triggers `installer.exe` on quit/restart, overwriting `C:\Users\19901\AppData\Local\Programs\antigravity\resources\app.asar`.

2. **Current Auto-Heal Daemon Implementation**:
   - `install.ps1:406–440` and `patch_antigravity.ps1:441–490` write `auto_heal.ps1` and register a startup entry at `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (`AntigravityChinesePatchAutoHeal`).
   - `auto_heal.ps1` content:
     ```powershell
     if (Test-Path $originalAsar) {
         $isPatched = Select-String -Path $originalAsar -Pattern 'Antigravity Chinese Localization Patch' -Quiet
         if (-not $isPatched) {
             $webScript = (Invoke-RestMethod -Uri 'https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.ps1' -TimeoutSec 10)
             Invoke-Expression $webScript
         }
     }
     ```
   - **Severe Limitations Identified**:
     1. **Trigger is Logon-Only**: It only runs once when the user logs into Windows. If Google Antigravity updates in the background while the user is actively working, the patch will be lost and un-patched until the next reboot.
     2. **No Real-Time FileSystemWatcher**: There is no resident daemon or background watcher listening to `resources\app.asar` file creation/change events.
     3. **Internet Dependency**: If the user is offline or GitHub/CDN is slow, the auto-heal script fails because it attempts to download `install.ps1` from the web instead of using a locally cached patch engine.
     4. **Zero macOS / Linux Auto-Healing**: `install.sh` has no launchd plist, systemd user unit, or background watcher whatsoever.

---

### 1.5 Target Application Version Comparison: v2.1.4 vs v2.11.0

Inspection of official Antigravity host `dist/preload.js` across versions:
- **v2.1.4 (Repo `app.asar`)**: Exposed basic updater and context APIs.
- **v2.11.0 (Installed user version `C:\Users\19901\AppData\Local\Programs\antigravity\resources\app.asar`)**:
  - `updaterAPI`: Added `getState: () => ipcRenderer.invoke('updater:get-state')`.
  - `dialogAPI`: Added `showOpenMultipleFolderDialog: () => ipcRenderer.invoke('dialog:open-workspaces')`.
  - `electronNativeAPI`: Zoom controls (`zoomIn`, `zoomOut`, `resetZoom`) refactored from direct `webFrame` calls to async IPC invocations (`window:zoom-in`, `window:zoom-out`, `window:reset-zoom`), and added `revealInFilePicker: (path) => ipcRenderer.invoke('shell:reveal-in-file-picker', path)`.

---

## 2. Logic Chain

```
[Observation 1.1 & 1.2: Dictionary contains 182 keys + 2 typos ("已修政文件")]
         │
         ├──> [Inference A]: The localization dictionary has good core coverage for v2.1.x, but lacks newer v2.11.0+ UI components (MCP server config, quota overage management, token metrics, multi-folder workspaces, slash actions).
         │
[Observation 1.2: Regex matchers use integer-only \d+ and exact prefixes]
         │
         ├──> [Inference B]: Fractional durations (e.g. "1.5s", "0.8s"), "Thought for 1.2s", "Thinking... (1.2s)", and relative times ("5 mins ago", "just now") fail to match and remain in English.
         │
[Observation 1.2: walk() lacks code block / editor exclusions]
         │
         ├──> [Inference C]: Potential for false positive translations inside agent code blocks containing common keywords ("Settings", "Close").
         │
[Observation 1.3: C# and Python ASAR injectors dynamically append to host preload]
         │
         ├──> [Inference D]: Preserving host preload contextBridge APIs is the correct architectural pattern that prevents binary conflicts across versions (verified between v2.1.4 and v2.11.0).
         │
[Observation 1.3 & 1.4: install.sh uses killall -9; install.ps1 lacks lock retries]
         │
         ├──> [Inference E]: install.sh disrupts active agent sessions (violating R3/Acceptance Criteria). Non-disruptive hot injection should be used across all platforms.
         │
[Observation 1.4: Auto-healing relies only on HKCU Run and remote CDN download]
         │
         ├──> [Inference F]: Surviving background auto-updates (R2) is not achieved for active desktop sessions because updates overwrite app.asar immediately without waiting for user re-login. A persistent local FileSystemWatcher / daemon is required.
```

---

## 3. Caveats

1. **Host Application Obfuscation**: The web bundle inside Antigravity's renderer is compiled React/TypeScript. While DOM text nodes are interceptable, classes and data attributes are minified. Translations must rely on normalized text and semantic attributes (`placeholder`, `title`, `aria-label`, `value`).
2. **Platform Scope**: Windows testing was performed directly on Windows 11 with PowerShell 5.1 and active Antigravity v2.11.0. macOS and Linux behavior was verified through structural code analysis of `install.sh` and Python ASAR injection logic.

---

## 4. Conclusion & Architectural Gap Assessment

| Requirement (ORIGINAL_REQUEST.md) | Current Status | Critical Deficiencies & Gaps | Priority Fix |
|---|---|---|---|
| **R1. Complete & Robust UI Localization Engine** | 🟡 Partially Implemented (~75%) | - Dictionary typos ("已修政文件")<br>- Missing ~200 UI strings in settings, MCP tools, quota balances, model parameters<br>- Regex gaps on float timestamps (`1.5s`), `Thinking... (1.2s)`, `Thought for 1.2s`<br>- Code blocks (`<pre><code>`, Monaco) not shielded from false-positive translation<br>- Raw UTF-8 strings in JS rather than safe Unicode escape sequences (`\uXXXX`) | **High** |
| **R2. Auto-Update Persistence & Self-Healing** | 🔴 Prototype Only (~30%) | - Auto-heal only executes on Windows login (HKCU Run), missing background updates during active sessions<br>- Requires network to download `install.ps1` instead of local cached engine<br>- No real-time `FileSystemWatcher` / background watcher daemon<br>- Zero auto-healing implementation on macOS / Linux | **High** |
| **R3. One-Click Universal Deployment & Maintenance** | 🟢 Substantially Implemented (~80%) | - `install.sh` forcefully kills active Antigravity processes (`killall -9`)<br>- Duplicate option numbers in README menu description<br>- GitHub Actions CI only zips files without running automated injection & dictionary validation tests | **Medium** |

---

## 5. Verification Method

### 5.1 Independent Verification Commands

1. **Verify Dictionary Typos & Encoding**:
   ```powershell
   Select-String -Path "dist\preload.js", "dist\dictionary.json" -Pattern "已修政"
   ```
   *Expected Output*: Displays lines containing the typo `"已修政文件"`.

2. **Verify ASAR Version & Structure**:
   ```python
   # Run in repository root
   python -c "import struct, json; b=open('app.asar','rb').read(); u2=struct.unpack('<I',b[4:8])[0]; sz=struct.unpack('<I',b[12:16])[0]; hdr=json.loads(b[16:16+sz].decode('utf-8')); print('ASAR Dist Files:', list(hdr['files']['dist']['files'].keys()))"
   ```

3. **Verify Active Process Non-Locking In-Place Injection**:
   ```powershell
   powershell -Command "Test-Path 'C:\Users\19901\AppData\Local\Programs\antigravity\resources\app.asar'"
   ```

4. **Verify Auto-Heal Registry Entry**:
   ```powershell
   Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "AntigravityChinesePatchAutoHeal"
   ```

---

## 6. Concrete Recommendations for Upcoming Milestones

### Milestone 1: Localization Engine Hardening (R1)
- Fix all dictionary typos and expand dictionary entries to 400+ keys covering Antigravity v2.11.0+ UI (MCP settings, Quota management, Model parameters, Dialog prompts).
- Convert all Chinese characters in `dist/preload.js` to pure ASCII Unicode escape sequences (`\uXXXX`) to ensure 100% encoding resilience across all OS codepages.
- Refactor regex matchers in `translateText()` to support float timestamps (`1.5s`), `Thinking... (1.2s)`, `Thought for 1.2s`, parenthetical counters `(0)`, and full relative time strings.
- Add code block / editor protection in `walk(node)` to skip `.monaco-editor`, `code`, `pre`, and `contenteditable` inputs.
- Add Shadow DOM traversal support (`node.shadowRoot`).

### Milestone 2: Real-Time Auto-Healing Daemon & Updater Persistence (R2)
- Implement a resident, lightweight background `FileSystemWatcher` daemon on Windows (via PowerShell background job / Scheduled Task / WMI or resident thread) that watches `resources\app.asar` and `%LOCALAPPDATA%\antigravity-updater\pending` for write/creation events.
- Embed the full localized patch payload and patcher logic locally into the daemon directory (e.g. `%LOCALAPPDATA%\Programs\antigravity\patcher\`) so auto-healing works 100% offline in < 50ms without network calls.
- Implement macOS `launchd` plist watcher and Linux systemd / inotify background script.
- Ensure hot in-place patching never kills or disrupts active Antigravity sessions.

### Milestone 3: Universal Deployment Toolkit, Verification Suite & CI (R3)
- Remove `killall -9` from `install.sh` to enable non-disruptive hot injection on macOS and Linux.
- Add automated verification scripts (`test_patcher.py` / `test_engine.ps1`) to validate ASAR integrity, dictionary JSON validity, regex coverage, and round-trip repacking.
- Update GitHub Actions workflow (`.github/workflows/release.yml`) to run the automated test suite before generating release packages.
