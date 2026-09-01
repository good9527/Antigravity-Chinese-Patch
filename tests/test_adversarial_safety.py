#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_adversarial_safety.py
Milestone 1 Challenger 2: Adversarial Safety Bypass & Sandbox Isolation Test Suite.

Empirically challenges:
1. Complex nested Monaco Editor trees containing code keywords (0% translation).
2. Complex Markdown code fences (<pre><code class="hljs">) with code keywords and timers.
3. High-frequency terminal streams (.xterm-rows with ANSI sequences).
4. User input interactions (<textarea>, <input type="text">, [contenteditable]) protecting user text while translating placeholder/title.
5. Button input value labels (<input type="submit|button|reset">) translating value labels properly.
"""

import unittest
import os
import sys
import json
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.test_engine import MockNode, SpecificationTranslationEngine

DICT_PATH = os.path.join(PROJECT_ROOT, "dist", "dictionary.json")
with open(DICT_PATH, "r", encoding="utf-8") as f:
    DICTIONARY = json.load(f)


class AdversarialSafetyEngine(SpecificationTranslationEngine):
    """Enhanced specification engine matching dist/engine.js behavior precisely."""

    def __init__(self):
        super().__init__(dictionary=DICTIONARY)
        self.button_input_types = {"button", "submit", "reset"}

    def walk(self, node):
        if not node:
            return
        if node.nodeType == MockNode.TEXT_NODE:
            if node.parent and self.should_bypass_element(node.parent):
                return
            trans = self.translate_text(node.nodeValue)
            if trans is not None and trans != node.nodeValue:
                node.nodeValue = trans
        elif node.nodeType == MockNode.ELEMENT_NODE:
            tag = node.tagName.lower() if node.tagName else ""

            # Check if self is bypassed
            if self.should_bypass_element(node):
                # Translate safe attributes on bypassed container itself
                for attr in ["placeholder", "title", "aria-label"]:
                    if node.hasAttribute(attr):
                        val = node.getAttribute(attr)
                        trans = self.translate_text(val)
                        if trans is not None and trans != val:
                            node.setAttribute(attr, trans)
                return

            # Translate safe attributes
            for attr in ["placeholder", "title", "aria-label"]:
                if node.hasAttribute(attr):
                    val = node.getAttribute(attr)
                    trans = self.translate_text(val)
                    if trans is not None and trans != val:
                        node.setAttribute(attr, trans)

            # Input element handling
            if tag == "input":
                itype = (node.getAttribute("type") or "text").lower()
                if itype in self.button_input_types:
                    if node.hasAttribute("value"):
                        val = node.getAttribute("value")
                        trans = self.translate_text(val)
                        if trans is not None and trans != val:
                            node.setAttribute("value", trans)
                return

            # Textarea handling
            if tag == "textarea" or node.isContentEditable:
                return

            for child in list(node.children):
                self.walk(child)


class TestAdversarialMonacoEditor(unittest.TestCase):
    """Adversarial stress test on Monaco editor and CodeMirror code trees."""

    def setUp(self):
        self.engine = AdversarialSafetyEngine()

    def test_nested_monaco_tree_with_code_keywords(self):
        """Monaco editor tree with keywords: const Settings = 'Close'; function deleteConversation() { return 'Save'; }"""
        root = MockNode(MockNode.ELEMENT_NODE, "div", class_name="monaco-editor vs-dark")
        scrollable = MockNode(MockNode.ELEMENT_NODE, "div", class_name="monaco-scrollable-element")
        view_lines = MockNode(MockNode.ELEMENT_NODE, "div", class_name="view-lines")

        lines_code = [
            'const Settings = "Close";',
            'function deleteConversation(id) {',
            '    const status = "Thinking for 2.5s";',
            '    if (id === "Files Changed") {',
            '        return "Save";',
            '    }',
            '    return "Cancel";',
            '}',
            '// Subagents 5, Completed in 3.4s, 10 files changed'
        ]

        text_nodes = []
        for code_str in lines_code:
            line_div = MockNode(MockNode.ELEMENT_NODE, "div", class_name="view-line")
            t_node = MockNode(MockNode.TEXT_NODE, node_value=code_str)
            text_nodes.append((t_node, code_str))
            line_div.append_child(t_node)
            view_lines.append_child(line_div)

        scrollable.append_child(view_lines)
        root.append_child(scrollable)

        # Run DOM translation pass
        self.engine.walk(root)

        # Verify 0% code translation across all text nodes
        for t_node, original_str in text_nodes:
            self.assertEqual(
                t_node.nodeValue, original_str,
                f"Monaco code corruption detected: expected '{original_str}', got '{t_node.nodeValue}'"
            )

    def test_monaco_tokenized_spans(self):
        """Monaco syntax-highlighted tokens inside view-line must remain untouched."""
        root = MockNode(MockNode.ELEMENT_NODE, "div", class_name="monaco-editor")
        line = MockNode(MockNode.ELEMENT_NODE, "div", class_name="view-line")
        
        tokens = [
            ("span", "mtk1", "const "),
            ("span", "mtk4", "Settings"),
            ("span", "mtk1", " = "),
            ("span", "mtk5", '"Delete All Conversations"'),
            ("span", "mtk1", ";")
        ]
        
        nodes = []
        for tag, cls, val in tokens:
            span = MockNode(MockNode.ELEMENT_NODE, tag, class_name=cls)
            t = MockNode(MockNode.TEXT_NODE, node_value=val)
            span.append_child(t)
            line.append_child(span)
            nodes.append((t, val))

        root.append_child(line)
        self.engine.walk(root)

        for t, expected_val in nodes:
            self.assertEqual(t.nodeValue, expected_val)


class TestAdversarialMarkdownCodeFences(unittest.TestCase):
    """Adversarial stress test on Markdown code fences and syntax highlighting."""

    def setUp(self):
        self.engine = AdversarialSafetyEngine()

    def test_markdown_code_fences_with_ui_keywords(self):
        """<pre><code class="hljs">let x = "Files Changed";</code></pre> must not be translated."""
        container = MockNode(MockNode.ELEMENT_NODE, "div", class_name="markdown-body")
        
        # UI Heading before code fence
        h2 = MockNode(MockNode.ELEMENT_NODE, "h2")
        h2_text = MockNode(MockNode.TEXT_NODE, node_value="New Conversation")
        h2.append_child(h2_text)
        container.append_child(h2)

        # Code fence with various UI keywords
        pre = MockNode(MockNode.ELEMENT_NODE, "pre")
        code = MockNode(MockNode.ELEMENT_NODE, "code", class_name="hljs language-javascript")
        code_str = (
            'let x = "Files Changed";\n'
            'const config = { "Settings": "Strict Mode", "Save": true };\n'
            '// Thinking for 1.2s ... Working for 3.4s\n'
            'function stopTask() { return "Done in 5s"; }'
        )
        code_text = MockNode(MockNode.TEXT_NODE, node_value=code_str)
        code.append_child(code_text)
        pre.append_child(code)
        container.append_child(pre)

        # UI Button after code fence
        btn = MockNode(MockNode.ELEMENT_NODE, "button")
        btn_text = MockNode(MockNode.TEXT_NODE, node_value="Delete Conversation")
        btn.append_child(btn_text)
        container.append_child(btn)

        self.engine.walk(container)

        # 1. UI elements ARE translated
        self.assertEqual(h2_text.nodeValue, "新建对话")
        self.assertEqual(btn_text.nodeValue, "删除对话")

        # 2. Code fence is 0% translated
        self.assertEqual(code_text.nodeValue, code_str)
        self.assertNotIn("已修改文件", code_text.nodeValue)
        self.assertNotIn("设置", code_text.nodeValue)
        self.assertNotIn("思考中", code_text.nodeValue)


class TestAdversarialHighFrequencyTerminalStreams(unittest.TestCase):
    """Adversarial stress test on xterm terminal streams with ANSI escapes."""

    def setUp(self):
        self.engine = AdversarialSafetyEngine()

    def test_terminal_ansi_streams_with_keywords(self):
        """Terminal rows with ANSI escape sequences and UI words must not be modified."""
        term = MockNode(MockNode.ELEMENT_NODE, "div", class_name="terminal xterm xterm-screen")
        rows = MockNode(MockNode.ELEMENT_NODE, "div", class_name="xterm-rows")
        term.append_child(rows)

        lines = [
            "\x1b[32m[SUCCESS]\x1b[0m Save file: /app/src/main.ts",
            "\x1b[31;1m[ERROR]\x1b[0m Failed Tasks: 3, Delete Conversation aborted",
            "\x1b[33m[WARN]\x1b[0m Files Changed 10, Subagents 3 active",
            "\x1b[36m[STATE]\x1b[0m Thinking for 3.2s | Working for 1.1s",
            "\x1b[1;34mCompleted in 15.2s\x1b[0m"
        ]

        text_nodes = []
        for line_str in lines:
            row_div = MockNode(MockNode.ELEMENT_NODE, "div", class_name="xterm-row")
            t = MockNode(MockNode.TEXT_NODE, node_value=line_str)
            row_div.append_child(t)
            rows.append_child(row_div)
            text_nodes.append((t, line_str))

        self.engine.walk(term)

        for t, orig_str in text_nodes:
            self.assertEqual(t.nodeValue, orig_str)
            self.assertIn("\x1b[", t.nodeValue)  # ANSI escapes intact


class TestAdversarialUserInputInteractions(unittest.TestCase):
    """Adversarial stress test on user input controls (textarea, text input, contenteditable)."""

    def setUp(self):
        self.engine = AdversarialSafetyEngine()

    def test_textarea_user_typing_protection(self):
        """User typing 'Delete all conversations' in textarea must not be translated; placeholder is."""
        textarea = MockNode(
            MockNode.ELEMENT_NODE, "textarea",
            attributes={
                "placeholder": "Search conversations...",
                "title": "Conversation History",
                "value": "Delete all conversations and Clear all history"
            }
        )
        child_text = MockNode(MockNode.TEXT_NODE, node_value="Delete all conversations and Clear all history")
        textarea.append_child(child_text)

        self.engine.walk(textarea)

        # Value and child text remain English user input
        self.assertEqual(textarea.getAttribute("value"), "Delete all conversations and Clear all history")
        self.assertEqual(child_text.nodeValue, "Delete all conversations and Clear all history")

        # Attributes are translated
        self.assertEqual(textarea.getAttribute("placeholder"), "搜索对话...")
        self.assertEqual(textarea.getAttribute("title"), "历史对话")

    def test_text_input_user_typing_protection(self):
        """User typing in <input type='text'> must not have value translated, placeholder is translated."""
        text_input = MockNode(
            MockNode.ELEMENT_NODE, "input",
            attributes={
                "type": "text",
                "placeholder": "Filter by date",
                "title": "Filter by project",
                "value": "Delete all conversations"
            }
        )

        self.engine.walk(text_input)

        # Value attribute must NOT be translated on text input
        self.assertEqual(text_input.getAttribute("value"), "Delete all conversations")

        # Placeholder and title MUST be translated
        self.assertEqual(text_input.getAttribute("placeholder"), "按日期筛选")
        self.assertEqual(text_input.getAttribute("title"), "按项目筛选")

    def test_contenteditable_protection(self):
        """[contenteditable='true'] user drafted message must be untouched."""
        ce = MockNode(
            MockNode.ELEMENT_NODE, "div",
            class_name="composer-editor",
            is_content_editable=True
        )
        user_text = MockNode(MockNode.TEXT_NODE, node_value="Please Close this task and Save the result.")
        ce.append_child(user_text)

        self.engine.walk(ce)

        self.assertEqual(user_text.nodeValue, "Please Close this task and Save the result.")


class TestAdversarialButtonInputValueLabels(unittest.TestCase):
    """Adversarial stress test on button input types (submit, button, reset)."""

    def setUp(self):
        self.engine = AdversarialSafetyEngine()

    def test_submit_button_value_translated(self):
        """<input type='submit' value='Save'> value must be translated to '保存'."""
        btn = MockNode(
            MockNode.ELEMENT_NODE, "input",
            attributes={"type": "submit", "value": "Save", "title": "Save File"}
        )
        self.engine.walk(btn)
        self.assertEqual(btn.getAttribute("value"), "保存")
        self.assertEqual(btn.getAttribute("title"), "保存文件")

    def test_button_input_value_translated(self):
        """<input type='button' value='Cancel'> value must be translated to '取消'."""
        btn = MockNode(
            MockNode.ELEMENT_NODE, "input",
            attributes={"type": "button", "value": "Cancel"}
        )
        self.engine.walk(btn)
        self.assertEqual(btn.getAttribute("value"), "取消")

    def test_reset_button_value_translated(self):
        """<input type='reset' value='Reset'> value must be translated to '重置'."""
        btn = MockNode(
            MockNode.ELEMENT_NODE, "input",
            attributes={"type": "reset", "value": "Reset"}
        )
        self.engine.walk(btn)
        self.assertEqual(btn.getAttribute("value"), "重置")

    def test_accept_reject_all_changes_submit_buttons(self):
        """<input type='submit' value='Accept All Changes'> and 'Reject All Changes'."""
        btn_accept = MockNode(
            MockNode.ELEMENT_NODE, "input",
            attributes={"type": "submit", "value": "Accept All Changes"}
        )
        btn_reject = MockNode(
            MockNode.ELEMENT_NODE, "button",
            attributes={"type": "submit", "value": "Reject All Changes"}
        )
        btn_reject.append_child(MockNode(MockNode.TEXT_NODE, node_value="Reject All Changes"))

        self.engine.walk(btn_accept)
        self.engine.walk(btn_reject)

        self.assertEqual(btn_accept.getAttribute("value"), "接受全部更改")
        self.assertEqual(btn_reject.firstChild.nodeValue, "拒绝全部更改")


if __name__ == "__main__":
    unittest.main()
