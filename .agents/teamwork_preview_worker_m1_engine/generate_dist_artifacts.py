# -*- coding: utf-8 -*-
"""
Generator and Verifier for Milestone 1 Artifacts:
- dist/dictionary.json (514 keys, clean standard UTF-8)
- dist/preload.js (host contextBridge stubs + pure ASCII Unicode-escaped engine)
- dist/engine.js (decoupled standalone translation engine)
"""

import json
import os
import re
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
DICT_PATH = os.path.join(DIST_DIR, "dictionary.json")
PRELOAD_PATH = os.path.join(DIST_DIR, "preload.js")
ENGINE_PATH = os.path.join(DIST_DIR, "engine.js")

sys.path.insert(0, os.path.join(PROJECT_ROOT, ".agents", "teamwork_preview_explorer_m1_engine_1"))
import build_dictionary

ENTRIES = build_dictionary.ENTRIES

def to_unicode_escapes(s):
    """Converts a string to pure ASCII with \\uXXXX escapes for non-ASCII characters."""
    out = []
    for char in s:
        code = ord(char)
        if code > 127:
            out.append(f"\\u{code:04x}")
        else:
            out.append(char)
    return "".join(out)

def generate_dictionary_json():
    print(f"Generating {DICT_PATH} with {len(ENTRIES)} keys...")
    with open(DICT_PATH, "w", encoding="utf-8") as f:
        json.dump(ENTRIES, f, ensure_ascii=False, indent=2)
    print("  -> dist/dictionary.json created.")

