## 2026-09-01T12:02:30Z
You are the Implementation Worker for Milestone 1: UI Localization Engine Hardening (R1).

Your working directory is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_worker_m1_engine
Project root is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch

MANDATORY FIRST STEP: Read C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\ORIGINAL_REQUEST.md and C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\PROJECT.md before doing anything else.

Input Reports to Read and Follow:
1. `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_explorer_m1_engine_1\handoff.md` (and files `compiled_dictionary.json`, `compiled_dictionary_escaped.js`, `build_dictionary.py` in that directory)
2. `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_explorer_m1_engine_2\handoff.md`
3. `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_explorer_m1_engine_3\handoff.md`

Your Exclusive File Write Ownership:
- `dist/dictionary.json`
- `dist/preload.js`
- `dist/engine.js`

Your Implementation Tasks:
1. `dist/dictionary.json`:
   - Generate complete 514-key dictionary in clean standard UTF-8 JSON.
   - Verify zero typos (strictly replace all "已修政" with "已修改", "无法修政" with "无法修改", `\u653f` with `\u6539`).
   - Zero duplicate keys.
2. `dist/preload.js`:
   - Implement the complete localization engine appended to the host preload ContextBridge stubs.
   - Use pure ASCII Unicode escapes (`\uXXXX`) for all Chinese characters to ensure 100% immunity to Windows CP936/GBK/ANSI codepage corruptions.
   - Implement the complete dynamic pattern matcher pipeline (18 regex rules):
     - Float thinking timers (`Thinking for 1.2s`, `850ms`, `Thought for 1.2s`, `Thinking... 1.2s`, `Thinking (1.5s)`).
     - Float working timers (`Working for 3.4s`, `Worked for...`, `Working...`).
     - Completion timers (`Completed in 12.3s`, `Done in 0.8s`, `Timed 1.2s`, `Elapsed time: 3.5s`, `Total duration: 10.2s`).
     - Compact and verbose relative timestamps (`10d`, `5m`, `1mo`, `2h`, `30s`, `1y`, `5 minutes ago`, `2 days ago`, `1 month ago`, `10 mins ago`, `2 hrs ago`, `Just now`, `Today ...`, `Yesterday ...`).
     - Dynamic counters (`Subagents 0`, `Files Changed 3`, `N files changed/modified/added/deleted`, `N subagents`, `N agents running`).
   - Implement Shadow DOM penetration and monkey-patch `Element.prototype.attachShadow` to capture dynamically mounted web components.
   - Implement strict safety bypass filters:
     - Monaco Editor (`.monaco-editor`, `.view-lines`, `.monaco-list-row`, `.cm-content`, `.editor-instance`)
     - Markdown code fences & tags (`<pre>`, `<code>`, `<kbd>`, `<samp>`, `.code-block`, `.hljs`)
     - Terminal canvas and xterm streams (`.terminal`, `.xterm`, `.xterm-screen`, `canvas`)
     - User input values (`<textarea>`, `<input type="text|search|password|email|url">` value attributes, `[contenteditable="true"]`). Only `placeholder`, `title`, and `aria-label` attributes are translated. Button input values (`submit`, `button`, `reset`) are safely translated.
   - Implement non-breaking space normalization (`\u00a0` -> `\u0020`).
   - Implement `MutationObserver` with childList, characterData, and attribute filtering with loop prevention.
3. `dist/engine.js`:
   - Decoupled standalone translation engine exportable for Node.js, CLI testing, or decoupled loader stub.
4. Validation & Verification:
   - Run verification scripts on `dist/dictionary.json`, `dist/preload.js`, and `dist/engine.js` to ensure syntax validity, encoding purity, typo absence, and functionality.
   - Document commands executed and test results.
5. Write your handoff report to `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_worker_m1_engine\handoff.md`.
6. Send a message to parent when completed.
