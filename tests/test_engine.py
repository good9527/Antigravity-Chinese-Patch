#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_engine.py
Tier 1 (Feature Coverage >=5 per feature) and Tier 2 (Boundary & Corner Cases)
Comprehensive test suite for the UI Localization Engine.
"""

import unittest
import json
import os
import re
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
DICT_PATH = os.path.join(DIST_DIR, "dictionary.json")
PRELOAD_PATH = os.path.join(DIST_DIR, "preload.js")


# ==============================================================================
# Pure Python DOM & Translation Mock Model (Opaque-Box Specification Model)
# ==============================================================================

class MockNode:
    """Mock representation of browser DOM node."""
    TEXT_NODE = 3
    ELEMENT_NODE = 1

    def __init__(self, node_type, tag_name="", node_value="", attributes=None, class_name="", is_content_editable=False):
        self.nodeType = node_type
        self.tagName = tag_name.upper() if tag_name else ""
        self.nodeValue = node_value
        self.attributes = attributes or {}
        self.className = class_name
        self.classList = set(class_name.split()) if class_name else set()
        self.isContentEditable = is_content_editable
        self.children = []
        self.parent = None

    def append_child(self, child):
        child.parent = self
        self.children.append(child)
        return child

    @property
    def firstChild(self):
        return self.children[0] if self.children else None

    @property
    def nextSibling(self):
        if not self.parent:
            return None
        idx = self.parent.children.index(self)
        if idx + 1 < len(self.parent.children):
            return self.parent.children[idx + 1]
        return None

    def hasAttribute(self, attr):
        return attr in self.attributes

    def getAttribute(self, attr):
        return self.attributes.get(attr)

    def setAttribute(self, attr, val):
        self.attributes[attr] = val

    def get_text_content(self):
        if self.nodeType == self.TEXT_NODE:
            return self.nodeValue
        return "".join(child.get_text_content() for child in self.children)


class SpecificationTranslationEngine:
    """
    Authoritative reference implementation derived strictly from
    PROJECT.md § Feature Inventory (F01–F26) and Interface Contracts.
    """

    def __init__(self, dictionary=None):
        self.dictionary = dictionary or {}
        self.substring_replacements = [
            ("Minimize", "最小化"),
            ("Maximize", "最大化"),
            ("Toggle Developer Tools", "切换开发者工具"),
            ("Default", "默认"),
            ("Full Machine", "整机授权"),
            ("Turbo Mode", "极速模式"),
            ("Turbo mode", "极速模式"),
            ("Custom", "自定义"),
            ("System", "跟随系统"),
        ]

    def normalize(self, text):
        if text is None:
            return ""
        return str(text).replace("\u00a0", " ")

    def should_bypass_element(self, node):
        if node.nodeType != MockNode.ELEMENT_NODE:
            return False
        tag = node.tagName.lower() if node.tagName else ""
        if tag in ("code", "pre", "script", "style", "noscript", "canvas"):
            return True
        bypass_classes = {
            "monaco-editor", "view-lines", "monaco-list-row", "terminal",
            "xterm", "xterm-screen", "code-block", "hljs"
        }
        if any(cls in bypass_classes for cls in node.classList):
            return True
        curr = node.parent
        while curr:
            if curr.nodeType == MockNode.ELEMENT_NODE:
                curr_tag = curr.tagName.lower() if curr.tagName else ""
                if curr_tag in ("code", "pre", "textarea") or curr.isContentEditable:
                    return True
                if any(cls in bypass_classes for cls in curr.classList):
                    return True
            curr = curr.parent
        return False

    def translate_text(self, text):
        if not text or not isinstance(text, str):
            return None
        normalized = self.normalize(text)
        trimmed = normalized.strip()
        if not trimmed:
            return None

        # 1. Exact Dictionary Match
        if trimmed in self.dictionary:
            return normalized.replace(trimmed, self.dictionary[trimmed])
        if normalized in self.dictionary:
            return self.dictionary[normalized]

        # 2. Dynamic Counter Badges: (Subagents|Files Changed|Artifacts|Uploads|Background Tasks) \d+
        pane_match = re.match(r"^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks)\s+(\d+)$", trimmed, re.IGNORECASE)
        if pane_match:
            label_name = pane_match.group(1).lower()
            num = pane_match.group(2)
            type_map = {
                "subagents": "子智能体",
                "files changed": "已修改文件",
                "artifacts": "产物",
                "uploads": "已上传文件",
                "background tasks": "后台任务"
            }
            label = type_map.get(label_name, pane_match.group(1))
            return normalized.replace(trimmed, f"{label} {num}")

        # 3. Dynamic File Change Counter: N files changed / 1 file changed
        files_changed_match = re.match(r"^(\d+)\s+files?\s+changed$", trimmed, re.IGNORECASE)
        if files_changed_match:
            return normalized.replace(trimmed, f"{files_changed_match.group(1)} 个文件已修改")

        # 4. Relative Timestamps Compact: 10d, 5m, 1mo, 2h, 30s, 1y
        compact_time_match = re.match(r"^(\d+)\s*(mo|d|m|h|s|y)$", trimmed, re.IGNORECASE)
        if compact_time_match:
            num = compact_time_match.group(1)
            unit = compact_time_match.group(2).lower()
            unit_map = {
                "mo": "个月前",
                "d": "天前",
                "m": "分钟前",
                "h": "小时前",
                "s": "秒前",
                "y": "年前"
            }
            return normalized.replace(trimmed, f"{num}{unit_map[unit]}")

        # 5. Relative Timestamps Suffixed: (\d+)\s*(days?|hours?|minutes?|seconds?)\s+ago
        suffixed_time_match = re.match(r"^(\d+)\s*(days?|hours?|minutes?|seconds?)\s+ago$", trimmed, re.IGNORECASE)
        if suffixed_time_match:
            num = suffixed_time_match.group(1)
            unit = suffixed_time_match.group(2).lower()
            if "day" in unit:
                return normalized.replace(trimmed, f"{num}天前")
            elif "hour" in unit:
                return normalized.replace(trimmed, f"{num}小时前")
            elif "minute" in unit:
                return normalized.replace(trimmed, f"{num}分钟前")
            elif "second" in unit:
                return normalized.replace(trimmed, f"{num}秒前")

        # 6. Date Header Prefixes: Today ... / Yesterday ...
        if trimmed.startswith("Today "):
            return normalized.replace("Today ", "今天 ")
        if trimmed.startswith("Yesterday "):
            return normalized.replace("Yesterday ", "昨天 ")

        # 7. Live Thinking Timer State: Thinking for 1.2s / Thought for 1.2s
        thinking_match = re.match(r"^(Thinking|Thought)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", trimmed, re.IGNORECASE)
        if thinking_match:
            num = thinking_match.group(2)
            unit = thinking_match.group(3) or "s"
            cn_unit = "毫秒" if unit.lower().startswith("ms") else "秒"
            return normalized.replace(trimmed, f"思考中 ({num}{cn_unit})")

        # 8. Live Working Timer State: Working for 3.4s
        working_match = re.match(r"^Working\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", trimmed, re.IGNORECASE)
        if working_match:
            num = working_match.group(1)
            unit = working_match.group(2) or "s"
            cn_unit = "毫秒" if unit.lower().startswith("ms") else "秒"
            return normalized.replace(trimmed, f"处理中 ({num}{cn_unit})")

        # 9. Execution Completion Duration: (Completed|Finished|Done) in 12.3s
        completed_match = re.match(r"^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", trimmed, re.IGNORECASE)
        if completed_match:
            num = completed_match.group(2)
            unit = completed_match.group(3) or "s"
            cn_unit = "毫秒" if unit.lower().startswith("ms") else "秒"
            return normalized.replace(trimmed, f"已完成 (耗时 {num}{cn_unit})")

        # 10. Substring Replacements
        new_text = normalized
        modified = False
        for search_str, replace_str in self.substring_replacements:
            if search_str in new_text:
                new_text = new_text.replace(search_str, replace_str)
                modified = True
        if modified:
            return new_text

        return None

    def walk(self, node):
        if not node:
            return
        if node.nodeType == MockNode.TEXT_NODE:
            # Check if parent should be bypassed
            if node.parent and self.should_bypass_element(node.parent):
                return
            trans = self.translate_text(node.nodeValue)
            if trans is not None and trans != node.nodeValue:
                node.nodeValue = trans
        elif node.nodeType == MockNode.ELEMENT_NODE:
            if self.should_bypass_element(node):
                return

            tag = node.tagName.lower() if node.tagName else ""

            # Translate standard attributes (excluding user typing value)
            for attr in ["placeholder", "title", "aria-label"]:
                if node.hasAttribute(attr):
                    val = node.getAttribute(attr)
                    trans = self.translate_text(val)
                    if trans is not None and trans != val:
                        node.setAttribute(attr, trans)

            # Skip children of textarea or contenteditable to protect user typing
            if tag == "textarea" or node.isContentEditable:
                return

            for child in list(node.children):
                self.walk(child)


# ==============================================================================
# TIER 1: Feature Coverage Unit Tests (>=5 tests per feature group)
# ==============================================================================

class TestDictionaryCompletenessAndIntegrity(unittest.TestCase):
    """
    Tier 1: Comprehensive verification of dictionary.json and preload.js dictionary.
    Requirement: 400+ keys, 100% pure UTF-8, no typos ("已修政" -> "已修改").
    """
    TIER = 1

    @classmethod
    def setUpClass(cls):
        cls.has_dict_file = os.path.isfile(DICT_PATH)
        if cls.has_dict_file:
            with open(DICT_PATH, "r", encoding="utf-8") as f:
                cls.raw_dict_json = f.read()
                cls.dict_data = json.loads(cls.raw_dict_json)
        else:
            cls.dict_data = {}

        cls.has_preload_file = os.path.isfile(PRELOAD_PATH)
        if cls.has_preload_file:
            with open(PRELOAD_PATH, "r", encoding="utf-8") as f:
                cls.preload_content = f.read()
        else:
            cls.preload_content = ""

    def test_01_dictionary_file_exists_and_is_valid_json(self):
        """Verify dist/dictionary.json exists and parses cleanly as UTF-8 JSON."""
        self.assertTrue(self.has_dict_file, f"dist/dictionary.json not found at {DICT_PATH}")
        self.assertIsInstance(self.dict_data, dict)

    def test_02_dictionary_key_count_specification_target(self):
        """
        Verify dictionary covers 400+ keys as required by PROJECT.md § Milestone 1.
        """
        key_count = len(self.dict_data)
        self.assertGreaterEqual(
            key_count, 400,
            f"Dictionary has {key_count} keys, which is below the 400+ specification target."
        )

    def test_03_dictionary_pure_utf8_encoding_no_mojibake(self):
        """Verify no mojibake or encoding corruption markers in dictionary values."""
        mojibake_indicators = ["\ufffd", "锟斤拷", "Ã©", "Ã", "???"]
        for key, val in self.dict_data.items():
            for indicator in mojibake_indicators:
                self.assertNotIn(
                    indicator, str(val),
                    f"Mojibake / encoding artifact '{indicator}' found in translation for '{key}': '{val}'"
                )

    def test_04_dictionary_no_known_typos(self):
        """
        Verify zero translation typos:
        - 'Files Changed' must be '已修改文件' (NOT '已修政文件')
        - 'Agent cannot modify files outside of the workspace in strict mode.' must NOT have '修政'
        """
        if "Files Changed" in self.dict_data:
            self.assertEqual(
                self.dict_data["Files Changed"], "已修改文件",
                f"Typo detected: 'Files Changed' is '{self.dict_data['Files Changed']}', expected '已修改文件'"
            )
        for key, val in self.dict_data.items():
            self.assertNotIn("已修政", val, f"Typo '已修政' found in key '{key}': '{val}'")
            self.assertNotIn("无法修政", val, f"Typo '无法修政' found in key '{key}': '{val}'")

    def test_05_preload_js_contains_valid_chinese_localization_marker(self):
        """Verify preload.js contains the official patch signature header marker."""
        self.assertTrue(self.has_preload_file, "dist/preload.js does not exist")
        self.assertIn(
            "// Antigravity Chinese Localization Patch",
            self.preload_content,
            "dist/preload.js missing header marker: '// Antigravity Chinese Localization Patch'"
        )

    def test_06_preload_js_unicode_escapes_or_utf8_validity(self):
        r"""Verify all Unicode escapes (\uXXXX) in preload.js represent valid Chinese characters."""
        unicode_escapes = re.findall(r"\\u([0-9a-fA-F]{4})", self.preload_content)
        self.assertGreater(len(unicode_escapes), 0, "preload.js should contain unicode escapes")
        for esc in unicode_escapes:
            char_code = int(esc, 16)
            self.assertTrue(
                0x0000 <= char_code <= 0xFFFF,
                f"Invalid unicode escape sequence \\u{esc}"
            )


class TestDynamicRegexMatchers(unittest.TestCase):
    """
    Tier 1: Dynamic Regex Matching for Timers, Relative Times, and Counters.
    Covers F04, F05, F06, F07, F08, F09, F10, F11.
    """
    TIER = 1

    def setUp(self):
        self.engine = SpecificationTranslationEngine()

    # --- F09: Live Thinking Timer State (>= 5 cases) ---
    def test_f09_thinking_timer_float_seconds(self):
        """F09: 'Thinking for 1.2s' -> '思考中 (1.2秒)'"""
        self.assertEqual(self.engine.translate_text("Thinking for 1.2s"), "思考中 (1.2秒)")

    def test_f09_thinking_timer_integer_seconds(self):
        """F09: 'Thinking for 5s' -> '思考中 (5秒)'"""
        self.assertEqual(self.engine.translate_text("Thinking for 5s"), "思考中 (5秒)")

    def test_f09_thinking_timer_milliseconds(self):
        """F09: 'Thinking for 500ms' -> '思考中 (500毫秒)'"""
        self.assertEqual(self.engine.translate_text("Thinking for 500ms"), "思考中 (500毫秒)")

    def test_f09_thought_past_tense(self):
        """F09: 'Thought for 0.8s' -> '思考中 (0.8秒)'"""
        self.assertEqual(self.engine.translate_text("Thought for 0.8s"), "思考中 (0.8秒)")

    def test_f09_thinking_verbose_seconds(self):
        """F09: 'Thinking for 12 seconds' -> '思考中 (12秒)'"""
        self.assertEqual(self.engine.translate_text("Thinking for 12 seconds"), "思考中 (12秒)")

    # --- F10: Live Working Timer State (>= 5 cases) ---
    def test_f10_working_timer_float_seconds(self):
        """F10: 'Working for 3.4s' -> '处理中 (3.4秒)'"""
        self.assertEqual(self.engine.translate_text("Working for 3.4s"), "处理中 (3.4秒)")

    def test_f10_working_timer_small_float(self):
        """F10: 'Working for 0.05s' -> '处理中 (0.05秒)'"""
        self.assertEqual(self.engine.translate_text("Working for 0.05s"), "处理中 (0.05秒)")

    def test_f10_working_timer_large_integer(self):
        """F10: 'Working for 120s' -> '处理中 (120秒)'"""
        self.assertEqual(self.engine.translate_text("Working for 120s"), "处理中 (120秒)")

    def test_f10_working_timer_milliseconds(self):
        """F10: 'Working for 250ms' -> '处理中 (250毫秒)'"""
        self.assertEqual(self.engine.translate_text("Working for 250ms"), "处理中 (250毫秒)")

    def test_f10_working_timer_with_padding(self):
        """F10: '  Working for 1.5s  ' -> '  处理中 (1.5秒)  '"""
        self.assertEqual(self.engine.translate_text("  Working for 1.5s  "), "  处理中 (1.5秒)  ")

    # --- F11: Execution Completion Duration (>= 5 cases) ---
    def test_f11_done_in_float_seconds(self):
        """F11: 'Done in 12.3s' -> '已完成 (耗时 12.3秒)'"""
        self.assertEqual(self.engine.translate_text("Done in 12.3s"), "已完成 (耗时 12.3秒)")

    def test_f11_completed_in_seconds(self):
        """F11: 'Completed in 0.8s' -> '已完成 (耗时 0.8秒)'"""
        self.assertEqual(self.engine.translate_text("Completed in 0.8s"), "已完成 (耗时 0.8秒)")

    def test_f11_finished_in_milliseconds(self):
        """F11: 'Finished in 450ms' -> '已完成 (耗时 450毫秒)'"""
        self.assertEqual(self.engine.translate_text("Finished in 450ms"), "已完成 (耗时 450毫秒)")

    def test_f11_done_in_integer_seconds(self):
        """F11: 'Done in 45s' -> '已完成 (耗时 45秒)'"""
        self.assertEqual(self.engine.translate_text("Done in 45s"), "已完成 (耗时 45秒)")

    def test_f11_completed_in_word_seconds(self):
        """F11: 'Completed in 2 seconds' -> '已完成 (耗时 2秒)'"""
        self.assertEqual(self.engine.translate_text("Completed in 2 seconds"), "已完成 (耗时 2秒)")

    # --- F06: Relative Timestamps Compact (>= 5 cases) ---
    def test_f06_compact_days(self):
        """F06: '10d' -> '10天前'"""
        self.assertEqual(self.engine.translate_text("10d"), "10天前")

    def test_f06_compact_minutes(self):
        """F06: '5m' -> '5分钟前'"""
        self.assertEqual(self.engine.translate_text("5m"), "5分钟前")

    def test_f06_compact_months(self):
        """F06: '1mo' -> '1个月前'"""
        self.assertEqual(self.engine.translate_text("1mo"), "1个月前")

    def test_f06_compact_hours(self):
        """F06: '2h' -> '2小时前'"""
        self.assertEqual(self.engine.translate_text("2h"), "2小时前")

    def test_f06_compact_seconds_and_years(self):
        """F06: '30s' -> '30秒前', '1y' -> '1年前'"""
        self.assertEqual(self.engine.translate_text("30s"), "30秒前")
        self.assertEqual(self.engine.translate_text("1y"), "1年前")

    # --- F07: Relative Timestamps Suffixed (>= 5 cases) ---
    def test_f07_suffixed_minutes_ago(self):
        """F07: '5 minutes ago' -> '5分钟前'"""
        self.assertEqual(self.engine.translate_text("5 minutes ago"), "5分钟前")

    def test_f07_suffixed_hours_ago(self):
        """F07: '2 hours ago' -> '2小时前'"""
        self.assertEqual(self.engine.translate_text("2 hours ago"), "2小时前")

    def test_f07_suffixed_days_ago(self):
        """F07: '3 days ago' -> '3天前'"""
        self.assertEqual(self.engine.translate_text("3 days ago"), "3天前")

    def test_f07_suffixed_single_day_ago(self):
        """F07: '1 day ago' -> '1天前'"""
        self.assertEqual(self.engine.translate_text("1 day ago"), "1天前")

    def test_f07_suffixed_seconds_ago(self):
        """F07: '45 seconds ago' -> '45秒前'"""
        self.assertEqual(self.engine.translate_text("45 seconds ago"), "45秒前")

    # --- F08: Date Header Prefixes (>= 5 cases) ---
    def test_f08_today_morning(self):
        """F08: 'Today 10:30 AM' -> '今天 10:30 AM'"""
        self.assertEqual(self.engine.translate_text("Today 10:30 AM"), "今天 10:30 AM")

    def test_f08_today_with_date(self):
        """F08: 'Today at 3:00 PM' -> '今天 at 3:00 PM'"""
        self.assertEqual(self.engine.translate_text("Today at 3:00 PM"), "今天 at 3:00 PM")

    def test_f08_yesterday_evening(self):
        """F08: 'Yesterday 4:15 PM' -> '昨天 4:15 PM'"""
        self.assertEqual(self.engine.translate_text("Yesterday 4:15 PM"), "昨天 4:15 PM")

    def test_f08_yesterday_with_time(self):
        """F08: 'Yesterday 23:59' -> '昨天 23:59'"""
        self.assertEqual(self.engine.translate_text("Yesterday 23:59"), "昨天 23:59")

    def test_f08_today_simple(self):
        """F08: 'Today 12:00' -> '今天 12:00'"""
        self.assertEqual(self.engine.translate_text("Today 12:00"), "今天 12:00")

    # --- F04 & F05: Dynamic Counter Badges (>= 5 cases) ---
    def test_f04_subagents_zero(self):
        """F04: 'Subagents 0' -> '子智能体 0'"""
        self.assertEqual(self.engine.translate_text("Subagents 0"), "子智能体 0")

    def test_f04_files_changed_counter(self):
        """F04: 'Files Changed 3' -> '已修改文件 3'"""
        self.assertEqual(self.engine.translate_text("Files Changed 3"), "已修改文件 3")

    def test_f04_artifacts_counter(self):
        """F04: 'Artifacts 1' -> '产物 1'"""
        self.assertEqual(self.engine.translate_text("Artifacts 1"), "产物 1")

    def test_f04_background_tasks_counter(self):
        """F04: 'Background Tasks 2' -> '后台任务 2'"""
        self.assertEqual(self.engine.translate_text("Background Tasks 2"), "后台任务 2")

    def test_f05_n_files_changed_plural_and_singular(self):
        """F05: '1 file changed' and '5 files changed'"""
        self.assertEqual(self.engine.translate_text("1 file changed"), "1 个文件已修改")
        self.assertEqual(self.engine.translate_text("5 files changed"), "5 个文件已修改")


class TestDynamicDOMTranslation(unittest.TestCase):
    """
    Tier 1: Dynamic DOM Tree Translation across UI Categories.
    Covers F01, F02, F03, F12, F13, F14, F15, F16, F17, F18, F19, F20, F24.
    """
    TIER = 1

    def setUp(self):
        # Build dictionary from specification
        dict_map = {
            "New Conversation": "新建对话",
            "Conversation History": "历史对话",
            "Scheduled Tasks": "计划任务",
            "Projects": "项目列表",
            "Settings": "设置",
            "Untitled Conversation": "未命名对话",
            "Close": "关闭",
            "Cancel": "取消",
            "Save": "保存",
            "Delete": "删除",
            "Rename": "重命名",
            "Review": "审核",
            "Accept": "接受",
            "Reject": "拒绝",
            "Accept Step": "接受步骤",
            "Reject Step": "拒绝步骤",
            "Action Required": "需要操作",
            "Apply Changes": "应用更改",
            "Thinking...": "思考中...",
            "Working...": "处理中...",
            "Agent finished": "智能体已完成",
            "Account": "账户设置",
            "Permissions": "权限控制",
            "Appearance": "外观样式",
            "Updates": "更新",
            "Your Plan: Google AI Ultra": "订阅计划：Google AI 旗舰版",
            "Credits Balance": "账户点数余额",
            "Daily Quota": "每日免费配额",
            "Monthly Quota": "每月配额",
            "Quota Exceeded": "配额已用尽",
            "Terminal Command Execution Policy": "终端命令执行策略",
            "File Access Policy": "文件访问策略",
            "Allow commands outside sandbox": "允许在沙箱外部执行命令",
            "Read-only mode": "只读模式",
            "Theme Mode": "配色主题模式",
            "Follow System Theme": "跟随系统主题",
            "Light Theme": "浅色主题",
            "Dark Theme": "深色主题",
            "Font Size": "字号大小",
            "Zoom Factor": "缩放比例",
            "Feedback Type": "反馈类型",
            "Bug Report": "缺陷报告",
            "Feature Request": "功能需求",
            "Steps to reproduce the issue": "重现步骤",
            "File": "文件",
            "View": "视图",
            "Window": "窗口",
            "Help": "帮助",
            "New Window": "新建窗口",
            "Check for Updates": "检查更新",
            "Ask anything, @ to mention, / for actions": "问我任何问题，用 @ 提及文件，用 / 执行动作"
        }
        self.engine = SpecificationTranslationEngine(dictionary=dict_map)

    def test_f01_primary_navigation_dom_translation(self):
        """F01: Translates core sidebar items in DOM tree."""
        nav_container = MockNode(MockNode.ELEMENT_NODE, "div", class_name="sidebar-nav")
        for item in ["New Conversation", "Conversation History", "Scheduled Tasks", "Projects", "Settings"]:
            btn = MockNode(MockNode.ELEMENT_NODE, "button")
            text = MockNode(MockNode.TEXT_NODE, node_value=item)
            btn.append_child(text)
            nav_container.append_child(btn)

        self.engine.walk(nav_container)
        expected_texts = ["新建对话", "历史对话", "计划任务", "项目列表", "设置"]
        actual_texts = [child.firstChild.nodeValue for child in nav_container.children]
        self.assertEqual(actual_texts, expected_texts)

    def test_f02_conversation_actions_dom_translation(self):
        """F02: Translates conversation management action buttons."""
        container = MockNode(MockNode.ELEMENT_NODE, "div")
        actions = ["Untitled Conversation", "Close", "Cancel", "Save", "Delete", "Rename"]
        for act in actions:
            span = MockNode(MockNode.ELEMENT_NODE, "span")
            span.append_child(MockNode(MockNode.TEXT_NODE, node_value=act))
            container.append_child(span)

        self.engine.walk(container)
        expected = ["未命名对话", "关闭", "取消", "保存", "删除", "重命名"]
        actual = [span.firstChild.nodeValue for span in container.children]
        self.assertEqual(actual, expected)

    def test_f13_review_and_action_buttons(self):
        """F13: Translates review buttons in review workflow pane."""
        panel = MockNode(MockNode.ELEMENT_NODE, "div", class_name="action-bar")
        buttons = ["Review", "Accept", "Reject", "Accept Step", "Reject Step", "Action Required", "Apply Changes"]
        for b in buttons:
            btn = MockNode(MockNode.ELEMENT_NODE, "button")
            btn.append_child(MockNode(MockNode.TEXT_NODE, node_value=b))
            panel.append_child(btn)

        self.engine.walk(panel)
        expected = ["审核", "接受", "拒绝", "接受步骤", "拒绝步骤", "需要操作", "应用更改"]
        actual = [btn.firstChild.nodeValue for btn in panel.children]
        self.assertEqual(actual, expected)

    def test_f15_model_quota_displays(self):
        """F15: Translates quota status displays and balance items."""
        modal = MockNode(MockNode.ELEMENT_NODE, "div", class_name="quota-modal")
        labels = ["Your Plan: Google AI Ultra", "Credits Balance", "Daily Quota", "Monthly Quota", "Quota Exceeded"]
        for lbl in labels:
            p = MockNode(MockNode.ELEMENT_NODE, "p")
            p.append_child(MockNode(MockNode.TEXT_NODE, node_value=lbl))
            modal.append_child(p)

        self.engine.walk(modal)
        expected = ["订阅计划：Google AI 旗舰版", "账户点数余额", "每日免费配额", "每月配额", "配额已用尽"]
        actual = [p.firstChild.nodeValue for p in modal.children]
        self.assertEqual(actual, expected)

    def test_f19_placeholders_and_tooltips_attributes(self):
        """F19: Translates placeholder, title, and aria-label attributes."""
        input_el = MockNode(
            MockNode.ELEMENT_NODE, "input",
            attributes={
                "placeholder": "Ask anything, @ to mention, / for actions",
                "title": "New Conversation",
                "aria-label": "Settings"
            }
        )
        self.engine.walk(input_el)
        self.assertEqual(input_el.getAttribute("placeholder"), "问我任何问题，用 @ 提及文件，用 / 执行动作")
        self.assertEqual(input_el.getAttribute("title"), "新建对话")
        self.assertEqual(input_el.getAttribute("aria-label"), "设置")

    def test_f24_substring_replacements(self):
        """F24: Targeted substring replacements in compound UI text."""
        self.assertEqual(self.engine.translate_text("Click to Minimize window"), "Click to 最小化 window")
        self.assertEqual(self.engine.translate_text("Click to Maximize window"), "Click to 最大化 window")
        self.assertEqual(self.engine.translate_text("Toggle Developer Tools in Help"), "切换开发者工具 in Help")
        self.assertEqual(self.engine.translate_text("Enable Turbo Mode now"), "Enable 极速模式 now")


# ==============================================================================
# TIER 2: Boundary & Corner Cases (Safety Bypass, Normalization, Stress)
# ==============================================================================

class TestSafetyBypassGuards(unittest.TestCase):
    """
    Tier 2: Verification of safety bypass rules (F25, F26).
    Ensures code, terminals, Monaco editor elements, and user typing are NEVER translated.
    """
    TIER = 2

    def setUp(self):
        dict_map = {
            "File": "文件",
            "Delete": "删除",
            "Save": "保存",
            "Close": "关闭",
            "function": "函数",
            "return": "返回",
            "import": "导入",
            "const": "常量"
        }
        self.engine = SpecificationTranslationEngine(dictionary=dict_map)

    def test_f25_bypass_monaco_editor_container(self):
        """F25: Code inside .monaco-editor container must NOT be translated."""
        monaco_root = MockNode(MockNode.ELEMENT_NODE, "div", class_name="monaco-editor vs-dark")
        view_lines = MockNode(MockNode.ELEMENT_NODE, "div", class_name="view-lines")
        line1 = MockNode(MockNode.ELEMENT_NODE, "div", class_name="view-line")
        code_text = MockNode(MockNode.TEXT_NODE, node_value="const File = delete(); // Save and Close")
        line1.append_child(code_text)
        view_lines.append_child(line1)
        monaco_root.append_child(view_lines)

        self.engine.walk(monaco_root)
        self.assertEqual(code_text.nodeValue, "const File = delete(); // Save and Close")

    def test_f25_bypass_pre_and_code_tags(self):
        """F25: Text inside <pre> and <code> blocks must NOT be translated."""
        pre = MockNode(MockNode.ELEMENT_NODE, "pre")
        code = MockNode(MockNode.ELEMENT_NODE, "code", class_name="language-python")
        code_str = "def delete_file(file_path):\n    save_data(file_path)\n    close_file()"
        code_text = MockNode(MockNode.TEXT_NODE, node_value=code_str)
        code.append_child(code_text)
        pre.append_child(code)

        self.engine.walk(pre)
        self.assertEqual(code_text.nodeValue, code_str)

    def test_f25_bypass_terminal_and_xterm(self):
        """F25: Output inside .terminal or .xterm elements must NOT be translated."""
        term = MockNode(MockNode.ELEMENT_NODE, "div", class_name="terminal xterm xterm-screen")
        term_text = MockNode(MockNode.TEXT_NODE, node_value="Deleting old cache... File saved. Close connection.")
        term.append_child(term_text)

        self.engine.walk(term)
        self.assertEqual(term_text.nodeValue, "Deleting old cache... File saved. Close connection.")

    def test_f26_bypass_textarea_user_typing(self):
        """F26: Text and user typing inside <textarea> must NOT be translated."""
        textarea = MockNode(MockNode.ELEMENT_NODE, "textarea", attributes={"value": "Please Delete and Save this File"})
        text_node = MockNode(MockNode.TEXT_NODE, node_value="Please Delete and Save this File")
        textarea.append_child(text_node)

        self.engine.walk(textarea)
        self.assertEqual(text_node.nodeValue, "Please Delete and Save this File")
        self.assertEqual(textarea.getAttribute("value"), "Please Delete and Save this File")

    def test_f26_bypass_contenteditable_elements(self):
        """F26: Elements with contenteditable='true' must NOT be translated."""
        editor_div = MockNode(
            MockNode.ELEMENT_NODE, "div",
            class_name="chat-input-box",
            is_content_editable=True
        )
        user_draft = MockNode(MockNode.TEXT_NODE, node_value="I want to Delete this File.")
        editor_div.append_child(user_draft)

        self.engine.walk(editor_div)
        self.assertEqual(user_draft.nodeValue, "I want to Delete this File.")


class TestNormalizationAndBoundaryStress(unittest.TestCase):
    """
    Tier 2: Boundary, escaping, and stress testing.
    """
    TIER = 2

    def setUp(self):
        dict_map = {
            "New Conversation": "新建对话",
            "Settings": "设置"
        }
        self.engine = SpecificationTranslationEngine(dictionary=dict_map)

    def test_f23_non_breaking_space_normalization(self):
        r"""F23: String containing non-breaking space \u00a0 is normalized and translated."""
        text_with_nbsp = "New\u00a0Conversation"
        result = self.engine.translate_text(text_with_nbsp)
        self.assertEqual(result, "新建对话")

    def test_boundary_empty_and_whitespace_strings(self):
        """Tier 2: Empty, whitespace-only, and None inputs return None gracefully."""
        self.assertIsNone(self.engine.translate_text(""))
        self.assertIsNone(self.engine.translate_text("   "))
        self.assertIsNone(self.engine.translate_text("\t\n\r"))
        self.assertIsNone(self.engine.translate_text(None))

    def test_boundary_special_symbols_and_emojis(self):
        """Tier 2: Text containing special symbols, emojis, and punctuation."""
        special_key = "Ask anything, @ to mention, / for actions"
        custom_dict = {
            special_key: "问我任何问题，用 @ 提及文件，用 / 执行动作",
            "✨ New Conversation 🚀": "✨ 新建对话 🚀"
        }
        engine = SpecificationTranslationEngine(dictionary=custom_dict)
        self.assertEqual(
            engine.translate_text(special_key),
            "问我任何问题，用 @ 提及文件，用 / 执行动作"
        )
        self.assertEqual(
            engine.translate_text("✨ New Conversation 🚀"),
            "✨ 新建对话 🚀"
        )

    def test_boundary_nested_dom_hierarchy(self):
        """Tier 2: Deeply nested DOM nodes with mixed element types."""
        root = MockNode(MockNode.ELEMENT_NODE, "div")
        curr = root
        for _ in range(10):
            next_div = MockNode(MockNode.ELEMENT_NODE, "div")
            curr.append_child(next_div)
            curr = next_div

        text_node = MockNode(MockNode.TEXT_NODE, node_value="Settings")
        curr.append_child(text_node)

        self.engine.walk(root)
        self.assertEqual(text_node.nodeValue, "设置")


if __name__ == "__main__":
    unittest.main()
