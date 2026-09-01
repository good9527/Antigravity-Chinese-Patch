/**
 * Antigravity Chinese Localization Engine - Dynamic Matchers & DOM Lifecycle Test
 */

const DICTIONARY = {
  "New Conversation": "\u65b0\u5efa\u5bf9\u8bdd",
  "Conversation History": "\u5386\u53f2\u5bf9\u8bdd",
  "Scheduled Tasks": "\u8ba1\u5212\u4efb\u52a1",
  "Projects": "\u9879\u76ee\u5217\u8868",
  "Settings": "\u8bbe\u7f6e",
  "Untitled Conversation": "\u672a\u547d\u540d\u5bf9\u8bdd",
  "Save": "\u4fdd\u5b58",
  "Delete": "\u5220\u9664",
  "Thinking...": "\u601d\u8003\u4e2d...",
  "Working...": "\u5904\u7406\u4e2d..."
};

const SUBSTRING_REPLACEMENTS = [
  { search: 'Minimize', replace: '\u6700\u5c0f\u5316' },
  { search: 'Maximize', replace: '\u6700\u5927\u5316' },
  { search: 'Toggle Developer Tools', replace: '\u5207\u6362\u5f00\u53d1\u8005\u5de5\u5177' },
  { search: 'Default', replace: '\u9ed8\u8ba4' },
  { search: 'Full Machine', replace: '\u6574\u673a\u6388\u6743' },
  { search: 'Turbo Mode', replace: '\u6781\u901f\u6a21\u5f0f' },
  { search: 'Turbo mode', replace: '\u6781\u901f\u6a21\u5f0f' },
  { search: 'Custom', replace: '\u81ea\u5b9a\u4e49' },
  { search: 'System', replace: '\u8ddf\u968f\u7cfb\u7edf' }
];

const UNIT_MAP_CN = {
  'mo': '\u4e2a\u6708\u524d',
  'month': '\u4e2a\u6708\u524d',
  'months': '\u4e2a\u6708\u524d',
  'd': '\u5929\u524d',
  'day': '\u5929\u524d',
  'days': '\u5929\u524d',
  'm': '\u5206\u949f\u524d',
  'min': '\u5206\u949f\u524d',
  'mins': '\u5206\u949f\u524d',
  'minute': '\u5206\u949f\u524d',
  'minutes': '\u5206\u949f\u524d',
  'h': '\u5c0f\u65f6\u524d',
  'hr': '\u5c0f\u65f6\u524d',
  'hrs': '\u5c0f\u65f6\u524d',
  'hour': '\u5c0f\u65f6\u524d',
  'hours': '\u5c0f\u65f6\u524d',
  's': '\u79d2\u524d',
  'sec': '\u79d2\u524d',
  'secs': '\u79d2\u524d',
  'second': '\u79d2\u524d',
  'seconds': '\u79d2\u524d',
  'y': '\u5e74\u524d',
  'yr': '\u5e74\u524d',
  'yrs': '\u5e74\u524d',
  'year': '\u5e74\u524d',
  'years': '\u5e74\u524d'
};

const BYPASS_TAGS = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEXTAREA', 'CODE', 'PRE', 'CANVAS']);
const BYPASS_CLASSES = [
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
];

function normalize(str) {
  if (!str) return '';
  return str.replace(/\u00a0/g, ' ');
}

function formatTimerUnit(unit) {
  if (!unit) return '\u79d2'; // 秒
  return unit.toLowerCase().startsWith('ms') ? '\u6beb\u79d2' : '\u79d2'; // 毫秒 : 秒
}

