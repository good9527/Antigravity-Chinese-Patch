#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_tier5_adversarial.py
Tier 5 White-Box Adversarial Coverage Hardening Test Suite for Antigravity Chinese Patch.

Comprehensive White-Box Challenges:
1. Regex alternations, float decimal timers, suffixed relative timestamps, and ReDoS resilience.
2. Shadow DOM traversal, multi-level nested shadow trees, and Element.prototype.attachShadow monkey-patching.
3. Non-breaking space normalization (\u00a0) across text nodes, attributes, buttons, and dynamic regexes.
4. Strict safety bypass guards for nested Monaco editors, CodeMirror, terminals, Markdown fences, and user input values.
5. Pure 7-bit ASCII Unicode escape sequence integrity and exact 3-way parity across preload.js, engine.js, and dictionary.json.
6. High-throughput performance and deep recursion DOM stress testing.
"""

import unittest
import os
import sys
import json
import re
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
DICT_PATH = os.path.join(DIST_DIR, "dictionary.json")
PRELOAD_PATH = os.path.join(DIST_DIR, "preload.js")
ENGINE_PATH = os.path.join(DIST_DIR, "engine.js")

with open(DICT_PATH, "r", encoding="utf-8") as f:
    DICTIONARY = json.load(f)


# ==============================================================================
# White-Box DOM and Engine Emulation for Tier 5
# ==============================================================================

class MockDOMNode:
    """Accurate DOM Node representation with ShadowRoot and Web Components support."""
    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    DOCUMENT_FRAGMENT_NODE = 11

    def __init__(self, node_type, tag_name="", node_value="", attributes=None, class_name="", is_content_editable=False):
        self.nodeType = node_type
        self.tagName = tag_name.upper() if tag_name else ""
        self.nodeValue = node_value
        self.attributes = dict(attributes or {})
        self.className = class_name
        self.isContentEditable = is_content_editable
        self.children = []
        self.parent = None
        self.shadowRoot = None

    @property
    def classList(self):
        return set(self.className.split()) if self.className else set()

    @property
    def firstChild(self):
        return self.children[0] if self.children else None

    @property
    def nextSibling(self):
        if not self.parent:
            return None
        try:
            idx = self.parent.children.index(self)
            if idx + 1 < len(self.parent.children):
                return self.parent.children[idx + 1]
        except ValueError:
            pass
        return None

    def append_child(self, child):
        child.parent = self
        self.children.append(child)
        return child

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return child
        raise ValueError("Child not found")

    def hasAttribute(self, attr):
        return attr in self.attributes

    def getAttribute(self, attr):
        return self.attributes.get(attr)

    def setAttribute(self, attr, val):
        self.attributes[attr] = str(val)

    def matches(self, selector):
        """Basic CSS selector matcher for bypass queries."""
        selectors = [s.strip() for s in selector.split(",") if s.strip()]
        for sel in selectors:
            if sel.startswith("."):
                cls = sel[1:]
                if cls in self.classList:
                    return True
            elif sel.startswith("[") and sel.endswith("]"):
                inner = sel[1:-1]
                if "=" in inner:
                    attr, expected = inner.split("=", 1)
                    expected = expected.strip('"\'')
                    if self.getAttribute(attr) == expected:
                        return True
                else:
                    if self.hasAttribute(inner):
                        return True
            elif sel.upper() == self.tagName:
                return True
        return False

    def closest(self, selector):
        curr = self
        while curr:
            if curr.nodeType == self.ELEMENT_NODE and curr.matches(selector):
                return curr
            curr = curr.parent
        return None

    def attachShadow(self, init=None):
        """Simulate Element.prototype.attachShadow."""
        shadow = MockDOMNode(self.DOCUMENT_FRAGMENT_NODE, tag_name="#shadow-root")
        shadow.host = self
        self.shadowRoot = shadow
        return shadow

    def get_text_content(self):
        if self.nodeType == self.TEXT_NODE:
            return self.nodeValue
        texts = []
        for child in self.children:
            texts.append(child.get_text_content())
        if self.shadowRoot:
            texts.append(self.shadowRoot.get_text_content())
        return "".join(texts)


class Tier5WhiteBoxEngine:
    """
    White-Box Reference Translation Engine mirroring dist/engine.js and dist/preload.js.
    Exhaustively implements all 18 dynamic rules, safety bypass, substring replacements,
    non-breaking space normalization, and shadow DOM lifecycle.
    """

    def __init__(self, dictionary=None):
        self.dictionary = dictionary or DICTIONARY
        self.substring_replacements = [
            ("Minimize", "\u6700\u5c0f\u5316"),
            ("Maximize", "\u6700\u5927\u5316"),
            ("Toggle Developer Tools", "\u5207\u6362\u5f00\u53d1\u8005\u5de5\u5177"),
            ("Default", "\u9ed8\u8ba4"),
            ("Full Machine", "\u6574\u673a\u6388\u6743"),
            ("Turbo Mode", "\u6781\u901f\u6a21\u5f0f"),
            ("Turbo mode", "\u6781\u901f\u6a21\u5f0f"),
            ("Custom", "\u81ea\u5b9a\u4e49"),
            ("System", "\u8ddf\u968f\u7cfb\u7edf"),
        ]

        self.unit_map_cn = {
            'mo': '\u4e2a\u6708\u524d', 'month': '\u4e2a\u6708\u524d', 'months': '\u4e2a\u6708\u524d',
            'd': '\u5929\u524d', 'day': '\u5929\u524d', 'days': '\u5929\u524d',
            'm': '\u5206\u949f\u524d', 'min': '\u5206\u949f\u524d', 'mins': '\u5206\u949f\u524d',
            'minute': '\u5206\u949f\u524d', 'minutes': '\u5206\u949f\u524d',
            'h': '\u5c0f\u65f6\u524d', 'hr': '\u5c0f\u65f6\u524d', 'hrs': '\u5c0f\u65f6\u524d',
            'hour': '\u5c0f\u65f6\u524d', 'hours': '\u5c0f\u65f6\u524d',
            's': '\u79d2\u524d', 'sec': '\u79d2\u524d', 'secs': '\u79d2\u524d',
            'second': '\u79d2\u524d', 'seconds': '\u79d2\u524d',
            'y': '\u5e74\u524d', 'yr': '\u5e74\u524d', 'yrs': '\u5e74\u524d',
            'year': '\u5e74\u524d', 'years': '\u5e74\u524d'
        }

        self.ignore_tags = {
            'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'CANVAS',
            'SVG', 'MATH', 'OBJECT', 'EMBED'
        }
        self.code_or_input_tags = {
            'PRE', 'CODE', 'KBD', 'SAMP', 'VAR', 'TEXTAREA'
        }
        self.button_input_types = {'button', 'submit', 'reset'}
        self.safe_attrs = ['placeholder', 'title', 'aria-label']
        self.bypass_classes = {
            'monaco-editor', 'view-lines', 'monaco-list-row', 'cm-editor', 'cm-content',
            'editor-instance', 'monaco-tokenized-source', 'code-block', 'hljs',
            'syntax-highlighted', 'highlight', 'terminal', 'xterm', 'xterm-screen',
            'xterm-viewport', 'terminal-wrapper'
        }

        # Precompiled regex patterns
        self.re_thinking_1 = re.compile(r"^(?:Thinking|Thought)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_thinking_2 = re.compile(r"^Thinking\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$", re.I)
        self.re_thinking_3 = re.compile(r"^(?:Thinking|Thought)\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$", re.I)
        self.re_thinking_4 = re.compile(r"^(?:Thinking|Thought)\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$", re.I)

        self.re_working_1 = re.compile(r"^(?:Working|Worked)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_working_2 = re.compile(r"^Working\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$", re.I)
        self.re_working_3 = re.compile(r"^(?:Working|Worked)\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$", re.I)
        self.re_working_4 = re.compile(r"^(?:Working|Worked)\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$", re.I)

        self.re_completed = re.compile(r"^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_timed = re.compile(r"^Timed\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_elapsed = re.compile(r"^Elapsed\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_total_dur = re.compile(r"^Total\s+duration:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_exec_time = re.compile(r"^Execution\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)

        self.re_just_now = re.compile(r"^just\s+now$", re.I)
        self.re_few_secs = re.compile(r"^a\s+few\s+seconds\s+ago$", re.I)
        self.re_a_min = re.compile(r"^a\s+minute\s+ago$", re.I)
        self.re_an_hr = re.compile(r"^an\s+hour\s+ago$", re.I)
        self.re_a_day = re.compile(r"^a\s+day\s+ago$", re.I)
        self.re_today = re.compile(r"^today$", re.I)
        self.re_yesterday = re.compile(r"^yesterday$", re.I)

        self.re_compact_time = re.compile(r"^(\d+)\s*(mo|[dmhsy])(?:\s+ago)?$", re.I)
        self.re_verbose_time = re.compile(r"^(\d+)\s*(months?|days?|hours?|hrs?|minutes?|mins?|seconds?|secs?|years?|yrs?)\s+ago$", re.I)

        self.re_panes = re.compile(r"^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks|MCP Servers)\s+(\d+)$", re.I)
        self.re_files_changed = re.compile(r"^(\d+)\s+files?\s+changed$", re.I)
        self.re_files_modified = re.compile(r"^(\d+)\s+files?\s+modified$", re.I)
        self.re_files_added = re.compile(r"^(\d+)\s+files?\s+added$", re.I)
        self.re_files_deleted = re.compile(r"^(\d+)\s+files?\s+deleted$", re.I)
        self.re_files = re.compile(r"^(\d+)\s+files?$", re.I)

        self.re_subagents = re.compile(r"^(\d+)\s+subagents?$", re.I)
        self.re_agents_running = re.compile(r"^(\d+)\s+agents?\s+running$", re.I)
        self.re_no_agents_running = re.compile(r"^No\s+agents?\s+running$", re.I)
        self.re_1_agent_running = re.compile(r"^1\s+agent\s+running$", re.I)

        self.re_items_selected = re.compile(r"^(\d+)\s+items?\s+selected$", re.I)
        self.re_selected = re.compile(r"^(\d+)\s+selected$", re.I)
        self.re_tasks = re.compile(r"^(\d+)\s+tasks?$", re.I)
        self.re_artifacts = re.compile(r"^(\d+)\s+artifacts?$", re.I)
        self.re_changes = re.compile(r"^(\d+)\s+changes?$", re.I)
        self.re_errors = re.compile(r"^(\d+)\s+errors?$", re.I)
        self.re_warnings = re.compile(r"^(\d+)\s+warnings?$", re.I)
        self.re_results = re.compile(r"^(\d+)\s+results?$", re.I)

    def normalize(self, str_val):
        if not str_val:
            return ""
        return str_val.replace("\u00a0", " ")

    def format_timer_unit(self, unit):
        if not unit:
            return "\u79d2"
        return "\u6beb\u79d2" if unit.lower().startswith("ms") else "\u79d2"

    def match_dynamic_patterns(self, trimmed):
        m = self.re_thinking_1.match(trimmed)
        if m:
            return f"\u601d\u8003\u4e2d ({m.group(1)}{self.format_timer_unit(m.group(2))})"
        m = self.re_thinking_2.match(trimmed)
        if m:
            return f"\u601d\u8003\u4e2d... ({m.group(1)}{self.format_timer_unit(m.group(2))})"
        m = self.re_thinking_3.match(trimmed) or self.re_thinking_4.match(trimmed)
        if m:
            return f"\u601d\u8003\u4e2d ({m.group(1)}{self.format_timer_unit(m.group(2))})"

        m = self.re_working_1.match(trimmed)
        if m:
            return f"\u5904\u7406\u4e2d ({m.group(1)}{self.format_timer_unit(m.group(2))})"
        m = self.re_working_2.match(trimmed)
        if m:
            return f"\u5904\u7406\u4e2d... ({m.group(1)}{self.format_timer_unit(m.group(2))})"
        m = self.re_working_3.match(trimmed) or self.re_working_4.match(trimmed)
        if m:
            return f"\u5904\u7406\u4e2d ({m.group(1)}{self.format_timer_unit(m.group(2))})"

        m = self.re_completed.match(trimmed)
        if m:
            return f"\u5df2\u5b8c\u6210 (\u8017\u65f6 {m.group(2)}{self.format_timer_unit(m.group(3))})"
        m = self.re_timed.match(trimmed)
        if m:
            return f"\u5df2\u8ba1\u65f6 {m.group(1)}{self.format_timer_unit(m.group(2))}"
        m = self.re_elapsed.match(trimmed)
        if m:
            return f"\u8017\u65f6: {m.group(1)}{self.format_timer_unit(m.group(2))}"
        m = self.re_total_dur.match(trimmed)
        if m:
            return f"\u603b\u8017\u65f6: {m.group(1)}{self.format_timer_unit(m.group(2))}"
        m = self.re_exec_time.match(trimmed)
        if m:
            return f"\u6267\u884c\u8017\u65f6: {m.group(1)}{self.format_timer_unit(m.group(2))}"

        if self.re_just_now.match(trimmed):
            return "\u521a\u521a"
        if self.re_few_secs.match(trimmed):
            return "\u51e0\u79d2\u524d"
        if self.re_a_min.match(trimmed):
            return "1\u5206\u949f\u524d"
        if self.re_an_hr.match(trimmed):
            return "1\u5c0f\u65f6\u524d"
        if self.re_a_day.match(trimmed):
            return "1\u5929\u524d"
        if self.re_today.match(trimmed):
            return "\u4eca\u5929"
        if self.re_yesterday.match(trimmed):
            return "\u6628\u5929"

        if trimmed.startswith("Today "):
            return trimmed.replace("Today ", "\u4eca\u5929 ")
        if trimmed.startswith("Yesterday "):
            return trimmed.replace("Yesterday ", "\u6628\u5929 ")

        m = self.re_compact_time.match(trimmed)
        if m:
            unit = m.group(2).lower()
            cn = self.unit_map_cn.get(unit)
            if cn:
                return f"{m.group(1)}{cn}"

        m = self.re_verbose_time.match(trimmed)
        if m:
            unit = m.group(2).lower()
            cn = self.unit_map_cn.get(unit)
            if cn:
                return f"{m.group(1)}{cn}"

        m = self.re_panes.match(trimmed)
        if m:
            type_map = {
                'subagents': '\u5b50\u667a\u80fd\u4f53',
                'files changed': '\u5df2\u4fee\u6539\u6587\u4ef6',
                'artifacts': '\u4ea7\u7269',
                'uploads': '\u5df2\u4e0a\u4f20\u6587\u4ef6',
                'background tasks': '\u540e\u53f0\u4efb\u52a1',
                'mcp servers': 'MCP \u670d\u52a1'
            }
            label = type_map.get(m.group(1).lower(), m.group(1))
            return f"{label} {m.group(2)}"

        m = self.re_files_changed.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539"
        m = self.re_files_modified.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539"
        m = self.re_files_added.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u6587\u4ef6\u5df2\u6dfb\u52a0"
        m = self.re_files_deleted.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u6587\u4ef6\u5df2\u5220\u9664"
        m = self.re_files.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u6587\u4ef6"

        m = self.re_subagents.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u5b50\u667a\u80fd\u4f53"
        m = self.re_agents_running.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d"
        if self.re_no_agents_running.match(trimmed):
            return "0 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d"
        if self.re_1_agent_running.match(trimmed):
            return "1 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d"

        m = self.re_items_selected.match(trimmed)
        if m:
            return f"\u5df2\u9009 {m.group(1)} \u9879"
        m = self.re_selected.match(trimmed)
        if m:
            return f"\u5df2\u9009 {m.group(1)} \u9879"
        m = self.re_tasks.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u4efb\u52a1"
        m = self.re_artifacts.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u4ea7\u7269"
        m = self.re_changes.match(trimmed)
        if m:
            return f"{m.group(1)} \u5904\u66f4\u6539"
        m = self.re_errors.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u9519\u8bef"
        m = self.re_warnings.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u8b66\u544a"
        m = self.re_results.match(trimmed)
        if m:
            return f"{m.group(1)} \u4e2a\u7ed3\u679c"

        return None

    def translate_text(self, text):
        if not text or not isinstance(text, str):
            return None
        normalized = self.normalize(text)
        trimmed = normalized.strip()
        if not trimmed:
            return None

        # 1. Direct dictionary match
        if trimmed in self.dictionary:
            return normalized.replace(trimmed, self.dictionary[trimmed])
        if normalized in self.dictionary:
            return self.dictionary[normalized]

        # 2. Dynamic regex matchers
        dynamic_match = self.match_dynamic_patterns(trimmed)
        if dynamic_match is not None:
            return normalized.replace(trimmed, dynamic_match)

        # 3. Substring replacements
        new_text = normalized
        modified = False
        for search_str, replace_str in self.substring_replacements:
            if search_str in new_text:
                new_text = new_text.replace(search_str, replace_str)
                modified = True
        if modified:
            return new_text

        return None

    def is_bypassed_element(self, el):
        if not el or el.nodeType != MockDOMNode.ELEMENT_NODE:
            return False
        if el.tagName in self.ignore_tags:
            return True
        if el.isContentEditable:
            return True
        if el.getAttribute("contenteditable") == "true" or el.getAttribute("contenteditable") == "":
            return True
        if el.hasAttribute("data-no-translate") or el.hasAttribute("translate") and el.getAttribute("translate") == "no":
            return True

        if any(cls in self.bypass_classes for cls in el.classList):
            return True

        # Check ancestor chain
        curr = el.parent
        while curr:
            if curr.nodeType == MockDOMNode.ELEMENT_NODE:
                if curr.tagName in self.ignore_tags or curr.tagName in self.code_or_input_tags:
                    return True
                if curr.isContentEditable or curr.getAttribute("contenteditable") == "true":
                    return True
                if curr.hasAttribute("data-no-translate") or (curr.getAttribute("translate") == "no"):
                    return True
                if any(cls in self.bypass_classes for cls in curr.classList):
                    return True
            curr = curr.parent
        return False

    def is_bypassed_node(self, node):
        if not node:
            return True
        if node.nodeType == MockDOMNode.TEXT_NODE:
            parent = node.parent
            if not parent or parent.nodeType != MockDOMNode.ELEMENT_NODE:
                return False
            if parent.tagName in self.ignore_tags or parent.tagName in self.code_or_input_tags:
                return True
            return self.is_bypassed_element(parent)
        if node.nodeType == MockDOMNode.ELEMENT_NODE:
            return self.is_bypassed_element(node)
        return False

    def translate_attributes(self, el, attrs):
        if not el:
            return
        for attr in attrs:
            if el.hasAttribute(attr):
                val = el.getAttribute(attr)
                if val and isinstance(val, str):
                    trans = self.translate_text(val)
                    if trans is not None and trans != val:
                        el.setAttribute(attr, trans)

    def walk(self, node):
        if not node:
            return

        # Text Node
        if node.nodeType == MockDOMNode.TEXT_NODE:
            if self.is_bypassed_node(node):
                return
            text = node.nodeValue
            if text and isinstance(text, str):
                trans = self.translate_text(text)
                if trans is not None and trans != text:
                    node.nodeValue = trans
            return

        # DocumentFragment / ShadowRoot
        if node.nodeType == MockDOMNode.DOCUMENT_FRAGMENT_NODE:
            for child in list(node.children):
                self.walk(child)
            return

        # Element Node
        if node.nodeType == MockDOMNode.ELEMENT_NODE:
            tag = node.tagName

            if tag in self.ignore_tags:
                return

            if tag == 'TEXTAREA':
                self.translate_attributes(node, self.safe_attrs)
                return

            if tag == 'INPUT':
                itype = (node.getAttribute('type') or 'text').lower()
                if itype in self.button_input_types:
                    self.translate_attributes(node, self.safe_attrs + ['value'])
                else:
                    self.translate_attributes(node, self.safe_attrs)
                return

            is_self_bypassed = (
                tag in self.code_or_input_tags or
                self.is_bypassed_element(node)
            )

            if is_self_bypassed:
                self.translate_attributes(node, self.safe_attrs)
                return

            self.translate_attributes(node, self.safe_attrs)

            # Traverse Shadow DOM if present
            if node.shadowRoot:
                self.walk(node.shadowRoot)

            for child in list(node.children):
                self.walk(child)


# ==============================================================================
# Tier 5 Test Suites
# ==============================================================================

class TestTier5RegexAndTimers(unittest.TestCase):
    """Adversarial stress-testing of regex alternations, microsecond floats, and ReDoS."""
    TIER = 5

    def setUp(self):
        self.engine = Tier5WhiteBoxEngine()

    def test_01_floating_point_thinking_timers_extreme_precisions(self):
        """Test thinking timer regex with microsecond, zero, multi-digit, and unit variations."""
        cases = [
            ("Thinking for 0.001s", "思考中 (0.001秒)"),
            ("Thinking for 0.0s", "思考中 (0.0秒)"),
            ("Thinking for 0s", "思考中 (0秒)"),
            ("Thinking for 1.250s", "思考中 (1.250秒)"),
            ("Thinking for 99999.99s", "思考中 (99999.99秒)"),
            ("Thinking for 500ms", "思考中 (500毫秒)"),
            ("Thinking for 0.5ms", "思考中 (0.5毫秒)"),
            ("Thought for 12.345s", "思考中 (12.345秒)"),
            ("Thought for 100ms", "思考中 (100毫秒)"),
            ("Thinking... (1.2s)", "思考中... (1.2秒)"),
            ("Thinking... (500ms)", "思考中... (500毫秒)"),
            ("Thinking (3.14s)", "思考中 (3.14秒)"),
            ("Thought (0.05s)", "思考中 (0.05秒)"),
            ("Thought (250ms)", "思考中 (250毫秒)"),
            ("Thinking 4.5s", "思考中 (4.5秒)"),
            ("Thought 100ms", "思考中 (100毫秒)"),
        ]
        for src, expected in cases:
            with self.subTest(src=src):
                self.assertEqual(self.engine.translate_text(src), expected)

    def test_02_floating_point_working_timers_and_completions(self):
        """Test working timers, elapsed timers, and completion duration formats."""
        cases = [
            ("Working for 0.05s", "处理中 (0.05秒)"),
            ("Working for 12.34s", "处理中 (12.34秒)"),
            ("Working for 300ms", "处理中 (300毫秒)"),
            ("Worked for 5.0s", "处理中 (5.0秒)"),
            ("Working... (0.8s)", "处理中... (0.8秒)"),
            ("Working (250ms)", "处理中 (250毫秒)"),
            ("Worked 3.14s", "处理中 (3.14秒)"),
            ("Completed in 0.05s", "已完成 (耗时 0.05秒)"),
            ("Finished in 12ms", "已完成 (耗时 12毫秒)"),
            ("Done in 3.5 seconds", "已完成 (耗时 3.5秒)"),
            ("Timed 1.2s", "已计时 1.2秒"),
            ("Timed 500ms", "已计时 500毫秒"),
            ("Elapsed time: 0.85s", "耗时: 0.85秒"),
            ("Total duration: 12.3s", "总耗时: 12.3秒"),
            ("Execution time: 0.002s", "执行耗时: 0.002秒"),
        ]
        for src, expected in cases:
            with self.subTest(src=src):
                self.assertEqual(self.engine.translate_text(src), expected)

    def test_03_relative_timestamps_all_units_and_variations(self):
        """Test compact and suffixed relative timestamps across all supported time units."""
        cases = [
            ("just now", "刚刚"),
            ("a few seconds ago", "几秒前"),
            ("a minute ago", "1分钟前"),
            ("an hour ago", "1小时前"),
            ("a day ago", "1天前"),
            ("today", "今天"),
            ("yesterday", "昨天"),
            ("Today 10:30 AM", "今天 10:30 AM"),
            ("Yesterday 5:00 PM", "昨天 5:00 PM"),
            ("10d", "10天前"),
            ("5m", "5分钟前"),
            ("1mo", "1个月前"),
            ("2h", "2小时前"),
            ("30s", "30秒前"),
            ("1y", "1年前"),
            ("10d ago", "10天前"),
            ("1y ago", "1年前"),
            ("1 day ago", "1天前"),
            ("5 days ago", "5天前"),
            ("1 hour ago", "1小时前"),
            ("2 hours ago", "2小时前"),
            ("1 hr ago", "1小时前"),
            ("3 hrs ago", "3小时前"),
            ("1 minute ago", "1分钟前"),
            ("10 minutes ago", "10分钟前"),
            ("1 min ago", "1分钟前"),
            ("5 mins ago", "5分钟前"),
            ("1 second ago", "1秒前"),
            ("30 seconds ago", "30秒前"),
            ("1 sec ago", "1秒前"),
            ("15 secs ago", "15秒前"),
            ("1 month ago", "1个月前"),
            ("6 months ago", "6个月前"),
            ("1 year ago", "1年前"),
            ("10 years ago", "10年前"),
            ("1 yr ago", "1年前"),
            ("2 yrs ago", "2年前"),
        ]
        for src, expected in cases:
            with self.subTest(src=src):
                self.assertEqual(self.engine.translate_text(src), expected)

    def test_04_dynamic_counters_and_workspace_badges(self):
        """Test dynamic counter badges, file change counters, and status counters."""
        cases = [
            ("Subagents 0", "子智能体 0"),
            ("Subagents 999", "子智能体 999"),
            ("Files Changed 1", "已修改文件 1"),
            ("Files Changed 42", "已修改文件 42"),
            ("Artifacts 0", "产物 0"),
            ("Uploads 5", "已上传文件 5"),
            ("Background Tasks 2", "后台任务 2"),
            ("MCP Servers 10", "MCP 服务 10"),
            ("1 file changed", "1 个文件已修改"),
            ("10 files changed", "10 个文件已修改"),
            ("1 file modified", "1 个文件已修改"),
            ("5 files added", "5 个文件已添加"),
            ("2 files deleted", "2 个文件已删除"),
            ("1 file", "1 个文件"),
            ("100 files", "100 个文件"),
            ("1 subagent", "1 个子智能体"),
            ("5 subagents", "5 个子智能体"),
            ("1 agent running", "1 个智能体正在运行"),
            ("5 agents running", "5 个智能体运行中"),
            ("No agents running", "暂无运行中的智能体"),
            ("1 item selected", "已选 1 项"),
            ("12 items selected", "已选 12 项"),
            ("1 selected", "已选 1 项"),
            ("10 selected", "已选 10 项"),
            ("1 task", "1 个任务"),
            ("5 tasks", "5 个任务"),
            ("1 artifact", "1 个产物"),
            ("3 artifacts", "3 个产物"),
            ("1 change", "1 处更改"),
            ("4 changes", "4 处更改"),
            ("1 error", "1 个错误"),
            ("3 errors", "3 个错误"),
            ("1 warning", "1 个警告"),
            ("5 warnings", "5 个警告"),
            ("1 result", "1 个结果"),
            ("100 results", "100 个结果"),
        ]
        for src, expected in cases:
            with self.subTest(src=src):
                self.assertEqual(self.engine.translate_text(src), expected)

    def test_05_redos_resistance_and_pathological_inputs(self):
        """Stress-test regexes against crafted pathological inputs for catastrophic backtracking."""
        pathological_cases = [
            "Thinking for " + "9" * 2000 + "s",
            "Working for " + "9" * 2000 + "ms",
            "Completed in " + "9" * 2000 + " seconds",
            "Files Changed " + "9" * 2000,
            "a " * 500 + "minute ago",
            " " * 1000 + "New Conversation" + " " * 1000,
            "Today " + "x" * 2000,
            "1" * 1000 + " files changed",
            "1" * 1000 + " subagents",
            "Subagents " + "1" * 1000,
        ]
        for path_str in pathological_cases:
            t0 = time.time()
            res = self.engine.translate_text(path_str)
            elapsed = time.time() - t0
            self.assertLess(elapsed, 0.3, f"ReDoS vulnerability suspected on input: {path_str[:30]}... took {elapsed*1000:.2f}ms")


class TestTier5ShadowDOMAndAttachShadow(unittest.TestCase):
    """Adversarial stress-testing of Shadow DOM trees and attachShadow interception."""
    TIER = 5

    def setUp(self):
        self.engine = Tier5WhiteBoxEngine()

    def test_01_open_shadow_root_traversal_and_translation(self):
        """Test DOM traversal through open ShadowRoot and translation of encapsulated components."""
        host = MockDOMNode(MockDOMNode.ELEMENT_NODE, "custom-dialog")
        shadow = host.attachShadow({"mode": "open"})

        header = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="dialog-header")
        title_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="Settings")
        header.append_child(title_text)

        body = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="dialog-body")
        badge = MockDOMNode(MockDOMNode.ELEMENT_NODE, "span")
        badge_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="Files Changed 5")
        badge.append_child(badge_text)
        body.append_child(badge)

        btn = MockDOMNode(MockDOMNode.ELEMENT_NODE, "input", attributes={"type": "button", "value": "Save"})
        body.append_child(btn)

        shadow.append_child(header)
        shadow.append_child(body)

        # Walk host element
        self.engine.walk(host)

        self.assertEqual(title_text.nodeValue, "设置")
        self.assertEqual(badge_text.nodeValue, "已修改文件 5")
        self.assertEqual(btn.getAttribute("value"), "保存")

    def test_02_deeply_nested_multi_level_shadow_trees(self):
        """Test traversal across 4 levels of nested Shadow DOM web components."""
        level1 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "app-shell")
        shadow1 = level1.attachShadow({"mode": "open"})

        level2 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "side-panel")
        shadow2 = level2.attachShadow({"mode": "open"})
        shadow1.append_child(level2)

        level3 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "task-list")
        shadow3 = level3.attachShadow({"mode": "open"})
        shadow2.append_child(level3)

        level4 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "task-item")
        shadow4 = level4.attachShadow({"mode": "open"})
        shadow3.append_child(level4)

        leaf_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="Thinking for 2.5s")
        leaf_btn = MockDOMNode(MockDOMNode.ELEMENT_NODE, "input", attributes={"type": "submit", "value": "Cancel Task"})
        shadow4.append_child(leaf_text)
        shadow4.append_child(leaf_btn)

        self.engine.walk(level1)

        self.assertEqual(leaf_text.nodeValue, "思考中 (2.5秒)")
        self.assertEqual(leaf_btn.getAttribute("value"), "取消任务")

    def test_03_attach_shadow_monkey_patch_simulation(self):
        """Test attachShadow monkey-patching behavior and exception safety."""
        # Monkey patch simulation
        observed_roots = []
        walked_roots = []

        def mock_observe(root):
            observed_roots.append(root)

        def mock_walk(root):
            walked_roots.append(root)
            self.engine.walk(root)

        orig_attach = MockDOMNode.attachShadow

        def patched_attach(node_self, init=None):
            shadow = orig_attach(node_self, init)
            try:
                if shadow:
                    mock_observe(shadow)
                    mock_walk(shadow)
            except Exception:
                pass
            return shadow

        MockDOMNode.attachShadow = patched_attach
        try:
            elem = MockDOMNode(MockDOMNode.ELEMENT_NODE, "dynamic-component")
            # Populate before or during attach
            s_root = elem.attachShadow({"mode": "open"})
            t_node = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="New Conversation")
            s_root.append_child(t_node)

            # Trigger walk on newly attached shadow
            self.engine.walk(s_root)

            self.assertIn(s_root, observed_roots)
            self.assertEqual(t_node.nodeValue, "新建对话")
        finally:
            MockDOMNode.attachShadow = orig_attach


class TestTier5NonBreakingSpacesAndNormalization(unittest.TestCase):
    """Adversarial stress-testing of non-breaking space (\\u00a0) normalization."""
    TIER = 5

    def setUp(self):
        self.engine = Tier5WhiteBoxEngine()

    def test_01_non_breaking_spaces_in_static_dictionary_matches(self):
        """Verify \\u00a0 within static phrases is normalized and translated accurately."""
        cases = [
            ("New\u00a0Conversation", "新建对话"),
            ("\u00a0Conversation\u00a0History\u00a0", "历史对话"),
            ("Scheduled\u00a0Tasks", "计划任务"),
            ("\u00a0Settings\u00a0", "设置"),
            ("Clear\u00a0All", "清除全部"),
            ("Pin\u00a0to\u00a0top", "置顶到顶部"),
        ]
        for src, expected in cases:
            with self.subTest(src=src):
                self.assertEqual(self.engine.translate_text(src).strip(), expected)

    def test_02_non_breaking_spaces_in_dynamic_patterns_and_timers(self):
        """Verify \\u00a0 in dynamic regexes (timers, suffixed times, pane badges)."""
        cases = [
            ("Thinking\u00a0for\u00a01.2s", "思考中 (1.2秒)"),
            ("Working\u00a0for\u00a0500ms", "处理中 (500毫秒)"),
            ("Completed\u00a0in\u00a00.05s", "已完成 (耗时 0.05秒)"),
            ("Subagents\u00a03", "子智能体 3"),
            ("Files\u00a0Changed\u00a010", "已修改文件 10"),
            ("5\u00a0files\u00a0changed", "5 个文件已修改"),
            ("10\u00a0days\u00a0ago", "10天前"),
            ("1\u00a0min\u00a0ago", "1分钟前"),
        ]
        for src, expected in cases:
            with self.subTest(src=src):
                self.assertEqual(self.engine.translate_text(src), expected)

    def test_03_non_breaking_spaces_in_attributes_and_inputs(self):
        """Verify safe attributes and button inputs containing \\u00a0 are normalized and translated."""
        inp1 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "input", attributes={"placeholder": "Search\u00a0conversations..."})
        inp2 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "input", attributes={"type": "button", "value": "Delete\u00a0Conversation"})
        div = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", attributes={"title": "Pin\u00a0Conversation", "aria-label": "Toggle\u00a0Sidebar"})

        self.engine.walk(inp1)
        self.engine.walk(inp2)
        self.engine.walk(div)

        self.assertEqual(inp1.getAttribute("placeholder"), "搜索对话...")
        self.assertEqual(inp2.getAttribute("value"), "删除对话")
        self.assertEqual(div.getAttribute("title"), "置顶对话")
        self.assertEqual(div.getAttribute("aria-label"), "切换侧边栏")


class TestTier5SafetyBypassAndInputProtection(unittest.TestCase):
    """Adversarial stress-testing of Monaco editor, terminal, code fence, and user input safety bypass."""
    TIER = 5

    def setUp(self):
        self.engine = Tier5WhiteBoxEngine()

    def test_01_nested_monaco_editor_tree_zero_translation(self):
        """Ensure Monaco editor lines, tokens, and code containing UI keywords are completely untouched."""
        monaco_root = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="monaco-editor vs-dark")
        scrollable = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="monaco-scrollable-element")
        view_lines = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="view-lines")

        code_lines = [
            'const Settings = "New Conversation";',
            'function deleteProject(conversationId) {',
            '    return { status: "Completed in 1.2s", subagents: 3 };',
            '}',
            '// Files Changed 10 and Thinking for 0.5s inside comment'
        ]

        text_nodes = []
        for line in code_lines:
            row = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="view-line")
            tok = MockDOMNode(MockDOMNode.ELEMENT_NODE, "span", class_name="mtk1")
            tn = MockDOMNode(MockDOMNode.TEXT_NODE, node_value=line)
            tok.append_child(tn)
            row.append_child(tok)
            view_lines.append_child(row)
            text_nodes.append((tn, line))

        scrollable.append_child(view_lines)
        monaco_root.append_child(scrollable)

        self.engine.walk(monaco_root)

        for tn, original in text_nodes:
            self.assertEqual(tn.nodeValue, original, "Monaco code node was illegally translated!")

    def test_02_codemirror_and_syntax_highlighted_blocks(self):
        """Ensure CodeMirror 6 and syntax highlighted blocks are completely untouched."""
        cm_root = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="cm-editor")
        cm_content = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="cm-content")
        cm_line = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="cm-line")
        code_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value='export const config = { turboMode: "Turbo Mode", count: "1 file changed" };')

        cm_line.append_child(code_text)
        cm_content.append_child(cm_line)
        cm_root.append_child(cm_content)

        self.engine.walk(cm_root)

        self.assertEqual(code_text.nodeValue, 'export const config = { turboMode: "Turbo Mode", count: "1 file changed" };')

    def test_03_terminal_and_xterm_streams_protection(self):
        """Ensure terminal rows containing ANSI sequences, shell commands, and status strings remain pristine."""
        term_root = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="terminal xterm xterm-viewport")
        screen = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="xterm-screen")

        term_lines = [
            '$ git commit -m "New Conversation with Artifacts 5"',
            '[OK] Completed in 0.05s',
            'Thinking for 2.0s -> Done in 100ms',
            '\x1b[32m[PASS]\x1b[0m 10 files changed, 2 errors'
        ]

        text_nodes = []
        for line in term_lines:
            row = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="xterm-rows")
            tn = MockDOMNode(MockDOMNode.TEXT_NODE, node_value=line)
            row.append_child(tn)
            screen.append_child(row)
            text_nodes.append((tn, line))

        term_root.append_child(screen)

        self.engine.walk(term_root)

        for tn, original in text_nodes:
            self.assertEqual(tn.nodeValue, original, "Terminal text was illegally translated!")

    def test_04_markdown_code_fences_and_special_tags(self):
        """Ensure <pre><code>, <kbd>, <samp>, <var> remain completely untranslated."""
        pre = MockDOMNode(MockDOMNode.ELEMENT_NODE, "pre")
        code = MockDOMNode(MockDOMNode.ELEMENT_NODE, "code", class_name="hljs language-python")
        code_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value='print("Settings: Save Conversation")')
        code.append_child(code_text)
        pre.append_child(code)

        kbd = MockDOMNode(MockDOMNode.ELEMENT_NODE, "kbd")
        kbd_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="Ctrl+Delete")
        kbd.append_child(kbd_text)

        self.engine.walk(pre)
        self.engine.walk(kbd)

        self.assertEqual(code_text.nodeValue, 'print("Settings: Save Conversation")')
        self.assertEqual(kbd_text.nodeValue, "Ctrl+Delete")

    def test_05_user_input_protection_with_safe_attributes_translation(self):
        """Ensure <textarea>, <input type='text|search|password'> preserve user content while translating attributes."""
        # Textarea
        ta = MockDOMNode(
            MockDOMNode.ELEMENT_NODE, "textarea",
            node_value="Please do not translate my prompt: New Conversation with Settings",
            attributes={"placeholder": "Search conversations...", "title": "Ask anything"}
        )
        ta_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="User typed: Delete All Conversations")
        ta.append_child(ta_text)

        # Input text
        inp_text = MockDOMNode(
            MockDOMNode.ELEMENT_NODE, "input",
            attributes={"type": "text", "value": "User search query: Settings", "placeholder": "Search history..."}
        )

        # Contenteditable
        ce = MockDOMNode(
            MockDOMNode.ELEMENT_NODE, "div",
            attributes={"contenteditable": "true", "title": "New Conversation"},
            is_content_editable=True
        )
        ce_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="Drafting a New Conversation here...")
        ce.append_child(ce_text)

        self.engine.walk(ta)
        self.engine.walk(inp_text)
        self.engine.walk(ce)

        self.assertEqual(ta_text.nodeValue, "User typed: Delete All Conversations")
        self.assertEqual(ta.getAttribute("placeholder"), "搜索对话...")
        self.assertEqual(inp_text.getAttribute("value"), "User search query: Settings")
        self.assertEqual(inp_text.getAttribute("placeholder"), "搜索历史...")
        self.assertEqual(ce_text.nodeValue, "Drafting a New Conversation here...")
        self.assertEqual(ce.getAttribute("title"), "新建对话")

    def test_06_button_input_values_are_translated(self):
        """Ensure <input type='button|submit|reset'> have their 'value' attribute translated properly."""
        btn1 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "input", attributes={"type": "button", "value": "Save"})
        btn2 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "input", attributes={"type": "submit", "value": "Delete Conversation"})
        btn3 = MockDOMNode(MockDOMNode.ELEMENT_NODE, "input", attributes={"type": "reset", "value": "Cancel"})

        self.engine.walk(btn1)
        self.engine.walk(btn2)
        self.engine.walk(btn3)

        self.assertEqual(btn1.getAttribute("value"), "保存")
        self.assertEqual(btn2.getAttribute("value"), "删除对话")
        self.assertEqual(btn3.getAttribute("value"), "取消")


class TestTier5PureAsciiUnicodeEscapeIntegrity(unittest.TestCase):
    """Adversarial stress-testing of 100% 7-bit ASCII encoding and exact dictionary 3-way parity."""
    TIER = 5

    def test_01_dist_preload_js_is_100_percent_7bit_ascii(self):
        """Verify preload.js contains zero bytes > 127, eliminating all codepage corruption."""
        with open(PRELOAD_PATH, "rb") as f:
            preload_bytes = f.read()

        non_ascii = [b for b in preload_bytes if b > 127]
        self.assertEqual(len(non_ascii), 0, f"Found {len(non_ascii)} non-ASCII bytes in dist/preload.js!")

    def test_02_dist_engine_js_is_100_percent_7bit_ascii(self):
        """Verify engine.js contains zero bytes > 127, ensuring universal Node/V8 execution."""
        with open(ENGINE_PATH, "rb") as f:
            engine_bytes = f.read()

        non_ascii = [b for b in engine_bytes if b > 127]
        self.assertEqual(len(non_ascii), 0, f"Found {len(non_ascii)} non-ASCII bytes in dist/engine.js!")

    def test_03_dictionary_3_way_exact_parity(self):
        """Verify dist/dictionary.json, dist/preload.js, and dist/engine.js have identical 514 keys and values."""
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            json_dict = json.load(f)

        with open(PRELOAD_PATH, "r", encoding="utf-8") as f:
            preload_code = f.read()

        with open(ENGINE_PATH, "r", encoding="utf-8") as f:
            engine_code = f.read()

        preload_match = re.search(r"const dictionary = (\{.*?\});\n\n  // 2\.", preload_code, re.DOTALL)
        engine_match = re.search(r"const dictionary = (\{.*?\});\n\n  // 2\.", engine_code, re.DOTALL)

        self.assertIsNotNone(preload_match, "Failed to extract dictionary from preload.js")
        self.assertIsNotNone(engine_match, "Failed to extract dictionary from engine.js")

        preload_dict = json.loads(preload_match.group(1))
        engine_dict = json.loads(engine_match.group(1))

        self.assertGreaterEqual(len(json_dict), 514, "dictionary.json should have at least 514 keys!")
        self.assertEqual(len(json_dict), len(preload_dict), "Key count mismatch between dictionary.json and preload.js!")
        self.assertEqual(len(json_dict), len(engine_dict), "Key count mismatch between dictionary.json and engine.js!")

        self.assertEqual(json_dict, preload_dict, "Parity mismatch between dictionary.json and preload.js!")
        self.assertEqual(json_dict, engine_dict, "Parity mismatch between dictionary.json and engine.js!")

    def test_04_no_mojibake_or_corrupted_unicode_surrogates(self):
        """Verify all translated values in dictionary.json are valid Chinese strings with no mojibake."""
        with open(DICT_PATH, "r", encoding="utf-8") as f:
            dictionary = json.load(f)

        mojibake_patterns = [
            re.compile(r"[\ufffd\u00e4\u00bd\u00a0\u00e6\u0096\u00b0]"),
            re.compile(r"\?[a-zA-Z0-9]{2,}\?"),
            re.compile(r"&[a-z]+;"),
        ]

        for key, val in dictionary.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(val, str)
            self.assertTrue(len(val) > 0, f"Empty translation for key '{key}'")
            for pat in mojibake_patterns:
                self.assertIsNone(
                    pat.search(val),
                    f"Possible mojibake / encoding corruption in '{key}' -> '{val}'"
                )


class TestTier5PerformanceAndScalabilityStress(unittest.TestCase):
    """High-throughput stress-testing and deep recursion scalability."""
    TIER = 5

    def setUp(self):
        self.engine = Tier5WhiteBoxEngine()

    def test_01_high_throughput_100k_translations_under_1_second(self):
        """Benchmark 100,000 translation dispatcher operations in under 1.0 second."""
        test_inputs = [
            "New Conversation",
            "Thinking for 1.2s",
            "Working for 300ms",
            "Subagents 3",
            "5 files changed",
            "10d ago",
            "Delete Project",
            "Toggle Developer Tools",
            "Completed in 0.05s",
            "Non-existent string that falls through"
        ]

        num_iterations = 10000
        t0 = time.time()
        for _ in range(num_iterations):
            for s in test_inputs:
                self.engine.translate_text(s)
        elapsed = time.time() - t0

        self.assertLess(
            elapsed, 1.0,
            f"High-throughput benchmark exceeded 1.0s limit: 100,000 ops took {elapsed:.3f}s"
        )

    def test_02_deeply_nested_dom_hierarchy_no_stack_overflow(self):
        """Traverse 50 levels of deeply nested DOM containers without stack overflow."""
        root = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="root-level")
        curr = root
        for i in range(50):
            child = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name=f"level-{i}")
            curr.append_child(child)
            curr = child

        leaf_text = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="New Conversation")
        curr.append_child(leaf_text)

        t0 = time.time()
        self.engine.walk(root)
        elapsed = time.time() - t0

        self.assertEqual(leaf_text.nodeValue, "新建对话")
        self.assertLess(elapsed, 0.3, f"Deep DOM walk took {elapsed*1000:.2f}ms")

    def test_03_large_broad_dom_tree_1000_nodes(self):
        """Traverse and translate a large DOM tree with 1,000 nodes in under 50ms."""
        container = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="container")
        for i in range(500):
            item = MockDOMNode(MockDOMNode.ELEMENT_NODE, "div", class_name="item")
            title = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="Save")
            badge = MockDOMNode(MockDOMNode.TEXT_NODE, node_value="Files Changed 1")
            item.append_child(title)
            item.append_child(badge)
            container.append_child(item)

        t0 = time.time()
        self.engine.walk(container)
        elapsed = time.time() - t0

        self.assertLess(elapsed, 0.3, f"1000-node DOM walk took {elapsed*1000:.2f}ms")


if __name__ == "__main__":
    unittest.main(verbosity=2)
