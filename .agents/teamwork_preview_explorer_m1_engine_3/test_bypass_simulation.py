# Test verification script for DOM Safety Bypass and Sandbox Isolation
import json

class MockNode:
    def __init__(self, node_type, name='', value='', attrs=None, parent=None):
        self.node_type = node_type  # 1: Element, 3: Text
        self.tag_name = name.upper() if node_type == 1 else ''
        self.node_value = value
        self.attrs = dict(attrs or {})
        self.parent = parent
        self.children = []
        self.shadow_root = None

    def append_child(self, child):
        child.parent = self
        self.children.append(child)
        return child

    def get_attribute(self, attr):
        return self.attrs.get(attr)

    def set_attribute(self, attr, val):
        self.attrs[attr] = val

    def has_attribute(self, attr):
        return attr in self.attrs

    def matches(self, selector):
        classes = self.attrs.get('class', '').split()
        tag = self.tag_name.lower()
        parts = [s.strip() for s in selector.split(',')]
        for p in parts:
            if p.startswith('.'):
                if p[1:] in classes:
                    return True
            elif p.startswith('['):
                attr_part = p[1:-1]
                if '=' in attr_part:
                    k, v = attr_part.split('=', 1)
                    v = v.strip('"\'')
                    if self.attrs.get(k) == v:
                        return True
                else:
                    if attr_part in self.attrs:
                        return True
            elif p.lower() == tag:
                return True
        return False

    def closest(self, selector):
        curr = self
        while curr:
            if curr.node_type == 1 and curr.matches(selector):
                return curr
            curr = curr.parent
        return None