def generate_engine_core_js():
    """Generates the engine core JavaScript string with 100% pure ASCII Unicode escapes."""
    
    # 1. Build dictionary lines
    dict_lines = ["  const dictionary = {"]
    for k, v in ENTRIES.items():
        escaped_key = to_unicode_escapes(k).replace('"', '\\"')
        escaped_val = to_unicode_escapes(v).replace('"', '\\"')
        dict_lines.append(f'    "{escaped_key}": "{escaped_val}",')
    if dict_lines[-1].endswith(","):
        dict_lines[-1] = dict_lines[-1][:-1]
    dict_lines.append("  };")
    dict_js = "\n".join(dict_lines)

    engine_js = f"""// Antigravity Chinese Localization Patch
(function() {{
  'use strict';

  // 1. Static Translation Dictionary (514 Keys, Pure ASCII Unicode Escapes)
{dict_js}

  // 2. Substring Replacement Rules
  const substringReplacements = [
    {{ search: 'Minimize', replace: '\\u6700\\u5c0f\\u5316' }},
    {{ search: 'Maximize', replace: '\\u6700\\u5927\\u5316' }},
    {{ search: 'Toggle Developer Tools', replace: '\\u5207\\u6362\\u5f00\\u53d1\\u8005\\u5de5\\u5177' }},
    {{ search: 'Default', replace: '\\u9ed8\\u8ba4' }},
    {{ search: 'Full Machine', replace: '\\u6574\\u673a\\u6388\\u6743' }},
    {{ search: 'Turbo Mode', replace: '\\u6781\\u901f\\u6a21\\u5f0f' }},
    {{ search: 'Turbo mode', replace: '\\u6781\\u901f\\u6a21\\u5f0f' }},
    {{ search: 'Custom', replace: '\\u81ea\\u5b9a\\u4e49' }},
    {{ search: 'System', replace: '\\u8ddf\\u968f\\u7cfb\\u7edf' }}
  ];

  // 3. Time Unit Chinese Lookup Map
  const UNIT_MAP_CN = {{
    'mo': '\\u4e2a\\u6708\\u524d',
    'month': '\\u4e2a\\u6708\\u524d',
    'months': '\\u4e2a\\u6708\\u524d',
    'd': '\\u5929\\u524d',
    'day': '\\u5929\\u524d',
    'days': '\\u5929\\u524d',
    'm': '\\u5206\\u949f\\u524d',
    'min': '\\u5206\\u949f\\u524d',
    'mins': '\\u5206\\u949f\\u524d',
    'minute': '\\u5206\\u949f\\u524d',
    'minutes': '\\u5206\\u949f\\u524d',
    'h': '\\u5c0f\\u65f6\\u524d',
    'hr': '\\u5c0f\\u65f6\\u524d',
    'hrs': '\\u5c0f\\u65f6\\u524d',
    'hour': '\\u5c0f\\u65f6\\u524d',
    'hours': '\\u5c0f\\u65f6\\u524d',
    's': '\\u79d2\\u524d',
    'sec': '\\u79d2\\u524d',
    'secs': '\\u79d2\\u524d',
    'second': '\\u79d2\\u524d',
    'seconds': '\\u79d2\\u524d',
    'y': '\\u5e74\\u524d',
    'yr': '\\u5e74\\u524d',
    'yrs': '\\u5e74\\u524d',
    'year': '\\u5e74\\u524d',
    'years': '\\u5e74\\u524d'
  }};

  // 4. Strict Safety Bypass Elements & Ancestor Selectors
  const IGNORE_TAGS = new Set([
    'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'CANVAS',
    'SVG', 'MATH', 'OBJECT', 'EMBED'
  ]);

  const CODE_OR_INPUT_TAGS = new Set([
    'PRE', 'CODE', 'KBD', 'SAMP', 'VAR', 'TEXTAREA'
  ]);

  const BUTTON_INPUT_TYPES = new Set([
    'button', 'submit', 'reset'
  ]);

  const SAFE_ATTRS = ['placeholder', 'title', 'aria-label'];

  const BYPASS_ANCESTOR_SELECTOR = [
    '.monaco-editor',
    '.view-lines',
    '.monaco-list-row',
    '.cm-editor',
    '.cm-content',
    '.editor-instance',
    '.monaco-tokenized-source',
    'pre',
    'code',
    'kbd',
    'samp',
    'var',
    '.code-block',
    '.hljs',
    '.syntax-highlighted',
    '.highlight',
    '.terminal',
    '.xterm',
    '.xterm-screen',
    '.xterm-viewport',
    '.terminal-wrapper',
    'textarea',
    '[contenteditable="true"]',
    '[contenteditable=""]',
    '[contenteditable]:not([contenteditable="false"])',
    '[data-no-translate]',
    '[translate="no"]',
    'svg',
    'canvas'
  ].join(', ');

  // Helper: Normalize non-breaking space
  function normalize(str) {{
    if (!str) return '';
    return str.replace(/\\u00a0/g, ' ');
  }}

  // Helper: Format timer unit (ms vs s)
  function formatTimerUnit(unit) {{
    if (!unit) return '\\u79d2';
    return unit.toLowerCase().startsWith('ms') ? '\\u6beb\\u79d2' : '\\u79d2';
  }}

  // 5. Dynamic Pattern Matcher Pipeline (18 Rules)
  function matchDynamicPatterns(trimmed) {{
    let m;

    // Rule 1-4: Live Thinking Timer State
    if ((m = trimmed.match(/^(?:Thinking|Thought)\\s+for\\s+(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?$/i))) {{
      return `\\u601d\\u8003\\u4e2d (${{m[1]}}${{formatTimerUnit(m[2])}})`;
    }}
    if ((m = trimmed.match(/^Thinking\\.\\.\\.\\s*\\(?(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?\\)?$/i))) {{
      return `\\u601d\\u8003\\u4e2d... (${{m[1]}}${{formatTimerUnit(m[2])}})`;
    }}
    if ((m = trimmed.match(/^(?:Thinking|Thought)\\s*\\((\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?\\)$/i)) ||
        (m = trimmed.match(/^(?:Thinking|Thought)\\s+(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)$/i))) {{
      return `\\u601d\\u8003\\u4e2d (${{m[1]}}${{formatTimerUnit(m[2])}})`;
    }}

    // Rule 5-7: Live Working Timer State
    if ((m = trimmed.match(/^(?:Working|Worked)\\s+for\\s+(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?$/i))) {{
      return `\\u5904\\u7406\\u4e2d (${{m[1]}}${{formatTimerUnit(m[2])}})`;
    }}
    if ((m = trimmed.match(/^Working\\.\\.\\.\\s*\\(?(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?\\)?$/i))) {{
      return `\\u5904\\u7406\\u4e2d... (${{m[1]}}${{formatTimerUnit(m[2])}})`;
    }}
    if ((m = trimmed.match(/^(?:Working|Worked)\\s*\\((\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?\\)$/i)) ||
        (m = trimmed.match(/^(?:Working|Worked)\\s+(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)$/i))) {{
      return `\\u5904\\u7406\\u4e2d (${{m[1]}}${{formatTimerUnit(m[2])}})`;
    }}

    // Rule 8-11: Completion & Execution Duration Timers
    if ((m = trimmed.match(/^(Completed|Finished|Done)\\s+in\\s+(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?$/i))) {{
      return `\\u5df2\\u5b8c\\u6210 (\\u8017\\u65f6 ${{m[2]}}${{formatTimerUnit(m[3])}})`;
    }}
    if ((m = trimmed.match(/^Timed\\s+(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?$/i))) {{
      return `\\u5df2\\u8ba1\\u65f6 ${{m[1]}}${{formatTimerUnit(m[2])}}`;
    }}
    if ((m = trimmed.match(/^Elapsed\\s+time:\\s*(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?$/i))) {{
      return `\\u8017\\u65f6: ${{m[1]}}${{formatTimerUnit(m[2])}}`;
    }}
    if ((m = trimmed.match(/^Total\\s+duration:\\s*(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?$/i))) {{
      return `\\u603b\\u8017\\u65f6: ${{m[1]}}${{formatTimerUnit(m[2])}}`;
    }}
    if ((m = trimmed.match(/^Execution\\s+time:\\s*(\\d+(?:\\.\\d+)?)\\s*(s|seconds?|ms)?$/i))) {{
      return `\\u6267\\u884c\\u8017\\u65f6: ${{m[1]}}${{formatTimerUnit(m[2])}}`;
    }}

    // Rule 12: Special Relative Times
    if (/^just\\s+now$/i.test(trimmed)) {{
      return '\\u521a\\u521a';
    }}
    if (/^a\\s+few\\s+seconds\\s+ago$/i.test(trimmed)) {{
      return '\\u51e0\\u79d2\\u524d';
    }}
    if (/^a\\s+minute\\s+ago$/i.test(trimmed)) {{
      return '1\\u5206\\u949f\\u524d';
    }}
    if (/^an\\s+hour\\s+ago$/i.test(trimmed)) {{
      return '1\\u5c0f\\u65f6\\u524d';
    }}
    if (/^a\\s+day\\s+ago$/i.test(trimmed)) {{
      return '1\\u5929\\u524d';
    }}
    if (/^today$/i.test(trimmed)) {{
      return '\\u4eca\\u5929';
    }}
    if (/^yesterday$/i.test(trimmed)) {{
      return '\\u6628\\u5929';
    }}

    // Rule 13: Date Header Prefixes: Today ... / Yesterday ...
    if (trimmed.startsWith('Today ')) {{
      return trimmed.replace('Today ', '\\u4eca\\u5929 ');
    }}
    if (trimmed.startsWith('Yesterday ')) {{
      return trimmed.replace('Yesterday ', '\\u6628\\u5929 ');
    }}

    // Rule 14: Compact Relative Timestamps: 10d, 5m, 1mo, 2h, 30s, 1y (with optional 'ago')
    if ((m = trimmed.match(/^(\\d+)\\s*(mo|[dmhsy])(?:\\s+ago)?$/i))) {{
      const unit = m[2].toLowerCase();
      const cn = UNIT_MAP_CN[unit];
      if (cn) return `${{m[1]}}${{cn}}`;
    }}

    // Rule 15: Verbose Relative Timestamps: 5 minutes ago, 2 days ago, 1 month ago, 10 mins ago, 2 hrs ago
    if ((m = trimmed.match(/^(\\d+)\\s*(months?|days?|hours?|hrs?|minutes?|mins?|seconds?|secs?|years?|yrs?)\\s+ago$/i))) {{
      const unit = m[2].toLowerCase();
      const cn = UNIT_MAP_CN[unit];
      if (cn) return `${{m[1]}}${{cn}}`;
    }}

    // Rule 16: Dynamic Pane Badges & Workspace Counters
    if ((m = trimmed.match(/^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks|MCP Servers)\\s+(\\d+)$/i))) {{
      const typeMap = {{
        'subagents': '\\u5b50\\u667a\\u80fd\\u4f53',
        'files changed': '\\u5df2\\u4fee\\u6539\\u6587\\u4ef6',
        'artifacts': '\\u4ea7\\u7269',
        'uploads': '\\u5df2\\u4e0a\\u4f20\\u6587\\u4ef6',
        'background tasks': '\\u540e\\u53f0\\u4efb\\u52a1',
        'mcp servers': 'MCP \\u670d\\u52a1'
      }};
      const label = typeMap[m[1].toLowerCase()] || m[1];
      return `${{label}} ${{m[2]}}`;
    }}

    // Rule 17: File change counters: N files changed / modified / added / deleted
    if ((m = trimmed.match(/^(\\d+)\\s+files?\\s+changed$/i))) {{
      return `${{m[1]}} \\u4e2a\\u6587\\u4ef6\\u5df2\\u4fee\\u6539`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+files?\\s+modified$/i))) {{
      return `${{m[1]}} \\u4e2a\\u6587\\u4ef6\\u5df2\\u4fee\\u6539`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+files?\\s+added$/i))) {{
      return `${{m[1]}} \\u4e2a\\u6587\\u4ef6\\u5df2\\u6dfb\\u52a0`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+files?\\s+deleted$/i))) {{
      return `${{m[1]}} \\u4e2a\\u6587\\u4ef6\\u5df2\\u5220\\u9664`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+files?$/i))) {{
      return `${{m[1]}} \\u4e2a\\u6587\\u4ef6`;
    }}

    // Rule 18: Subagent, Item, and Task Counters
    if ((m = trimmed.match(/^(\\d+)\\s+subagents?$/i))) {{
      return `${{m[1]}} \\u4e2a\\u5b50\\u667a\\u80fd\\u4f53`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+agents?\\s+running$/i))) {{
      return `${{m[1]}} \\u4e2a\\u667a\\u80fd\\u4f53\\u8fd0\\u884c\\u4e2d`;
    }}
    if (/^No\\s+agents?\\s+running$/i.test(trimmed)) {{
      return '0 \\u4e2a\\u667a\\u80fd\\u4f53\\u8fd0\\u884c\\u4e2d';
    }}
    if (/^1\\s+agent\\s+running$/i.test(trimmed)) {{
      return '1 \\u4e2a\\u667a\\u80fd\\u4f53\\u8fd0\\u884c\\u4e2d';
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+items?\\s+selected$/i))) {{
      return `\\u5df2\\u9009 ${{m[1]}} \\u9879`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+selected$/i))) {{
      return `\\u5df2\\u9009 ${{m[1]}} \\u9879`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+tasks?$/i))) {{
      return `${{m[1]}} \\u4e2a\\u4efb\\u52a1`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+artifacts?$/i))) {{
      return `${{m[1]}} \\u4e2a\\u4ea7\\u7269`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+changes?$/i))) {{
      return `${{m[1]}} \\u5904\\u66f4\\u6539`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+errors?$/i))) {{
      return `${{m[1]}} \\u4e2a\\u9519\\u8bef`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+warnings?$/i))) {{
      return `${{m[1]}} \\u4e2a\\u8b66\\u544a`;
    }}
    if ((m = trimmed.match(/^(\\d+)\\s+results?$/i))) {{
      return `${{m[1]}} \\u4e2a\\u7ed3\\u679c`;
    }}

    return null;
  }}

  // 6. Master Text Translation Dispatcher
  function translateText(text) {{
    if (!text || typeof text !== 'string') return null;
    const normalized = normalize(text);
    const trimmed = normalized.trim();
    if (!trimmed) return null;

    // 1. Direct dictionary match
    if (dictionary[trimmed]) {{
      return normalized.replace(trimmed, dictionary[trimmed]);
    }}
    if (dictionary[normalized]) {{
      return dictionary[normalized];
    }}

    // 2. Dynamic regex matchers
    const dynamicMatch = matchDynamicPatterns(trimmed);
    if (dynamicMatch !== null) {{
      return normalized.replace(trimmed, dynamicMatch);
    }}

    // 3. Substring replacements
    let newText = normalized;
    let modified = false;
    for (let i = 0; i < substringReplacements.length; i++) {{
      const item = substringReplacements[i];
      if (newText.includes(item.search)) {{
        newText = newText.replaceAll(item.search, item.replace);
        modified = true;
      }}
    }}
    if (modified) return newText;

    return null;
  }}

  // 7. Safety Bypass Checks
  function isBypassedElement(el) {{
    if (!el || el.nodeType !== 1) return false;
    if (IGNORE_TAGS.has(el.tagName)) return true;
    if (el.isContentEditable) return true;
    if (el.getAttribute && el.getAttribute('contenteditable') === 'true') return true;

    if (el.matches && el.matches(BYPASS_ANCESTOR_SELECTOR)) return true;
    if (el.closest && el.closest(BYPASS_ANCESTOR_SELECTOR)) return true;

    const className = (typeof el.className === 'string') ? el.className : (el.getAttribute ? (el.getAttribute('class') || '') : '');
    if (className) {{
      const bypassClasses = ['monaco-editor', 'view-lines', 'monaco-list-row', 'terminal', 'xterm', 'code-block', 'hljs', 'cm-editor', 'cm-content'];
      for (let i = 0; i < bypassClasses.length; i++) {{
        if (className.includes(bypassClasses[i])) return true;
      }}
    }}
    return false;
  }}

  function isBypassedNode(node) {{
    if (!node) return true;
    if (node.nodeType === 3) {{
      const parent = node.parentElement || node.parentNode;
      if (!parent || parent.nodeType !== 1) return false;
      const parentTag = parent.tagName ? parent.tagName.toUpperCase() : '';
      if (IGNORE_TAGS.has(parentTag) || CODE_OR_INPUT_TAGS.has(parentTag)) return true;
      if (parent.isContentEditable) return true;
      if (parent.closest && parent.closest(BYPASS_ANCESTOR_SELECTOR)) return true;
      return isBypassedElement(parent);
    }}
    if (node.nodeType === 1) {{
      return isBypassedElement(node);
    }}
    return false;
  }}

  function translateAttributes(el, attrs) {{
    if (!el || !el.getAttribute) return;
    for (let i = 0; i < attrs.length; i++) {{
      const attr = attrs[i];
      if (el.hasAttribute && el.hasAttribute(attr)) {{
        const val = el.getAttribute(attr);
        if (val && typeof val === 'string') {{
          const trans = translateText(val);
          if (trans !== null && trans !== val) {{
            el.setAttribute(attr, trans);
          }}
        }}
      }}
    }}
  }}

  // 8. Recursive DOM and Shadow DOM Walker
  function walk(node) {{
    if (!node) return;

    // Text Node (Type 3)
    if (node.nodeType === 3) {{
      if (isBypassedNode(node)) return;
      const text = node.nodeValue;
      if (text && typeof text === 'string') {{
        const trans = translateText(text);
        if (trans !== null && trans !== text) {{
          node.nodeValue = trans;
        }}
      }}
      return;
    }}

    // DocumentFragment / ShadowRoot (Type 11)
    if (node.nodeType === 11) {{
      for (let child = node.firstChild; child; child = child.nextSibling) {{
        walk(child);
      }}
      return;
    }}

    // Element Node (Type 1)
    if (node.nodeType === 1) {{
      const tag = node.tagName ? node.tagName.toUpperCase() : '';

      // A. Ignore script, style, svg, canvas, etc.
      if (IGNORE_TAGS.has(tag)) return;

      // B. Textarea: translate safe attributes only, do not touch children/value
      if (tag === 'TEXTAREA') {{
        translateAttributes(node, SAFE_ATTRS);
        return;
      }}

      // C. Input elements
      if (tag === 'INPUT') {{
        const itype = (node.getAttribute('type') || 'text').toLowerCase();
        if (BUTTON_INPUT_TYPES.has(itype)) {{
          translateAttributes(node, [...SAFE_ATTRS, 'value']);
        }} else {{
          translateAttributes(node, SAFE_ATTRS);
        }}
        return;
      }}

      // D. Protected Containers & Code Blocks: prune subtree
      const isSelfBypassed = (
        CODE_OR_INPUT_TAGS.has(tag) ||
        (node.matches && node.matches(BYPASS_ANCESTOR_SELECTOR)) ||
        isBypassedElement(node)
      );

      if (isSelfBypassed) {{
        translateAttributes(node, SAFE_ATTRS);
        return;
      }}

      // E. Normal Element: Translate safe attributes
      translateAttributes(node, SAFE_ATTRS);

      // F. Traverse Open Shadow DOM
      if (node.shadowRoot) {{
        observeRoot(node.shadowRoot);
        walk(node.shadowRoot);
      }}

      // G. Traverse Child Nodes
      for (let child = node.firstChild; child; child = child.nextSibling) {{
        walk(child);
      }}
    }}
  }}

  // 9. MutationObserver Setup & Lifecycle
  let observer = null;
  const observedRoots = new WeakSet();
  const observerConfig = {{
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true,
    attributeFilter: ['placeholder', 'title', 'aria-label', 'value']
  }};

  function observeRoot(root) {{
    if (!root || !observer || observedRoots.has(root)) return;
    try {{
      observedRoots.add(root);
      observer.observe(root, observerConfig);
    }} catch (e) {{
      // Fail-safe
    }}
  }}

  function startObserver() {{
    if (observer) return;
    if (typeof MutationObserver === 'undefined') return;

    observer = new MutationObserver(mutations => {{
      for (let i = 0; i < mutations.length; i++) {{
        const m = mutations[i];
        if (m.type === 'childList') {{
          for (let j = 0; j < m.addedNodes.length; j++) {{
            const added = m.addedNodes[j];
            if (added.nodeType === 1 && added.shadowRoot) {{
              observeRoot(added.shadowRoot);
            }}
            walk(added);
          }}
        }} else if (m.type === 'characterData') {{
          const node = m.target;
          if (!isBypassedNode(node)) {{
            const trans = translateText(node.nodeValue);
            if (trans !== null && trans !== node.nodeValue) {{
              node.nodeValue = trans;
            }}
          }}
        }} else if (m.type === 'attributes') {{
          const el = m.target;
          const attr = m.attributeName;
          if (el.nodeType === 1 && !isBypassedElement(el) && el.getAttribute) {{
            if (attr === 'value') {{
              if (el.tagName === 'INPUT') {{
                const itype = (el.getAttribute('type') || 'text').toLowerCase();
                if (BUTTON_INPUT_TYPES.has(itype)) {{
                  const val = el.getAttribute('value');
                  const trans = translateText(val);
                  if (trans !== null && trans !== val) el.setAttribute('value', trans);
                }}
              }}
            }} else if (SAFE_ATTRS.includes(attr)) {{
              const val = el.getAttribute(attr);
              const trans = translateText(val);
              if (trans !== null && trans !== val) el.setAttribute(attr, trans);
            }}
          }}
        }}
      }}
    }});

    if (typeof document !== 'undefined' && document.body) {{
      observeRoot(document.body);
    }}
  }}

  // 10. Intercept Element.prototype.attachShadow for dynamic Web Components
  if (typeof Element !== 'undefined' && Element.prototype && Element.prototype.attachShadow) {{
    const origAttachShadow = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function(init) {{
      const shadowRoot = origAttachShadow.apply(this, arguments);
      try {{
        if (shadowRoot) {{
          observeRoot(shadowRoot);
          walk(shadowRoot);
        }}
      }} catch (e) {{
        // Fail-safe
      }}
      return shadowRoot;
    }};
  }}

  // 11. Hook DOM Ready State
  if (typeof document !== 'undefined') {{
    if (document.readyState === 'loading') {{
      document.addEventListener('DOMContentLoaded', () => {{
        walk(document.body);
        startObserver();
      }});
    }} else {{
      walk(document.body);
      startObserver();
    }}
  }}

  // 12. Global CommonJS Exports for testing and decoupled loader
  if (typeof module !== 'undefined' && module.exports) {{
    module.exports = {{
      dictionary,
      substringReplacements,
      UNIT_MAP_CN,
      normalize,
      formatTimerUnit,
      matchDynamicPatterns,
      translateText,
      isBypassedElement,
      isBypassedNode,
      walk,
      startObserver
    }};
  }}
}})();
"""
    return engine_js

