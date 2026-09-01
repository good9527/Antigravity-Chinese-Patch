## 2026-09-01T11:57:53Z
You are an Explorer agent investigating Safety Bypass & Sandbox Isolation for Milestone 1 (UI Localization Engine).

Your working directory is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_explorer_m1_engine_3
Project root is: C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch

MANDATORY FIRST STEP: Read C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\ORIGINAL_REQUEST.md and C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\PROJECT.md before doing anything else.

Your Task:
1. Investigate how to strictly prevent translation engine interference with code editors, terminal streams, and user typing inputs:
   - Monaco Editor bypass: `.monaco-editor`, `.view-lines`, `.monaco-list-row`, `.cm-content`, `.editor-instance`.
   - Markdown & Code fence bypass: `<pre>`, `<code>`, `.code-block`, `.hljs`, `pre code`.
   - Terminal bypass: `.terminal`, `.xterm`, `.xterm-screen`, `canvas`.
   - User Input protection: `<textarea>`, `<input type="text|search|password|email|url">` value attributes, `[contenteditable="true"]`. (Ensure ONLY `placeholder`, `title`, and `aria-label` attributes are translated on these elements, while their value/typed content is strictly untouched).
2. Design the exact AST/DOM node filter function and guard conditions for `walk(node)` and `MutationObserver`.
3. Design test verification cases for all bypass rules.
4. Write your detailed safety filter design and specifications to `C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch\.agents\teamwork_preview_explorer_m1_engine_3\handoff.md`.
5. Send a message to parent when completed.