function matchDynamicPatterns(trimmed) {
  let m;

  // 1. Thinking timers
  if ((m = trimmed.match(/^Thinking\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u601d\u8003\u4e2d (${m[1]}${formatTimerUnit(m[2])})`;
  }
  if ((m = trimmed.match(/^Thought\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u5df2\u601d\u8003 (${m[1]}${formatTimerUnit(m[2])})`;
  }
  if ((m = trimmed.match(/^Thinking\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$/i))) {
    return `\u601d\u8003\u4e2d... (${m[1]}${formatTimerUnit(m[2])})`;
  }
  if ((m = trimmed.match(/^Thinking\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$/i)) ||
      (m = trimmed.match(/^Thinking\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$/i))) {
    return `\u601d\u8003\u4e2d (${m[1]}${formatTimerUnit(m[2])})`;
  }
  if ((m = trimmed.match(/^Thought\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$/i))) {
    return `\u5df2\u601d\u8003 (${m[1]}${formatTimerUnit(m[2])})`;
  }

  // 2. Working timers
  if ((m = trimmed.match(/^Working\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u5904\u7406\u4e2d (${m[1]}${formatTimerUnit(m[2])})`;
  }
  if ((m = trimmed.match(/^Worked\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u5df2\u5904\u7406 (${m[1]}${formatTimerUnit(m[2])})`;
  }
  if ((m = trimmed.match(/^Working\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$/i))) {
    return `\u5904\u7406\u4e2d... (${m[1]}${formatTimerUnit(m[2])})`;
  }
  if ((m = trimmed.match(/^Working\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$/i)) ||
      (m = trimmed.match(/^Working\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$/i))) {
    return `\u5904\u7406\u4e2d (${m[1]}${formatTimerUnit(m[2])})`;
  }

  // 3. Completion & Duration
  if ((m = trimmed.match(/^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u5df2\u5b8c\u6210 (\u8017\u65f6 ${m[2]}${formatTimerUnit(m[3])})`;
  }
  if ((m = trimmed.match(/^Timed\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u5df2\u8ba1\u65f6 ${m[1]}${formatTimerUnit(m[2])}`;
  }
  if ((m = trimmed.match(/^Elapsed\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u8017\u65f6: ${m[1]}${formatTimerUnit(m[2])}`;
  }
  if ((m = trimmed.match(/^Total\s+duration:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u603b\u8017\u65f6: ${m[1]}${formatTimerUnit(m[2])}`;
  }
  if ((m = trimmed.match(/^Execution\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
    return `\u6267\u884c\u8017\u65f6: ${m[1]}${formatTimerUnit(m[2])}`;
  }

  // 4. Relative Timestamps
  if (/^just\s+now$/i.test(trimmed)) {
    return '\u521a\u521a';
  }
  if (/^a\s+few\s+seconds\s+ago$/i.test(trimmed)) {
    return '\u51e0\u79d2\u524d';
  }
  if (/^a\s+minute\s+ago$/i.test(trimmed)) {
    return '1\u5206\u949f\u524d';
  }
  if (/^an\s+hour\s+ago$/i.test(trimmed)) {
    return '1\u5c0f\u65f6\u524d';
  }
  if (/^a\s+day\s+ago$/i.test(trimmed)) {
    return '1\u5929\u524d';
  }
  if (/^yesterday$/i.test(trimmed)) {
    return '\u6628\u5929';
  }
  if (/^today$/i.test(trimmed)) {
    return '\u4eca\u5929';
  }
  if ((m = trimmed.match(/^Today\s+(?:at\s+)?(.+)$/i))) {
    return `\u4eca\u5929 ${m[1]}`;
  }
  if ((m = trimmed.match(/^Yesterday\s+(?:at\s+)?(.+)$/i))) {
    return `\u6628\u5929 ${m[1]}`;
  }

  // Compact relative: 10d, 5m, 1mo, 2h, 30s, 1y (with optional 'ago')
  if ((m = trimmed.match(/^(\d+)\s*(mo|[dmhsy])(?:\s+ago)?$/i))) {
    const unit = m[2].toLowerCase();
    const cn = UNIT_MAP_CN[unit];
    if (cn) return `${m[1]}${cn}`;
  }
  // Verbose relative: 5 minutes ago, 2 days ago, 1 month ago, 10 mins ago, 2 hrs ago
  if ((m = trimmed.match(/^(\d+)\s*(months?|days?|hours?|hrs?|minutes?|mins?|seconds?|secs?|years?|yrs?)\s+ago$/i))) {
    const unit = m[2].toLowerCase();
    const cn = UNIT_MAP_CN[unit];
    if (cn) return `${m[1]}${cn}`;
  }

  // 5. Dynamic Pane Badges & Counters
  if ((m = trimmed.match(/^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks|MCP Servers)\s+(\d+)$/i))) {
    const typeMap = {
      'subagents': '\u5b50\u667a\u80fd\u4f53',
      'files changed': '\u5df2\u4fee\u6539\u6587\u4ef6',
      'artifacts': '\u4ea7\u7269',
      'uploads': '\u5df2\u4e0a\u4f20\u6587\u4ef6',
      'background tasks': '\u540e\u53f0\u4efb\u52a1',
      'mcp servers': 'MCP \u670d\u52a1'
    };
    const label = typeMap[m[1].toLowerCase()] || m[1];
    return `${label} ${m[2]}`;
  }

  // File change counters: N files changed / modified / added / deleted
  if ((m = trimmed.match(/^(\d+)\s+files?\s+changed$/i))) {
    return `${m[1]} \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539`;
  }
  if ((m = trimmed.match(/^(\d+)\s+files?\s+modified$/i))) {
    return `${m[1]} \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539`;
  }
  if ((m = trimmed.match(/^(\d+)\s+files?\s+added$/i))) {
    return `${m[1]} \u4e2a\u6587\u4ef6\u5df2\u6dfb\u52a0`;
  }
  if ((m = trimmed.match(/^(\d+)\s+files?\s+deleted$/i))) {
    return `${m[1]} \u4e2a\u6587\u4ef6\u5df2\u5220\u9664`;
  }
  if ((m = trimmed.match(/^(\d+)\s+files?$/i))) {
    return `${m[1]} \u4e2a\u6587\u4ef6`;
  }

  // Subagents counter: N subagents
  if ((m = trimmed.match(/^(\d+)\s+subagents?$/i))) {
    return `${m[1]} \u4e2a\u5b50\u667a\u80fd\u4f53`;
  }

  // Running agents: N agents running / No agents running / 1 agent running
  if ((m = trimmed.match(/^(\d+)\s+agents?\s+running$/i))) {
    return `${m[1]} \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d`;
  }
  if (/^No\s+agents?\s+running$/i.test(trimmed)) {
    return '0 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d';
  }
  if (/^1\s+agent\s+running$/i.test(trimmed)) {
    return '1 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d';
  }

  // Other counters
  if ((m = trimmed.match(/^(\d+)\s+items?\s+selected$/i))) {
    return `\u5df2\u9009 ${m[1]} \u9879`;
  }
  if ((m = trimmed.match(/^(\d+)\s+selected$/i))) {
    return `\u5df2\u9009 ${m[1]} \u9879`;
  }
  if ((m = trimmed.match(/^(\d+)\s+tasks?$/i))) {
    return `${m[1]} \u4e2a\u4efb\u52a1`;
  }
  if ((m = trimmed.match(/^(\d+)\s+artifacts?$/i))) {
    return `${m[1]} \u4e2a\u4ea7\u7269`;
  }
  if ((m = trimmed.match(/^(\d+)\s+changes?$/i))) {
    return `${m[1]} \u5904\u66f4\u6539`;
  }
  if ((m = trimmed.match(/^(\d+)\s+errors?$/i))) {
    return `${m[1]} \u4e2a\u9519\u8bef`;
  }
  if ((m = trimmed.match(/^(\d+)\s+warnings?$/i))) {
    return `${m[1]} \u4e2a\u8b66\u544a`;
  }
  if ((m = trimmed.match(/^(\d+)\s+results?$/i))) {
    return `${m[1]} \u4e2a\u7ed3\u679c`;
  }

  return null;
}

function translateText(text) {
  if (!text || typeof text !== 'string') return null;
  const normalized = normalize(text);
  const trimmed = normalized.trim();
  if (!trimmed) return null;

  // 1. Direct dictionary match
  if (DICTIONARY[trimmed]) {
    return normalized.replace(trimmed, DICTIONARY[trimmed]);
  }
  if (DICTIONARY[normalized]) {
    return DICTIONARY[normalized];
  }

  // 2. Dynamic pattern matchers
  const dynamicMatch = matchDynamicPatterns(trimmed);
  if (dynamicMatch !== null) {
    return normalized.replace(trimmed, dynamicMatch);
  }

  // 3. Substring replacements
  let newText = normalized;
  let modified = false;
  for (let i = 0; i < SUBSTRING_REPLACEMENTS.length; i++) {
    const item = SUBSTRING_REPLACEMENTS[i];
    if (newText.includes(item.search)) {
      newText = newText.replaceAll(item.search, item.replace);
      modified = true;
    }
  }
  if (modified) return newText;

  return null;
}

function isBypassedElement(el) {
  if (!el || el.nodeType !== 1) return false;
  if (BYPASS_TAGS.has(el.tagName)) return true;
  if (el.isContentEditable) return true;
  if (el.getAttribute && el.getAttribute('contenteditable') === 'true') return true;

  const className = (typeof el.className === 'string') ? el.className : (el.getAttribute ? (el.getAttribute('class') || '') : '');
  if (className) {
    for (let i = 0; i < BYPASS_CLASSES.length; i++) {
      if (className.includes(BYPASS_CLASSES[i])) {
        return true;
      }
    }
  }
  return false;
}

function isBypassedNode(node) {
  if (!node) return true;
  if (node.nodeType === 3) {
    let parent = node.parentNode;
    while (parent && parent.nodeType === 1) {
      if (isBypassedElement(parent)) return true;
      parent = parent.parentNode;
    }
    return false;
  }
  if (node.nodeType === 1) {
    return isBypassedElement(node);
  }
  return false;
}

function walk(node) {
  if (!node) return;

  // Text Node
  if (node.nodeType === 3) {
    if (isBypassedNode(node)) return;
    const text = node.nodeValue;
    const trans = translateText(text);
    if (trans !== null && trans !== text) {
      node.nodeValue = trans;
    }
    return;
  }

  // DocumentFragment / ShadowRoot
  if (node.nodeType === 11) {
    for (let child = node.firstChild; child; child = child.nextSibling) {
      walk(child);
    }
    return;
  }

  // Element Node
  if (node.nodeType === 1) {
    if (isBypassedElement(node)) return;

    // Attributes translation: placeholder, title, aria-label
    const attrs = ['placeholder', 'title', 'aria-label'];
    for (let i = 0; i < attrs.length; i++) {
      const attr = attrs[i];
      if (node.hasAttribute && node.hasAttribute(attr)) {
        const val = node.getAttribute(attr);
        const trans = translateText(val);
        if (trans !== null && trans !== val) {
          node.setAttribute(attr, trans);
        }
      }
    }

    // Value attribute on button inputs only (NEVER on text inputs)
    if (node.tagName === 'INPUT' && node.hasAttribute && node.hasAttribute('value')) {
      const type = (node.getAttribute('type') || 'text').toLowerCase();
      if (type === 'button' || type === 'submit' || type === 'reset') {
        const val = node.getAttribute('value');
        const trans = translateText(val);
        if (trans !== null && trans !== val) {
          node.setAttribute('value', trans);
        }
      }
    }

    // Shadow DOM traversal
    if (node.shadowRoot) {
      walk(node.shadowRoot);
    }

    // Traverse child nodes
    for (let child = node.firstChild; child; child = child.nextSibling) {
      walk(child);
    }
  }
}

// Module export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    normalize,
    formatTimerUnit,
    matchDynamicPatterns,
    translateText,
    isBypassedElement,
    isBypassedNode,
    walk
  };
}
