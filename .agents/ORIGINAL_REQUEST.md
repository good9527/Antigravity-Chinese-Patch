# Original User Request

## 2026-09-01T11:51:12Z

Build a permanent, self-healing, zero-maintenance localization system for Google Antigravity that persists across background auto-updates (Electron updater), supports multi-platform deployment, and provides complete Chinese UI coverage.

Working directory: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch

## Requirements

### R1. Complete & Robust UI Localization Engine
Deliver a pure UTF-8 dynamic DOM translation engine that intercepts and translates all Antigravity UI components (navigation, auxiliary panes, relative timestamps, dialogs, settings, model quotas, and status notifications) with zero encoding corruption.

### R2. Auto-Update Interception & Self-Healing Architecture
Ensure the localization survives background Google updates (e.g. v2.10.0 -> v2.11.0 -> future versions) by implementing multi-tiered persistence:
- Real-time file system watcher / daemon for instant post-update re-injection.
- Safe updater hooking to prevent unpatched overwrites or re-patch immediately post-extraction.
- Cross-version resilience that extracts and patches host `preload.js` dynamically without binary conflicts.

### R3. One-Click Universal Deployment & Maintenance Toolkit
Provide zero-dependency Windows, macOS, and Linux installers with CDN mirror acceleration, automated health checks, one-click backup/restore, and GitHub Actions CI.

## Acceptance Criteria

### Localization Coverage & Stability
- [ ] 100% of standard navigation items, panes, settings, and modal dialogs are rendered in accurate Chinese.
- [ ] Dynamic relative timestamps (`10d`, `5m`, `1mo`), task counters (`Subagents 0`, `Files Changed 3`), and thinking states (`Thinking for 1.2s`) are properly formatted in Chinese.
- [ ] No encoding glitches (100% pure UTF-8 across all operating system codepages).

### Update Persistence & Auto-Healing
- [ ] When Google's `electron-updater` downloads and installs a new official release (e.g., v2.11.0+), the patch automatically re-applies without user intervention.
- [ ] The patch never kills the active agent process or disrupts the running session during installation.
- [ ] One-click rollback restores official Google binaries cleanly.