def generate_preload_js(engine_js):
    host_header = """\"use strict\";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Preload script -- runs in every BrowserWindow before the page loads.
 * Exposes a minimal, secure API via contextBridge so the renderer can
 * communicate with the main-process auto-updater without nodeIntegration.
 */
const electron_1 = require("electron");
const updaterAPI = {
    onStateChanged: (callback) => {
        const handler = (_event, state) => {
            callback(state);
        };
        electron_1.ipcRenderer.on('updater:state-changed', handler);
        return () => {
            electron_1.ipcRenderer.removeListener('updater:state-changed', handler);
        };
    },
    checkForUpdates: () => electron_1.ipcRenderer.invoke('updater:check'),
    quitAndInstall: () => electron_1.ipcRenderer.invoke('updater:quit-and-install'),
    getUpdateChannel: () => electron_1.ipcRenderer.invoke('updater:get-channel'),
    setUpdateChannel: (channel) => electron_1.ipcRenderer.invoke('updater:set-channel', channel),
};
const ideAPI = {
    launch: (appPath, projectPath) => electron_1.ipcRenderer.invoke('ide:launch', appPath, projectPath),
    getAvailableApps: () => electron_1.ipcRenderer.invoke('ide:get-available-apps'),
    getDefaultIde: () => electron_1.ipcRenderer.invoke('ide:get-default-ide'),
    setDefaultIde: (bundleId) => electron_1.ipcRenderer.invoke('ide:set-default-ide', bundleId),
    installAgyCli: () => electron_1.ipcRenderer.invoke('ide:install-agy-cli'),
};
const electronNativeAPI = {
    getPlatform: () => process.platform,
    getDeepLink: () => electron_1.ipcRenderer.invoke('deep-link:get-stored'),
    onDeepLinkReceived: (callback) => {
        const handler = (_event, link) => {
            callback(link);
        };
        electron_1.ipcRenderer.on('deep-link:received', handler);
        return () => {
            electron_1.ipcRenderer.removeListener('deep-link:received', handler);
        };
    },
};
electron_1.contextBridge.exposeInMainWorld('updater', updaterAPI);
electron_1.contextBridge.exposeInMainWorld('electronNative', electronNativeAPI);
electron_1.contextBridge.exposeInMainWorld('ide', ideAPI);

"""
    full_preload = host_header + engine_js + "\n"
    print(f"Generating {PRELOAD_PATH}...")
    with open(PRELOAD_PATH, "w", encoding="ascii") as f:
        f.write(full_preload)
    print("  -> dist/preload.js created.")

