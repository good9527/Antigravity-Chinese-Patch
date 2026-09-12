# Project: Antigravity Chinese Patch

## Architecture

The **Antigravity Chinese Patch** is a permanent, self-healing, zero-maintenance localization system for Google Antigravity (Electron architecture).

```
+---------------------------------------------------------------------------------------------------+
|                                  ANTIGRAVITY CHINESE PATCH ARCHITECTURE                           |
+---------------------------------------------------------------------------------------------------+
                                                  |
           +--------------------------------------+--------------------------------------+
           |                                      |                                      |
           v                                      v                                      v
+-----------------------+              +-----------------------+              +-----------------------+
|  R1. UI LOCALIZATION  |              |   R2. AUTO-UPDATE     |              |   R3. UNIVERSAL CLI   |
|        ENGINE         |              |     SELF-HEALING      |              |   & TOOLKIT ENGINE    |
+-----------------------+              +-----------------------+              +-----------------------+
| - MutationObserver    |              | - Tier A: FS Watcher  |              | - install.ps1 (.NET)  |
| - 514 Dict Mappings   |              |   Daemon (Win/Mac/Lin)|              | - install.sh (Python) |
| - Dynamic Timers      |              | - Tier B: Launch Hook |              | - patch_antigravity.ps1|
| - Counters & States   |              | - Tier C: In-Place    |              | - Multi-CDN Waterfall |
| - Monaco/Code Bypass  |              |   ASAR Preload Stub   |              | - Health Diagnostics  |
| - Pure ASCII Escapes  |              | - Offline Cache       |              | - Backup & Rollback   |
| - Shadow DOM Traversal|              | - Zero Disruption     |              | - GitHub Actions CI   |
+-----------------------+              +-----------------------+              +-----------------------+
```

## Feature Inventory

Every feature from the Phase 0 Survey is inventoried below and mapped to a milestone.

| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| F01 | Primary Navigation Items | Translates core sidebar items: New Conversation, History, Scheduled Tasks, Projects, Settings | M1 | survey | DONE |
| F02 | Conversation Management | Translates conversation actions: Untitled, Close, Cancel, Save, Delete, Rename, Pin, Collapse All | M1 | survey | DONE |
| F03 | Auxiliary Panes Headers | Translates pane tabs: Subagents, Files Changed, Artifacts, Uploads, Background Tasks, MCP Servers | M1 | survey | DONE |
| F04 | Dynamic Counter Badges | Regex pattern matches pane labels with counts: `(Subagents\|Files Changed\|Artifacts...) \d+` | M1 | survey | DONE |
| F05 | File Change Counter | Regex pattern matches file change counter: `(\d+)\s+files?\s+changed` $\rightarrow$ `$1 个文件已修改` | M1 | survey | DONE |
| F06 | Relative Timestamps (Compact) | Matches relative time: `(\d+)\s*(mo\|d\|m\|h\|s\|y)` $\rightarrow$ `$1天前`, `$1分钟前`, `$1个月前` | M1 | survey | DONE |
| F07 | Relative Timestamps (Suffixed) | Matches relative time with "ago": `(\d+)\s*(days?\|hours?\|minutes?\|seconds?)\s+ago` | M1 | survey | DONE |
| F08 | Date Header Prefixes | Matches date prefixes: `Today ...`, `Yesterday ...` $\rightarrow$ `今天 ...`, `昨天 ...` | M1 | survey | DONE |
| F09 | Live Thinking Timer State | Regex matches active thinking timer: `Thinking for (\d+(?:\.\d+)?)\s*(s\|seconds?\|ms)?` | M1 | survey | DONE |
| F10 | Live Working Timer State | Regex matches active working timer: `Working for (\d+(?:\.\d+)?)\s*(s\|seconds?\|ms)?` | M1 | survey | DONE |
| F11 | Execution Completion Duration | Regex matches execution completion: `(Completed\|Finished\|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s\|ms)?` | M1 | survey | DONE |
| F12 | Static Agent Status Messages | Translates static agent states: Thinking..., Working..., Agent finished, Failed, Regenerate | M1 | survey | DONE |
| F13 | Review & Action Buttons | Translates review buttons: Review, Accept, Reject, Accept Step, Reject Step, Action Required, Apply | M1 | survey | DONE |
| F14 | Settings Modal Navigation | Translates settings categories: Account, Permissions, Appearance, Customizations, Updates | M1 | survey | DONE |
| F15 | Model Quota & Subscriptions | Translates quota displays: Your Plan: Google AI Ultra, Daily/Monthly Quota, Credits Balance | M1 | survey | DONE |
| F16 | Security & Execution Policies | Translates agent permissions: Sandbox policy, Terminal execution, File access, Network access | M1 | survey | DONE |
| F17 | Appearance & Theme Controls | Translates theme settings: Theme Mode, Follow System, Light/Dark, Font Size, Zoom Factor | M1 | survey | DONE |
| F18 | Feedback & Diagnostic Modal | Translates feedback modal: Bug Report, Feature Request, Auth & Billing, Steps to reproduce | M1 | survey | DONE |
| F19 | Input Placeholders & Tooltips | Translates `placeholder`, `title`, and `aria-label` attributes on DOM elements | M1 | survey | DONE |
| F20 | Application Menus | Translates top menu items: File, View, Window, Help, New Window, Docs, Check for Updates | M1 | survey | DONE |
| F21 | System Tray & Agent Count | Translates system tray tooltip and running agents counter: `N agents running` | M1 | survey | DONE |
| F22 | Splash & Onboarding Overlays | Translates loading overlay and IDE install wizard: Loading Antigravity, Setting up... | M1 | survey | DONE |
| F23 | Non-Breaking Space Normalizer | Replaces `\u00a0` with `\u0020` before dictionary matching | M1 | survey | DONE |
| F24 | Substring Replacement Pipeline | Targeted word replacements: Minimize, Maximize, Toggle Developer Tools, Turbo Mode, etc. | M1 | survey | DONE |
| F25 | Monaco Editor & Code Bypass | Enforces bypass rules for `.monaco-editor`, `<pre>`, `<code>`, `.hljs` to prevent code translation | M1 | survey | DONE |
| F26 | User Input Value Protection | Prevents translation of text inside `<textarea>`, `<input type="text">`, `[contenteditable]` | M1 | survey | DONE |
| F27 | In-Place ASAR Injection (.NET) | Dynamically parses ASAR binary header in C#, appends patch, recalculates offsets without CLI tools | M2 | survey | DONE |
| F28 | In-Place ASAR Injection (Python) | Dynamically parses ASAR header in Python 3, injects patch on macOS/Linux without node/npm | M2 | survey | DONE |
| F29 | ASAR Version Extractor | Reads `package.json` embedded inside ASAR to display active client version | M2 | survey | DONE |
| F30 | Real-Time Auto-Healing Daemon | Real-time `FileSystemWatcher` / daemon monitoring `app.asar` for instant re-injection post-update | M2 | survey | DONE |
| F31 | Safe Updater Hooking | Intercepts update lifecycle and enables offline self-healing without network calls | M2 | survey | DONE |
| F32 | Interactive Elite Console | Menu-driven console UI for Windows (`patch_antigravity.ps1`) | M3 | survey | DONE |
| F33 | Non-Interactive CLI Flags | Supports automated CLI flags: `--install`, `--uninstall`, `--check`, `--update`, `--daemon`, `--quiet` | M3 | survey | DONE |
| F34 | CDN Multi-Mirror Waterfall | Downloads latest patch assets from 4+ CDN mirrors with timeout and cache-busting | M3 | survey | DONE |
| F35 | One-Click Backup & Rollback | Creates `app.asar.bak` before first patch; restores official Google binary cleanly | M3 | survey | DONE |
| F36 | Multi-OS CI & Test Suite | Automated GitHub Actions CI workflow running multi-OS validation and packaging release zip | M3 | survey | DONE |

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | UI Localization Engine Hardening | F01–F26: 514 key dictionary, pure ASCII Unicode escapes, float timestamp regexes, Monaco/code/input safety bypass, Shadow DOM traversal, decoupled engine | none | DONE |
| M2 | Auto-Update Self-Healing & In-Place ASAR Engine | F27–F31: Real-time FileSystemWatcher daemon (Win/Mac/Linux), Scheduled Task / LaunchAgent / systemd unit, offline self-heal cache, zero session disruption in-place patcher | M1 | DONE |
| M3 | Universal Deployment Toolkit, Health Diagnostics & CI | F32–F36: Full CLI flag suite (`--install`, `--check`, `--restore`, `--uninstall`, `--daemon`), 4-tier CDN waterfall, diagnostic health check report, backup & rollback, GitHub Actions CI | M1, M2 | DONE |
| M4 | Final Milestone: Full E2E Verification & Adversarial Hardening | Pass 100% of E2E test suite (Tiers 1-4) from E2E Testing Track, then Tier 5 adversarial coverage hardening | M1, M2, M3 | DONE |

