class MockNode:
    def __init__(self, node_type, tag_name=None, node_value=None, attributes=None, class_name=""):
        self.node_type = node_type # 1: Element, 3: Text, 11: DocumentFragment/ShadowRoot
        self.tag_name = tag_name.upper() if tag_name else None
        self.node_value = node_value
        self.attributes = attributes or {}
        self.class_name = class_name
        self.children = []
        self.parent_node = None
        self.shadow_root = None
        self.is_content_editable = False

    @property
    def first_child(self):
        return self.children[0] if self.children else None

    @property
    def next_sibling(self):
        if not self.parent_node:
            return None
        idx = self.parent_node.children.index(self)
        if idx + 1 < len(self.parent_node.children):
            return self.parent_node.children[idx + 1]
        return None

    def append_child(self, child):
        child.parent_node = self
        self.children.append(child)
        return child

    def has_attribute(self, name):
        return name in self.attributes

    def get_attribute(self, name):
        return self.attributes.get(name)

    def set_attribute(self, name, value):
        self.attributes[name] = value

def create_element(tag, attrs=None, class_name=""):
    return MockNode(1, tag_name=tag, attributes=attrs, class_name=class_name)

def create_text(val):
    return MockNode(3, node_value=val)

def create_shadow_root():
    return MockNode(11)

# Import our verified python matcher
from verify_patterns import match_dynamic_patterns, UNIT_MAP_CN, format_timer_unit

DICTIONARY = {
  "New Conversation": "\u65b0\u5efa\u5bf9\u8bdd",
  "Conversation History": "\u5386\u53f2\u5bf9\u8bdd",
  "Scheduled Tasks": "\u8ba1\u5212\u4efb\u52a1",
  "Projects": "\u9879\u76ee\u5217\u8868",
  "Settings": "\u8bbe\u7f6e",
  "Untitled Conversation": "\u672a\u547d\u540d\u5bf9\u8bdd",
  "Save": "\u4fdd\u5b58",
  "Delete": "\u5220\u9664"
}

BYPASS_TAGS = {'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEXTAREA', 'CODE', 'PRE', 'CANVAS'}
BYPASS_CLASSES = [
  'monaco-editor',
  'view-lines',
  'monaco-list-row',
  'terminal',
  'xterm',
  'xterm-screen',
  'code-block',
  'hljs',
  'cm-content',
  'editor-instance'
]

def normalize(s):
    if not s:
        return ""
    return s.replace('\u00a0', ' ')

def translate_text(text):
    if not text or not isinstance(text, str):
        return None
    norm = normalize(text)
    trimmed = norm.strip()
    if not trimmed:
        return None
    if trimmed in DICTIONARY:
        return norm.replace(trimmed, DICTIONARY[trimmed])
    if norm in DICTIONARY:
        return DICTIONARY[norm]
    dyn = match_dynamic_patterns(trimmed)
    if dyn is not None:
        return norm.replace(trimmed, dyn)
    return None

def is_bypassed_element(el):
    if not el or el.node_type != 1:
        return False
    if el.tag_name in BYPASS_TAGS:
        return True
    if el.is_content_editable:
        return True
    if el.get_attribute('contenteditable') == 'true':
        return True
    cls = el.class_name or el.get_attribute('class') or ""
    for bc in BYPASS_CLASSES:
        if bc in cls:
            return True
    return False

def is_bypassed_node(node):
    if not node:
        return True
    if node.node_type == 3:
        p = node.parent_node
        while p and p.node_type == 1:
            if is_bypassed_element(p):
                return True
            p = p.parent_node
        return False
    if node.node_type == 1:
        return is_bypassed_element(node)
    return False

def walk(node):
    if not node:
        return
    if node.node_type == 3:
        if is_bypassed_node(node):
            return
        val = node.node_value
        trans = translate_text(val)
        if trans is not None and trans != val:
            node.node_value = trans
        return
    if node.node_type == 11:
        for child in list(node.children):
            walk(child)
        return
    if node.node_type == 1:
        if is_bypassed_element(node):
            return
        # Translate placeholder, title, aria-label
        for attr in ['placeholder', 'title', 'aria-label']:
            if node.has_attribute(attr):
                val = node.get_attribute(attr)
                trans = translate_text(val)
                if trans is not None and trans != val:
                    node.set_attribute(attr, trans)
        # Value attribute for button inputs only
        if node.tag_name == 'INPUT' and node.has_attribute('value'):
            itype = (node.get_attribute('type') or 'text').lower()
            if itype in ('button', 'submit', 'reset'):
                val = node.get_attribute('value')
                trans = translate_text(val)
                if trans is not None and trans != val:
                    node.set_attribute('value', trans)
        # Traverse Shadow DOM
        if node.shadow_root:
            walk(node.shadow_root)
        # Traverse children
        for child in list(node.children):
            walk(child)

# Run DOM tests
print("Testing DOM Walker...")

# Test 1: Standard Element & Text
div = create_element('div')
text1 = create_text('New Conversation')
div.append_child(text1)
walk(div)
assert text1.node_value == '新建对话', f"Expected 新建对话, got {text1.node_value}"

# Test 2: Dynamic Thinking Timer
span = create_element('span')
text2 = create_text('Thinking for 1.2s')
span.append_child(text2)
walk(span)
assert text2.node_value == '思考中 (1.2秒)', f"Expected 思考中 (1.2秒), got {text2.node_value}"

# Test 3: Shadow DOM Traversal
custom_el = create_element('custom-widget')
shadow = create_shadow_root()
custom_el.shadow_root = shadow
shadow_text = create_text('Scheduled Tasks')
shadow.append_child(shadow_text)
walk(custom_el)
assert shadow_text.node_value == '计划任务', f"Expected 计划任务 in shadow root, got {shadow_text.node_value}"

# Test 4: Monaco Editor Bypass
monaco_div = create_element('div', class_name='monaco-editor')
code_line = create_element('div', class_name='view-line')
code_text = create_text('const Save = "Settings";')
code_line.append_child(code_text)
monaco_div.append_child(code_line)
walk(monaco_div)
assert code_text.node_value == 'const Save = "Settings";', f"Monaco code should NOT be translated! Got {code_text.node_value}"

# Test 5: Pre / Code Bypass
pre = create_element('pre')
code = create_element('code')
raw_code = create_text('function deleteItem() { return Save; }')
code.append_child(raw_code)
pre.append_child(code)
walk(pre)
assert raw_code.node_value == 'function deleteItem() { return Save; }', "Code fence should NOT be translated!"

# Test 6: Textarea and Input Value Protection
textarea = create_element('textarea', attrs={'placeholder': 'New Conversation', 'value': 'Please Save this prompt'})
walk(textarea)
# Textarea tag itself is bypassed from walk
assert textarea.attributes.get('value') == 'Please Save this prompt', "Textarea value must be untouched!"

input_text = create_element('input', attrs={'type': 'text', 'placeholder': 'New Conversation', 'value': 'Save'})
walk(input_text)
assert input_text.get_attribute('placeholder') == '新建对话', "Input placeholder should be translated"
assert input_text.get_attribute('value') == 'Save', "Input text value should NOT be translated!"

input_btn = create_element('input', attrs={'type': 'submit', 'value': 'Save'})
walk(input_btn)
assert input_btn.get_attribute('value') == '保存', "Submit button value SHOULD be translated!"

print("All DOM Walker, Shadow DOM, and Bypass tests passed successfully!")
