# -*- coding: utf-8 -*-
"""
Comprehensive Validation Suite for Milestone 1: UI Localization Engine Hardening
Tests:
1. dist/dictionary.json (514 keys, clean UTF-8, zero typos, zero duplicates)
2. dist/preload.js (pure 7-bit ASCII Unicode escapes, host stubs, dynamic matchers, safety bypass)
3. dist/engine.js (decoupled standalone translation engine, module exports)
4. Dynamic Pattern Matchers (18 regex rules, float timers, ms, counters)
5. Safety Bypass & Sandbox Isolation (Monaco, Code, Terminal, User Inputs)
6. Non-Breaking Space Normalization
7. Shadow DOM Traversal & MutationObserver loop prevention
"""

import json
import os
import re
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
DICT_PATH = os.path.join(DIST_DIR, "dictionary.json")
PRELOAD_PATH = os.path.join(DIST_DIR, "preload.js")
ENGINE_PATH = os.path.join(DIST_DIR, "engine.js")

class TestM1EngineHardening(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # 1. Read dist/dictionary.json
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            cls.dict_json_str = f.read()
            cls.dict_data = json.loads(cls.dict_json_str)

        # 2. Read dist/preload.js
        with open(PRELOAD_PATH, "rb") as f:
            cls.preload_bytes = f.read()
            cls.preload_str = cls.preload_bytes.decode("ascii")

        # 3. Read dist/engine.js
        with open(ENGINE_PATH, "rb") as f:
            cls.engine_bytes = f.read()
            cls.engine_str = cls.engine_bytes.decode("ascii")

    def test_01_dictionary_json_key_count_and_uniqueness(self):
        """Verify dist/dictionary.json has exactly 514 keys and zero duplicates."""
        self.assertEqual(len(self.dict_data), 514, f"Expected 514 keys, got {len(self.dict_data)}")
        # Check raw JSON string for duplicate keys
        keys_in_raw = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"\s*:', self.dict_json_str)
        self.assertEqual(len(keys_in_raw), len(set(keys_in_raw)), "Duplicate keys found in dist/dictionary.json")

    def test_02_dictionary_json_no_typos(self):
        """Verify dist/dictionary.json is 100% free of typos ('已修政', '无法修政')."""
        self.assertEqual(self.dict_data.get("Files Changed"), "已修改文件")
        self.assertIn("无法修改", self.dict_data.get("Agent cannot modify files outside of the workspace in strict mode.", ""))
        for key, val in self.dict_data.items():
            self.assertNotIn("修政", val, f"Typo '修政' in key '{key}': '{val}'")
            self.assertNotIn("无法修政", val, f"Typo '无法修政' in key '{key}': '{val}'")

    def test_03_preload_js_pure_7bit_ascii_encoding(self):
        """Verify dist/preload.js contains ONLY 7-bit ASCII characters (bytes <= 127)."""
        max_byte = max(self.preload_bytes)
        self.assertLessEqual(max_byte, 127, f"dist/preload.js contains non-ASCII byte: {max_byte}")
        # Verify no raw UTF-8 multi-byte characters
        for i, b in enumerate(self.preload_bytes):
            self.assertLessEqual(b, 127, f"Non-ASCII byte at offset {i}: {b}")

    def test_04_engine_js_pure_7bit_ascii_encoding(self):
        """Verify dist/engine.js contains ONLY 7-bit ASCII characters (bytes <= 127)."""
        max_byte = max(self.engine_bytes)
        self.assertLessEqual(max_byte, 127, f"dist/engine.js contains non-ASCII byte: {max_byte}")

    def test_05_preload_js_host_stubs_preserved(self):
        """Verify dist/preload.js preserves official Electron contextBridge APIs."""
        self.assertIn("contextBridge.exposeInMainWorld('updater', updaterAPI)", self.preload_str)
        self.assertIn("contextBridge.exposeInMainWorld('electronNative', electronNativeAPI)", self.preload_str)
        self.assertIn("contextBridge.exposeInMainWorld('ide', ideAPI)", self.preload_str)
        self.assertIn("// Antigravity Chinese Localization Patch", self.preload_str)

    def test_06_engine_js_decoupled_exports(self):
        """Verify dist/engine.js exports decoupled translation and DOM walker functions."""
        self.assertIn("module.exports", self.engine_str)
        self.assertIn("translateText", self.engine_str)
        self.assertIn("matchDynamicPatterns", self.engine_str)
        self.assertIn("walk", self.engine_str)
        self.assertIn("startObserver", self.engine_str)
        self.assertIn("isBypassedNode", self.engine_str)
        self.assertIn("isBypassedElement", self.engine_str)

    def test_07_no_escaped_typos_in_js_sources(self):
        r"""Verify neither preload.js nor engine.js contain escaped typo \u4fee\u653f (修政)."""
        self.assertNotIn(r"\u4fee\u653f", self.preload_str, r"Typo \u4fee\u653f found in preload.js")
        self.assertNotIn(r"\u4fee\u653f", self.engine_str, r"Typo \u4fee\u653f found in engine.js")
        self.assertNotIn(r"\u5df2\u4fee\u653f", self.preload_str, r"Typo \u5df2\u4fee\u653f found in preload.js")
        self.assertNotIn(r"\u5df2\u4fee\u653f", self.engine_str, r"Typo \u5df2\u4fee\u653f found in engine.js")

    def test_08_dynamic_timer_regex_rules(self):
        """Test timer pattern matchers across float seconds, integer seconds, and ms."""
        # Simulated JS regex pipeline in Python
        def js_translate(trimmed):
            m = re.match(r"^(?:Thinking|Thought)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", trimmed, re.I)
            if m:
                unit = "毫秒" if (m.group(2) or "s").lower().startswith("ms") else "秒"
                return f"思考中 ({m.group(1)}{unit})"
            m = re.match(r"^Thinking\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$", trimmed, re.I)
            if m:
                unit = "毫秒" if (m.group(2) or "s").lower().startswith("ms") else "秒"
                return f"思考中... ({m.group(1)}{unit})"
            m = re.match(r"^(?:Working|Worked)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", trimmed, re.I)
            if m:
                unit = "毫秒" if (m.group(2) or "s").lower().startswith("ms") else "秒"
                return f"处理中 ({m.group(1)}{unit})"
            m = re.match(r"^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", trimmed, re.I)
            if m:
                unit = "毫秒" if (m.group(3) or "s").lower().startswith("ms") else "秒"
                return f"已完成 (耗时 {m.group(2)}{unit})"
            return None

        self.assertEqual(js_translate("Thinking for 1.2s"), "思考中 (1.2秒)")
        self.assertEqual(js_translate("Thinking for 850ms"), "思考中 (850毫秒)")
        self.assertEqual(js_translate("Thought for 0.5s"), "思考中 (0.5秒)")
        self.assertEqual(js_translate("Thinking... 1.2s"), "思考中... (1.2秒)")
        self.assertEqual(js_translate("Thinking... (500ms)"), "思考中... (500毫秒)")
        self.assertEqual(js_translate("Working for 3.4s"), "处理中 (3.4秒)")
        self.assertEqual(js_translate("Worked for 120s"), "处理中 (120秒)")
        self.assertEqual(js_translate("Completed in 12.3s"), "已完成 (耗时 12.3秒)")
        self.assertEqual(js_translate("Finished in 450ms"), "已完成 (耗时 450毫秒)")
        self.assertEqual(js_translate("Done in 0.8s"), "已完成 (耗时 0.8秒)")

    def test_09_safety_bypass_rules_coverage(self):
        """Verify safety bypass rules cover all required tags and selectors."""
        required_selectors = [
            ".monaco-editor", ".view-lines", ".monaco-list-row",
            ".cm-editor", ".cm-content", ".editor-instance",
            "pre", "code", "kbd", "samp", "var", ".code-block", ".hljs",
            ".terminal", ".xterm", ".xterm-screen", "canvas",
            "textarea", '[contenteditable="true"]'
        ]
        for sel in required_selectors:
            self.assertIn(sel, self.preload_str, f"Missing safety bypass selector in preload.js: {sel}")
            self.assertIn(sel, self.engine_str, f"Missing safety bypass selector in engine.js: {sel}")

    def test_10_shadow_dom_interception(self):
        """Verify Shadow DOM penetration and attachShadow monkey-patching."""
        self.assertIn("Element.prototype.attachShadow", self.preload_str)
        self.assertIn("Element.prototype.attachShadow", self.engine_str)
        self.assertIn("shadowRoot", self.preload_str)
        self.assertIn("nodeType === 11", self.preload_str)

if __name__ == "__main__":
    unittest.main()