# Safety bypass constants
IGNORE_TAGS = {'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'CANVAS', 'SVG', 'MATH', 'OBJECT', 'EMBED'}
CODE_OR_INPUT_TAGS = {'PRE', 'CODE', 'KBD', 'SAMP', 'VAR', 'TEXTAREA'}
BUTTON_INPUT_TYPES = {'button', 'submit', 'reset'}
SAFE_ATTRS = ['placeholder', 'title', 'aria-label']
BYPASS_ANCESTOR_SELECTOR = (
    '.monaco-editor, .view-lines, .monaco-list-row, .cm-editor, .cm-content, '
    '.editor-instance, .monaco-tokenized-source, pre, code, kbd, samp, '
    '.code-block, .hljs, .syntax-highlighted, .highlight, .terminal, .xterm, '
    '.xterm-screen, .xterm-viewport, .terminal-wrapper, textarea, '
    '[contenteditable="true"], [contenteditable=""], [data-no-translate], [translate="no"], svg, canvas'
)

DICTIONARY = {
    'New Conversation': '新建对话',
    'Settings': '设置',
    'Save': '保存',
    'Close': '关闭',
    'Delete': '删除',
    'Cancel': '取消',
    'Files Changed': '已修改文件',
    'Ask anything, @ to mention, / for actions': '问我任何问题，用 @ 提及文件，用 / 执行动作'
}

def translate_text(text):
    if not text:
        return None
    trimmed = text.strip()
    if trimmed in DICTIONARY:
        return DICTIONARY[trimmed]
    return None

def is_bypassed_node(node):
    if not node:
        return True
    if node.node_type == 3:  # TextNode
        parent = node.parent
        if not parent:
            return True
        if parent.tag_name in IGNORE_TAGS or parent.tag_name in CODE_OR_INPUT_TAGS:
            return True
        if parent.closest(BYPASS_ANCESTOR_SELECTOR):
            return True
        return False
    if node.node_type == 1:  # Element
        if node.tag_name in IGNORE_TAGS:
            return True
        if node.matches(BYPASS_ANCESTOR_SELECTOR) or node.closest(BYPASS_ANCESTOR_SELECTOR):
            return True
        return False
    return False

def translate_attributes(el, attrs):
    for a in attrs:
        if el.has_attribute(a):
            val = el.get_attribute(a)
            trans = translate_text(val)
            if trans:
                el.set_attribute(a, trans)

def walk(node):
    if not node:
        return
    if node.node_type == 3:
        if not is_bypassed_node(node):
            trans = translate_text(node.node_value)
            if trans:
                node.node_value = trans
        return
    if node.node_type == 1:
        tag = node.tag_name
        if tag in IGNORE_TAGS:
            return
        if tag == 'TEXTAREA':
            translate_attributes(node, SAFE_ATTRS)
            return
        if tag == 'INPUT':
            itype = (node.get_attribute('type') or 'text').lower()
            if itype in BUTTON_INPUT_TYPES:
                translate_attributes(node, SAFE_ATTRS + ['value'])
            else:
                translate_attributes(node, SAFE_ATTRS)
            return
        is_self_bypassed = (tag in CODE_OR_INPUT_TAGS) or node.matches(BYPASS_ANCESTOR_SELECTOR)
        if is_self_bypassed:
            translate_attributes(node, SAFE_ATTRS)
            return
        translate_attributes(node, SAFE_ATTRS)
        for child in list(node.children):
            walk(child)
        if node.shadow_root:
            walk(node.shadow_root)

def test_all():
    root = MockNode(1, 'div')

    # 1. Normal UI element (Should be translated)
    btn = root.append_child(MockNode(1, 'button'))
    btn_text = btn.append_child(MockNode(3, value='Settings'))

    # 2. Monaco Editor (Should be untouched)
    monaco = root.append_child(MockNode(1, 'div', attrs={'class': 'monaco-editor'}))
    view_lines = monaco.append_child(MockNode(1, 'div', attrs={'class': 'view-lines'}))
    code_line = view_lines.append_child(MockNode(1, 'span'))
    code_text = code_line.append_child(MockNode(3, value='const Settings = "Save";'))

    # 3. Markdown code fence (Should be untouched)
    pre = root.append_child(MockNode(1, 'pre'))
    code = pre.append_child(MockNode(1, 'code'))
    code_text2 = code.append_child(MockNode(3, value='Close()'))

    # 4. Terminal (Should be untouched)
    terminal = root.append_child(MockNode(1, 'div', attrs={'class': 'terminal xterm'}))
    term_text = terminal.append_child(MockNode(3, value='Delete'))

    # 5. User Input (Textarea: placeholder translated, inner text untouched)
    textarea = root.append_child(MockNode(1, 'textarea', attrs={'placeholder': 'Ask anything, @ to mention, / for actions'}))
    ta_text = textarea.append_child(MockNode(3, value='Delete'))

    # 6. Search Input (Placeholder translated, value untouched)
    inp_search = root.append_child(MockNode(1, 'input', attrs={'type': 'text', 'placeholder': 'Settings', 'value': 'Save'}))

    # 7. Submit Input (Value translated)
    inp_submit = root.append_child(MockNode(1, 'input', attrs={'type': 'submit', 'value': 'Save'}))

    # 8. Contenteditable (Aria-label translated, inner text untouched)
    ce = root.append_child(MockNode(1, 'div', attrs={'contenteditable': 'true', 'aria-label': 'New Conversation'}))
    ce_text = ce.append_child(MockNode(3, value='Save'))

    walk(root)

    print('1. Button text:', btn_text.node_value, '(Expected: 设置)')
    print('2. Monaco code:', code_text.node_value, '(Expected: const Settings = "Save";)')
    print('3. Markdown code:', code_text2.node_value, '(Expected: Close())')
    print('4. Terminal text:', term_text.node_value, '(Expected: Delete)')
    print('5. Textarea placeholder:', textarea.get_attribute('placeholder'), '(Expected: 问我任何问题...)')
    print('5. Textarea content:', ta_text.node_value, '(Expected: Delete)')
    print('6. Search placeholder:', inp_search.get_attribute('placeholder'), '(Expected: 设置)')
    print('6. Search value:', inp_search.get_attribute('value'), '(Expected: Save)')
    print('7. Submit value:', inp_submit.get_attribute('value'), '(Expected: 保存)')
    print('8. Contenteditable aria-label:', ce.get_attribute('aria-label'), '(Expected: 新建对话)')
    print('8. Contenteditable content:', ce_text.node_value, '(Expected: Save)')

    assert btn_text.node_value == '设置', 'Button text failed'
    assert code_text.node_value == 'const Settings = "Save";', 'Monaco text modified'
    assert code_text2.node_value == 'Close()', 'Markdown code modified'
    assert term_text.node_value == 'Delete', 'Terminal text modified'
    assert textarea.get_attribute('placeholder') == '问我任何问题，用 @ 提及文件，用 / 执行动作', 'Textarea placeholder failed'
    assert ta_text.node_value == 'Delete', 'Textarea content modified'
    assert inp_search.get_attribute('placeholder') == '设置', 'Search placeholder failed'
    assert inp_search.get_attribute('value') == 'Save', 'Search value modified'
    assert inp_submit.get_attribute('value') == '保存', 'Submit value failed'
    assert ce.get_attribute('aria-label') == '新建对话', 'Contenteditable aria-label failed'
    assert ce_text.node_value == 'Save', 'Contenteditable text modified'
    print('\n>>> ALL 8 CORE TEST SCENARIOS PASSED WITH ZERO VIOLATIONS! <<<')

if __name__ == '__main__':
    test_all()