## Interface Contracts

### 1. Localization Engine (`dist/preload.js`, `dist/dictionary.json`, `dist/engine.js`)
- Export: Injected self-executing IIFE appended after host ContextBridge exports.
- Global signature: `// Antigravity Chinese Localization Patch` header marker.
- Dictionary: 514 key-value pairs formatted with pure ASCII Unicode escapes (`\uXXXX`) in JS and standard UTF-8 in JSON.
- Safety Bypass: Skips `script`, `style`, `noscript`, `textarea`, `code`, `pre`, `canvas`, `.monaco-editor`, `.view-lines`, `.monaco-list-row`, `.terminal`, `.xterm`, `.xterm-screen`, `.code-block`, `.hljs`, `[contenteditable="true"]`.

### 2. Patcher & Auto-Heal Engine (`UniversalAsarEngine`)
- Input: `app.asar` file path, patch script content string.
- Header parsing: 16-byte ASAR header, JSON decoding without external tools.
- Injection: Modifies `dist/preload.js` entry, strips old patch marker, appends new patch code, updates size & offset table, re-serializes ASAR archive.
- Atomicity: Writes to `app.asar.tmp` and performs atomic rename/copy with retry logic.
- Exit code / Exceptions: Returns 0 on success, throws descriptive exception on failure.

### 3. CLI & Installer Interface (`install.ps1`, `install.sh`, `patch_antigravity.ps1`)
- Flags:
  - `--install` / `-i`: Installs patch in-place, configures backup, enables auto-heal daemon.
  - `--uninstall` / `-u`: Restores clean `app.asar.bak`, deletes patcher configs, disables auto-heal daemon.
  - `--check` / `-c`: Diagnoses installation path, client version, ASAR patch status, backup presence, daemon health, CDN latency. Returns JSON or formatted text. Exit code 0 if healthy, 1 if unhealthy.
  - `--restore` / `-r`: Reverts `app.asar` to `app.asar.bak`.
  - `--daemon <enable|disable|status>`: Manages Tier A background watcher daemon.
  - `--quiet` / `-q`: Silent non-interactive mode.
  - `--path <dir>` / `-p <dir>`: Custom installation directory.

## Code Layout

```
Antigravity-Chinese-Patch/
├── dist/
│   ├── preload.js          # Injected localization engine (UTF-8 / Unicode escaped)
│   ├── dictionary.json     # Complete translation dictionary (514 keys)
│   └── engine.js           # Decoupled standalone runtime translation engine
├── watcher/
│   ├── watcher.ps1         # Windows real-time FileSystemWatcher & scheduled task script
│   ├── auto_heal.sh        # macOS / Linux background auto-healing script
│   ├── com.antigravity.chinese.patch.plist # macOS launchd LaunchAgent definition
│   ├── antigravity-patch.path              # Linux systemd user path unit
│   └── antigravity-patch.service           # Linux systemd user service unit
├── tests/
│   ├── test_runner.py          # E2E test suite runner & orchestrator (103 tests)
│   ├── test_engine.py          # Tier 1 & Tier 2 DOM translation & regex unit tests
│   ├── test_asar.py            # Tier 1 & Tier 2 ASAR parser & in-place patching tests
│   ├── test_integration.py     # Tier 3 cross-feature combination tests
│   ├── test_scenarios.py       # Tier 4 real-world workload & update persistence scenarios
│   ├── test_adversarial.py     # Adversarial stress suite
│   ├── test_adversarial_safety.py # Safety bypass stress suite
│   ├── test_tier5_adversarial.py  # Tier 5 white-box engine stress suite
│   ├── test_adversarial_tier5.py  # Tier 5 persistence & toolkit stress suite
│   └── run_browser_adversarial.py # Real Chromium Headless V8 browser test harness
├── .github/
│   └── workflows/
│       └── release.yml     # Multi-OS CI/CD workflow matrix
├── patch_antigravity.ps1   # Windows Elite management console
├── install.ps1             # Windows zero-dependency one-click installer
├── install.sh              # macOS / Linux zero-dependency installer
├── 安装汉化补丁.bat        # Windows UTF-8 double-click batch launcher
├── README.md               # User & developer documentation
├── ORIGINAL_REQUEST.md     # Immutable user requirements record
└── PROJECT.md              # Global project architecture and milestone index
```
