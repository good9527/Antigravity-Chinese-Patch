## 2026-09-01T11:57:53Z
You are the E2E Test Suite Architect and Writer for the Antigravity Chinese Patch project.

Your working directory is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_test_writer_e2e_suite
Project root is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch

MANDATORY FIRST STEP: Read C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\ORIGINAL_REQUEST.md and C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\PROJECT.md before doing anything else.

Your Task:
Design and build the comprehensive, requirement-driven, opaque-box E2E test suite in the `tests/` directory:
1. `tests/test_runner.py`: Main test CLI runner supporting `--tier [1-4|all]`, verbose output, failure diagnostics, and summary statistics.
2. `tests/test_engine.py`: Tier 1 (Feature Coverage >=5 per feature) and Tier 2 (Boundary & Corner cases) testing:
   - Dynamic DOM translation (mocking DOM nodes / strings).
   - Dictionary completeness & 100% pure UTF-8 / Unicode escape validity (no typos like "已修政", 400+ keys).
   - Dynamic regex matchers: float timestamps (`Thinking for 1.2s`, `Working for 3.4s`, `Done in 12.3s`, `500ms`, `Thought for 1.2s`), relative timestamps (`10d`, `5m`, `1mo`, `2h`, `30s`, `1y`, `5 minutes ago`, `Today ...`, `Yesterday ...`), dynamic counters (`Subagents 0`, `Files Changed 3`, `N files changed`).
   - Safety bypass guards: verifying Monaco editor elements (`.monaco-editor`), `<pre><code>` code blocks, terminals, and `<textarea>`/`<input>` user typing values are NEVER translated.
   - Non-breaking space `\u00a0` normalization.
3. `tests/test_asar.py`: Tier 1 & Tier 2 tests for ASAR binary manipulation:
   - Header parsing, size/offset recalculation, in-place `dist/preload.js` extraction/injection.
   - Header integrity stripping, idempotency (re-running patch does not duplicate code).
   - Backup creation (`app.asar.bak`) and byte-exact restoration.
4. `tests/test_integration.py`: Tier 3 (Cross-Feature Combinations & Pairwise testing):
   - CLI flags (`--install`, `--check`, `--restore`, `--uninstall`, `--daemon`) in headless and quiet modes.
   - Multi-mirror CDN waterfall simulation with network timeouts and fallback verification.
5. `tests/test_scenarios.py`: Tier 4 (Real-World Application Scenarios):
   - Scenario 1: Fresh installation on unpatched client with active process non-locking.
   - Scenario 2: Simulated Google official auto-update (unpatched ASAR overwrite) -> Watcher detection and instant auto-healing.
   - Scenario 3: Corrupted patch recovery & one-click rollback to official Google binary.
   - Scenario 4: User typing and code review workflow with active agent state transitions.
6. Create `TEST_INFRA.md` at project root documenting test architecture, methodology, feature coverage matrix, and runner invocation.
7. Run the test suite against the repository to verify tests are executable (e.g. `python tests/test_runner.py`).
8. When ready, publish `TEST_READY.md` at project root with complete tier counts and feature checklist.
9. Write your handoff report to `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_test_writer_e2e_suite\handoff.md`.
10. Send a message to parent when completed.