def generate_engine_js(engine_js):
    print(f"Generating {ENGINE_PATH}...")
    with open(ENGINE_PATH, "w", encoding="ascii") as f:
        f.write(engine_js + "\n")
    print("  -> dist/engine.js created.")

def verify_artifacts():
    print("\n--- Verifying Artifacts ---")
    # 1. Verify dist/dictionary.json
    with open(DICT_PATH, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert len(d) == 514, f"Expected 514 keys, got {len(d)}"
    assert d["Files Changed"] == "已修改文件", "Typo in Files Changed"
    assert "无法修改" in d["Agent cannot modify files outside of the workspace in strict mode."], "Typo in Agent cannot modify files..."
    for k, v in d.items():
        assert "修政" not in v, f"Typo '修政' found in {k}: {v}"
        assert "无法修政" not in v, f"Typo '无法修政' found in {k}: {v}"
    print(f"1. dist/dictionary.json: PASS ({len(d)} keys, 0 typos, valid UTF-8)")

    # 2. Verify dist/preload.js
    with open(PRELOAD_PATH, "rb") as f:
        preload_bytes = f.read()
    max_byte_preload = max(preload_bytes)
    assert max_byte_preload <= 127, f"preload.js contains non-ASCII bytes (max: {max_byte_preload})"
    preload_str = preload_bytes.decode("ascii")
    assert "// Antigravity Chinese Localization Patch" in preload_str
    assert "exposeInMainWorld" in preload_str
    assert "matchDynamicPatterns" in preload_str
    assert "\\u4fee\\u653f" not in preload_str, "Found \\u4fee\\u653f (修政) in preload.js"
    assert "\\u5df2\\u4fee\\u653f" not in preload_str, "Found \\u5df2\\u4fee\\u653f (已修政) in preload.js"
    print(f"2. dist/preload.js: PASS (Pure 7-bit ASCII, max byte={max_byte_preload}, host stubs intact)")

    # 3. Verify dist/engine.js
    with open(ENGINE_PATH, "rb") as f:
        engine_bytes = f.read()
    max_byte_engine = max(engine_bytes)
    assert max_byte_engine <= 127, f"engine.js contains non-ASCII bytes (max: {max_byte_engine})"
    engine_str = engine_bytes.decode("ascii")
    assert "// Antigravity Chinese Localization Patch" in engine_str
    assert "module.exports" in engine_str
    assert "\\u4fee\\u653f" not in engine_str, "Found \\u4fee\\u653f (修政) in engine.js"
    assert "\\u5df2\\u4fee\\u653f" not in engine_str, "Found \\u5df2\\u4fee\\u653f (已修政) in engine.js"
    print(f"3. dist/engine.js: PASS (Pure 7-bit ASCII, max byte={max_byte_engine}, decoupled module exports)")

if __name__ == "__main__":
    generate_dictionary_json()
    core_engine = generate_engine_core_js()
    generate_preload_js(core_engine)
    generate_engine_js(core_engine)
    verify_artifacts()
