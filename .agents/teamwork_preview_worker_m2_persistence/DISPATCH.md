## 2026-09-01T12:12:52Z
You are the Implementation Worker for Milestone 2: Auto-Update Self-Healing & In-Place ASAR Engine (R2).

Your working directory is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_worker_m2_persistence
Project root is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch

MANDATORY FIRST STEP: Read C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\ORIGINAL_REQUEST.md and C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\PROJECT.md before doing anything else.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Reference Architecture to Read:
`C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_explorer_survey_persistence\handoff.md`

Your Exclusive File Write Ownership:
- `watcher/` (directory and all scripts inside)
  - `watcher/watcher.ps1`
  - `watcher/auto_heal.sh`
  - `watcher/com.antigravity.chinese.patch.plist`
  - `watcher/antigravity-patch.path`
  - `watcher/antigravity-patch.service`
- `patch_antigravity.ps1`
- `install.ps1`
- `install.sh`

Implementation Tasks:
1. `watcher/` Subsystem:
   - `watcher/watcher.ps1`: High-performance real-time Windows `FileSystemWatcher` and Scheduled Task registration. Listens to `resources\app.asar` and `%LOCALAPPDATA%\antigravity-updater\pending` for modifications and re-patches unpatched official Google releases in < 50ms using locally cached engine in `%APPDATA%\AntigravityChinesePatch\`.
   - `watcher/auto_heal.sh`: macOS / Linux background auto-healing script with local Python 3 patcher.
   - `watcher/com.antigravity.chinese.patch.plist`: macOS `launchd` LaunchAgent configuration using native `WatchPaths`.
   - `watcher/antigravity-patch.path` & `watcher/antigravity-patch.service`: Linux systemd user path and service units.
2. `install.ps1` & `patch_antigravity.ps1`:
   - Integrate local engine/payload offline caching into `%APPDATA%\AntigravityChinesePatch\` so auto-healing works 100% offline without CDN/internet dependency.
   - Implement `--daemon <enable|disable|status>` and `--daemon-on` / `--daemon-off` CLI commands.
   - Ensure zero session disruption (no `taskkill`, atomic file swap with retry backoff).
3. `install.sh`:
   - Remove any `killall -9` or process killing.
   - Ensure in-place non-disruptive ASAR patching via Python 3 with retry backoff.
   - Integrate macOS `launchd` / Linux `systemd` daemon installation.
4. Testing & Verification:
   - Run `python tests/test_runner.py --tier all`.
   - Run `python -m unittest tests/test_scenarios.py -v`.
   - Verify that simulated update overwrite instantly triggers auto-healing and rollback restores pristine binaries.
5. Write your handoff report to `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_worker_m2_persistence\handoff.md`.
6. Send a message to parent when completed.
