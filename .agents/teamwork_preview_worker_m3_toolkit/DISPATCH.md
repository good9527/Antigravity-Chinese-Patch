## 2026-09-01T12:26:01Z

You are the Implementation Worker for Milestone 3: Universal Deployment Toolkit, Health Diagnostics & CI (R3).

Your working directory is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_worker_m3_toolkit
Project root is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch

MANDATORY FIRST STEP: Read C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\ORIGINAL_REQUEST.md and C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\PROJECT.md before doing anything else.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Exclusive File Write Ownership:
- `.github/workflows/release.yml`
- `README.md`
- `安装汉化补丁.bat`

Implementation Tasks:
1. `.github/workflows/release.yml`:
   - Multi-OS test matrix across `ubuntu-latest`, `windows-latest`, `macos-latest`.
   - Runs automated validation tests (`python tests/test_runner.py --tier all`) on push to main, tags `v*`, and PRs.
   - Release packaging step: packages `dist/`, `watcher/`, `install.ps1`, `install.sh`, `patch_antigravity.ps1`, `安装汉化补丁.bat`, `README.md` into `Antigravity-Chinese-Patch-Elite.zip` with SHA256 checksum generation.
2. `README.md`:
   - Comprehensive, beautifully structured documentation in Chinese and English.
   - Documents the 3-Tier persistence architecture, real-time background watcher daemon, one-click online/offline installation, multi-CDN mirror acceleration, complete CLI flags (`--install`, `--uninstall`, `--check`, `--restore`, `--daemon <enable|disable|status>`, `--quiet`, `--json`), diagnostic health check report, and manual rollback.
   - Eliminates duplicate menu option numbering.
3. `安装汉化补丁.bat`:
   - Robust UTF-8 codepage enforcement (`chcp 65001 >nul`), execution policy bypass, and menu-driven launcher:
     1. 一键安装 / 更新汉化补丁 (In-place Hot Patch)
     2. 运行环境与健康状态诊断 (Health Diagnostics)
     3. 开启 / 关闭后台自动守护 (Toggle Auto-Heal Daemon)
     4. 一键恢复官方原版备份 (One-Click Rollback)
     5. 退出 (Exit)
4. Validation & Verification:
   - Validate YAML syntax of `.github/workflows/release.yml`.
   - Run `python tests/test_runner.py --tier all`.
5. Write your handoff report to `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_worker_m3_toolkit\handoff.md`.
6. Send a message to parent when completed.
