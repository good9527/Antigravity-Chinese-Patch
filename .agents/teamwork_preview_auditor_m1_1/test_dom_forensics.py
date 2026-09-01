#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep DOM & Shadow DOM Simulation and Safety Bypass Stress Test
"""
import re
import json

with open('dist/dictionary.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

# DOM node mock representation
class DOMNode:
    TEXT_NODE = 3
    ELEMENT_NODE = 1
    DOCUMENT_FRAGMENT_NODE = 11

    def __init__(self, node_type, tag_name="", node_value="", attributes=None, class_name="", is_content_editable=False):
        self.nodeType = node_type
        self.tagName = tag_name.upper() if tag_name else ""
        self.nodeValue = node_value
        self.attributes = attributes or {}
        self.className = class_name
        self.isContentEditable = is_content_editable
        self.children = []
        self.parent = None
        self.shadowRoot = None

    def append_child(self, child):
        child.parent = self
        self.children.append(child)
        return child

    @property
    def firstChild(self):
        return self.children[0] if self.children else None

    @property
    def nextSibling(self):
        if not self.parent: return None
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

    def matches(self, selector):
        classes = self.className.split() if self.className else []
        tag = self.tagName.lower() if self.tagName else ""
        for part in selector.split(','):
            part = part.strip()
            if part.startswith('.') and part[1:] in classes:
                return True
            if part == tag:
                return True
            if part == 'textarea' and tag == 'textarea':
                return True
            if '[contenteditable="true"]' in part and self.isContentEditable:
                return True
        return False

    def closest(self, selector):
        curr = self
        while curr:
            if curr.nodeType == DOMNode.ELEMENT_NODE and curr.matches(selector):
                return curr
            curr = curr.parent
        return None

# Localization engine implementation extracted from preload.js
IGNORE_TAGS = {'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'CANVAS', 'SVG', 'MATH', 'OBJECT', 'EMBED'}
CODE_OR_INPUT_TAGS = {'PRE', 'CODE', 'KBD', 'SAMP', 'VAR', 'TEXTAREA'}
BUTTON_INPUT_TYPES = {'button', 'submit', 'reset'}
SAFE_ATTRS = ['placeholder', 'title', 'aria-label']
BYPASS_ANCESTOR_SELECTOR = '.monaco-editor, .view-lines, .monaco-list-row, .cm-editor, .cm-content, .editor-instance, .monaco-tokenized-source, pre, code, kbd, samp, var, .code-block, .hljs, .syntax-highlighted, .highlight, .terminal, .xterm, .xterm-screen, .xterm-viewport, .terminal-wrapper, textarea, [contenteditable="true"], [contenteditable=""], [contenteditable]:not([contenteditable="false"]), [data-no-translate], [translate="no"], svg, canvas'

def normalize(str_val):
    if not str_val: return ''
    return str_val.replace('\u00a0', ' ')

def translateText(text):
    if not text or not isinstance(text, str): return None
    norm = normalize(text)
    trimmed = norm.strip()
    if not trimmed: return None
    if trimmed in dictionary:
        return norm.replace(trimmed, dictionary[trimmed])
    # Dynamic patterns
    m = re.match(r'^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks)\s+(\d+)$', trimmed, re.IGNORECASE)
    if m:
        tmap = {'subagents': '子智能体', 'files changed': '已修改文件', 'artifacts': '产物', 'uploads': '已上传文件', 'background tasks': '后台任务'}
        lbl = tmap.get(m.group(1).lower(), m.group(1))
        return f"{lbl} {m.group(2)}"
    return None

def isBypassedElement(el):
    if not el or el.nodeType != 1: return False
    if el.tagName in IGNORE_TAGS: return True
    if el.isContentEditable: return True
    if el.getAttribute and el.getAttribute('contenteditable') == 'true': return True
    if el.matches and el.matches(BYPASS_ANCESTOR_SELECTOR): return True
    if el.closest and el.closest(BYPASS_ANCESTOR_SELECTOR): return True
    cls = el.className or ''
    if any(b in cls for b in ['monaco-editor', 'view-lines', 'monaco-list-row', 'terminal', 'xterm', 'code-block', 'hljs']):
        return True
    return False

def isBypassedNode(node):
    if not node: return True
    if node.nodeType == 3:
        p = node.parent
        if not p or p.nodeType != 1: return False
        if p.tagName in IGNORE_TAGS or p.tagName in CODE_OR_INPUT_TAGS: return True
        if p.isContentEditable: return True
        if p.closest and p.closest(BYPASS_ANCESTOR_SELECTOR): return True
        return isBypassedElement(p)
    if node.nodeType == 1:
        return isBypassedElement(node)
    return False

def translateAttributes(el, attrs):
    if not el: return
    for attr in attrs:
        if el.hasAttribute(attr):
            val = el.getAttribute(attr)
            if val:
                trans = translateText(val)
                if trans is not None and trans != val:
                    el.setAttribute(attr, trans)

def walk(node):
    if not node: return
    if node.nodeType == 3:
        if isBypassedNode(node): return
        text = node.nodeValue
        if text:
            trans = translateText(text)
            if trans is not None and trans != text:
                node.nodeValue = trans
        return

    if node.nodeType == 11:
        for child in list(node.children):
            walk(child)
        return

    if node.nodeType == 1:
        tag = node.tagName
        if tag in IGNORE_TAGS: return
        if tag == 'TEXTAREA':
            translateAttributes(node, SAFE_ATTRS)
            return
        if tag == 'INPUT':
            itype = (node.getAttribute('type') or 'text').lower()
            if itype in BUTTON_INPUT_TYPES:
                translateAttributes(node, SAFE_ATTRS + ['value'])
            else:
                translateAttributes(node, SAFE_ATTRS)
            return

        is_self_bypassed = (
            tag in CODE_OR_INPUT_TAGS or
            (node.matches and node.matches(BYPASS_ANCESTOR_SELECTOR)) or
            isBypassedElement(node)
        )
        if is_self_bypassed:
            translateAttributes(node, SAFE_ATTRS)
            return

        translateAttributes(node, SAFE_ATTRS)

        if node.shadowRoot:
            walk(node.shadowRoot)

        for child in list(node.children):
            walk(child)

print("--- Running Deep DOM & Shadow DOM Stress Tests ---")

# Test 1: Normal UI container
root = DOMNode(DOMNode.ELEMENT_NODE, "div", class_name="app-sidebar")
item1 = DOMNode(DOMNode.ELEMENT_NODE, "button", class_name="nav-btn", attributes={"title": "New Conversation", "aria-label": "New Conversation"})
item1_text = DOMNode(DOMNode.TEXT_NODE, node_value="New Conversation")
item1.append_child(item1_text)
root.append_child(item1)

walk(root)
assert item1_text.nodeValue == "新建对话", f"Expected '新建对话', got '{item1_text.nodeValue}'"
assert item1.getAttribute("title") == "新建对话"
assert item1.getAttribute("aria-label") == "新建对话"
print("[PASS] Normal UI element translated correctly.")

# Test 2: Monaco Editor Bypass
monaco = DOMNode(DOMNode.ELEMENT_NODE, "div", class_name="monaco-editor vs-dark")
view_lines = DOMNode(DOMNode.ELEMENT_NODE, "div", class_name="view-lines")
line = DOMNode(DOMNode.ELEMENT_NODE, "span", class_name="token keyword")
line_text = DOMNode(DOMNode.TEXT_NODE, node_value="Settings")
line.append_child(line_text)
view_lines.append_child(line)
monaco.append_child(view_lines)

walk(monaco)
assert line_text.nodeValue == "Settings", f"Expected 'Settings' (untranslated), got '{line_text.nodeValue}'"
print("[PASS] Monaco Editor content protected and untranslated.")

# Test 3: Terminal / Xterm Bypass
term = DOMNode(DOMNode.ELEMENT_NODE, "div", class_name="terminal xterm")
term_screen = DOMNode(DOMNode.ELEMENT_NODE, "div", class_name="xterm-screen")
term_row = DOMNode(DOMNode.ELEMENT_NODE, "span")
term_text = DOMNode(DOMNode.TEXT_NODE, node_value="New Conversation")
term_row.append_child(term_text)
term_screen.append_child(term_row)
term.append_child(term_screen)

walk(term)
assert term_text.nodeValue == "New Conversation", f"Expected 'New Conversation' (untranslated), got '{term_text.nodeValue}'"
print("[PASS] Terminal / Xterm content protected and untranslated.")

# Test 4: Textarea user typing protection + placeholder translation
textarea = DOMNode(DOMNode.ELEMENT_NODE, "textarea", attributes={"placeholder": "Ask a question or provide instructions...", "value": "New Conversation"})
textarea_text = DOMNode(DOMNode.TEXT_NODE, node_value="I am typing: New Conversation")
textarea.append_child(textarea_text)

walk(textarea)
assert textarea_text.nodeValue == "I am typing: New Conversation", "Textarea children must NOT be translated"
assert textarea.getAttribute("placeholder") == "请输入您的问题或具体指令..."
assert textarea.getAttribute("value") == "New Conversation", "Textarea value attribute must NOT be translated"
print("[PASS] Textarea user input protected, placeholder translated.")

# Test 5: ContentEditable protection
editable = DOMNode(DOMNode.ELEMENT_NODE, "div", is_content_editable=True, attributes={"contenteditable": "true"})
ed_text = DOMNode(DOMNode.TEXT_NODE, node_value="Settings are configured here")
editable.append_child(ed_text)

walk(editable)
assert ed_text.nodeValue == "Settings are configured here", "ContentEditable text must NOT be translated"
print("[PASS] ContentEditable user input protected.")

# Test 6: Shadow DOM Traversal
custom_el = DOMNode(DOMNode.ELEMENT_NODE, "custom-component")
shadow = DOMNode(DOMNode.DOCUMENT_FRAGMENT_NODE)
shadow_btn = DOMNode(DOMNode.ELEMENT_NODE, "button")
shadow_btn_text = DOMNode(DOMNode.TEXT_NODE, node_value="Files Changed")
shadow_btn.append_child(shadow_btn_text)
shadow.append_child(shadow_btn)
custom_el.shadowRoot = shadow

walk(custom_el)
assert shadow_btn_text.nodeValue == "已修改文件", f"Expected '已修改文件', got '{shadow_btn_text.nodeValue}'"
print("[PASS] Open Shadow DOM traversed and translated correctly.")

# Test 7: Button Input vs Text Input
btn_input = DOMNode(DOMNode.ELEMENT_NODE, "input", attributes={"type": "button", "value": "Cancel"})
text_input = DOMNode(DOMNode.ELEMENT_NODE, "input", attributes={"type": "text", "value": "Cancel", "placeholder": "Search conversations..."})

walk(btn_input)
walk(text_input)

assert btn_input.getAttribute("value") == "取消", "Button input value must be translated"
assert text_input.getAttribute("value") == "Cancel", "Text input value must NOT be translated"
assert text_input.getAttribute("placeholder") == "搜索对话...", "Text input placeholder must be translated"
print("[PASS] Button input vs Text input value protection verified.")

print("\nALL 7 DOM FORENSIC SIMULATION CHECKS PASSED EMPIRICALLY [OK]!")
