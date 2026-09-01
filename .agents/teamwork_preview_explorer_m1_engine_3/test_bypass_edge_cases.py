# Comprehensive Edge Case Verification Suite for Bypass & MutationObserver Isolation
import json

class MockNode:
    def __init__(self, node_type, name='', value='', attrs=None, parent=None):
        self.node_type = node_type  # 1: Element, 3: Text, 11: DocumentFragment
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

# Exact JavaScript Engine implementation ported to Python for verification
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
    'New Conversation': '\u65b0\u5efa\u5bf9\u8bdd',
    'Settings': '\u8bbe\u7f6e',
    'Save': '\u4fdd\u5b58',
    'Close': '\u5173\u95ed',
    'Delete': '\u5220\u9664',
    'Cancel': '\u53d6\u6d88',
    'Files Changed': '\u5df2\u4fee\u653f\u6587\u4ef6',
    'Ask anything, @ to mention, / for actions': '\u95ee\u6211\u4efb\u4f55\u95ee\u9898\uff0c\u7528 @ \u63d0\u53ca\u6587\u4ef6\uff0c\u7528 / \u6267\u884c\u52a8\u4f5c'
}

def translate_text(text):
    if not text or not isinstance(text, str):
        return None
    trimmed = text.strip()
    if trimmed in DICTIONARY:
        return text.replace(trimmed, DICTIONARY[trimmed])
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
            if trans and trans != val:
                el.set_attribute(a, trans)

def walk(node):
    if not node:
        return
    if node.node_type == 3:
        if not is_bypassed_node(node):
            trans = translate_text(node.node_value)
            if trans and trans != node.node_value:
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
        is_self_bypassed = (tag in CODE_OR_INPUT_TAGS) or (node.matches and node.matches(BYPASS_ANCESTOR_SELECTOR))
        if is_self_bypassed:
            translate_attributes(node, SAFE_ATTRS)
            return
        translate_attributes(node, SAFE_ATTRS)
        for child in list(node.children):
            walk(child)
        if node.shadow_root:
            walk(node.shadow_root)
        return
    if node.node_type == 11:
        for child in list(node.children):
            walk(child)
        return

# MutationObserver handler simulation
def handle_mutation(mutation):
    mtype = mutation['type']
    if mtype == 'childList':
        for added in mutation.get('addedNodes', []):
            if added.node_type == 3:
                if not is_bypassed_node(added):
                    trans = translate_text(added.node_value)
                    if trans and trans != added.node_value:
                        added.node_value = trans
            elif added.node_type == 1:
                # If parent itself is already in bypass container, skip
                if added.parent and added.parent.closest(BYPASS_ANCESTOR_SELECTOR):
                    continue
                walk(added)
            elif added.node_type == 11:
                walk(added)
    elif mtype == 'characterData':
        target = mutation['target']
        if not is_bypassed_node(target):
            trans = translate_text(target.node_value)
            if trans and trans != target.node_value:
                target.node_value = trans
    elif mtype == 'attributes':
        target = mutation['target']
        attr = mutation['attributeName']
        if attr == 'value':
            if target.tag_name == 'INPUT':
                itype = (target.get_attribute('type') or 'text').lower()
                if itype in BUTTON_INPUT_TYPES:
                    val = target.get_attribute('value')
                    trans = translate_text(val)
                    if trans and trans != val:
                        target.set_attribute('value', trans)
        elif attr in SAFE_ATTRS:
            if target.tag_name not in IGNORE_TAGS:
                val = target.get_attribute(attr)
                trans = translate_text(val)
                if trans and trans != val:
                    target.set_attribute(attr, trans)

def run_tests():
    # 1. Inline Code Test (<p>Settings <code>Save</code></p>)
    p = MockNode(1, 'p')
    t1 = p.append_child(MockNode(3, value='Settings'))
    code = p.append_child(MockNode(1, 'code'))
    t2 = code.append_child(MockNode(3, value='Save'))
    t3 = p.append_child(MockNode(3, value=' here'))
    walk(p)
    assert t1.node_value == '\u8bbe\u7f6e', 'P text failed'
    assert t2.node_value == 'Save', 'Inline code was modified!'
    assert t3.node_value == ' here'

    # 2. Dynamic Streaming into Monaco Editor (characterData mutation)
    monaco = MockNode(1, 'div', attrs={'class': 'monaco-editor'})
    line = monaco.append_child(MockNode(1, 'div', attrs={'class': 'view-line'}))
    token = line.append_child(MockNode(3, value=''))
    # Stream token 'Settings'
    token.node_value = 'Settings'
    handle_mutation({'type': 'characterData', 'target': token})
    assert token.node_value == 'Settings', 'Monaco stream token was corrupted!'

    # 3. Dynamic Terminal Output (childList mutation)
    term = MockNode(1, 'div', attrs={'class': 'terminal xterm'})
    new_row = MockNode(1, 'div', attrs={'class': 'xterm-rows'})
    term.append_child(new_row)
    new_text = new_row.append_child(MockNode(3, value='Delete'))
    handle_mutation({'type': 'childList', 'addedNodes': [new_row]})
    assert new_text.node_value == 'Delete', 'Terminal childList corrupted!'

    # 4. Contenteditable input typing (characterData mutation)
    chat_input = MockNode(1, 'div', attrs={'contenteditable': 'true'})
    chat_text = chat_input.append_child(MockNode(3, value='Please Save'))
    handle_mutation({'type': 'characterData', 'target': chat_text})
    assert chat_text.node_value == 'Please Save', 'User typed prompt in contenteditable was corrupted!'

    # 5. Search input typing value mutation (attributes mutation)
    search_input = MockNode(1, 'input', attrs={'type': 'search', 'value': 'Initial'})
    search_input.set_attribute('value', 'Save')
    handle_mutation({'type': 'attributes', 'target': search_input, 'attributeName': 'value'})
    assert search_input.get_attribute('value') == 'Save', 'Search input value was corrupted!'

    # 6. Button input value mutation (attributes mutation)
    submit_btn = MockNode(1, 'input', attrs={'type': 'submit', 'value': 'Initial'})
    submit_btn.set_attribute('value', 'Save')
    handle_mutation({'type': 'attributes', 'target': submit_btn, 'attributeName': 'value'})
    assert submit_btn.get_attribute('value') == '\u4fdd\u5b58', 'Submit button value was not translated!'

    # 7. Shadow DOM inside Custom Web Component
    custom_comp = MockNode(1, 'custom-card')
    shadow = MockNode(11) # DocumentFragment
    custom_comp.shadow_root = shadow
    shadow_header = shadow.append_child(MockNode(1, 'h2'))
    shadow_header_text = shadow_header.append_child(MockNode(3, value='Settings'))
    # Code inside shadow DOM
    shadow_code = shadow.append_child(MockNode(1, 'pre'))
    shadow_code_text = shadow_code.append_child(MockNode(3, value='Close'))
    walk(custom_comp)
    assert shadow_header_text.node_value == '\u8bbe\u7f6e', 'Shadow DOM UI text failed'
    assert shadow_code_text.node_value == 'Close', 'Shadow DOM code block corrupted!'

    # 8. data-no-translate attribute escape hatch
    escape_box = MockNode(1, 'div', attrs={'data-no-translate': 'true'})
    escape_text = escape_box.append_child(MockNode(3, value='Settings'))
    walk(escape_box)
    assert escape_text.node_value == 'Settings', 'data-no-translate was not respected!'

    print('ALL 8 EXTENDED EDGE CASE TESTS PASSED!')

if __name__ == '__main__':
    run_tests()
