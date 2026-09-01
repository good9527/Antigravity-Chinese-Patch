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

function formatTimerUnit(unit) {
  if (!unit) return '\u79d2'; // 秒
  return unit.toLowerCase().startsWith('ms') ? '\u6beb\u79d2' : '\u79d2'; // 毫秒 : 秒
}

function matchDynamicPatterns(trimmed) {
  let m;

  // 1. Thinking timers
  // 'Thinking for 1.2s', 'Thinking for 800ms', 'Thought for 1.2s', 'Thinking... 1.2s', 'Thinking (1.2s)'
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

const testCases = [
  // Timers
  ['Thinking for 1.2s', '\u601d\u8003\u4e2d (1.2\u79d2)'],
  ['Thinking for 0.4s', '\u601d\u8003\u4e2d (0.4\u79d2)'],
  ['Thinking for 850ms', '\u601d\u8003\u4e2d (850\u6beb\u79d2)'],
  ['Thinking for 1 second', '\u601d\u8003\u4e2d (1\u79d2)'],
  ['Thinking for 2 seconds', '\u601d\u8003\u4e2d (2\u79d2)'],
  ['Thought for 1.2s', '\u5df2\u601d\u8003 (1.2\u79d2)'],
  ['Thought for 500ms', '\u5df2\u601d\u8003 (500\u6beb\u79d2)'],
  ['Thinking... 1.2s', '\u601d\u8003\u4e2d... (1.2\u79d2)'],
  ['Thinking (1.5s)', '\u601d\u8003\u4e2d (1.5\u79d2)'],
  ['Working for 3.4s', '\u5904\u7406\u4e2d (3.4\u79d2)'],
  ['Working for 800ms', '\u5904\u7406\u4e2d (800\u6beb\u79d2)'],
  ['Worked for 3.4s', '\u5df2\u5904\u7406 (3.4\u79d2)'],
  ['Working... 3.4s', '\u5904\u7406\u4e2d... (3.4\u79d2)'],
  ['Completed in 12.3s', '\u5df2\u5b8c\u6210 (\u8017\u65f6 12.3\u79d2)'],
  ['Completed in 500ms', '\u5df2\u5b8c\u6210 (\u8017\u65f6 500\u6beb\u79d2)'],
  ['Finished in 1.5s', '\u5df2\u5b8c\u6210 (\u8017\u65f6 1.5\u79d2)'],
  ['Done in 0.8s', '\u5df2\u5b8c\u6210 (\u8017\u65f6 0.8\u79d2)'],
  ['Timed 1.2s', '\u5df2\u8ba1\u65f6 1.2\u79d2'],

  // Timestamps
  ['10d', '10\u5929\u524d'],
  ['5m', '5\u5206\u949f\u524d'],
  ['1mo', '1\u4e2a\u6708\u524d'],
  ['2mo', '2\u4e2a\u6708\u524d'],
  ['2h', '2\u5c0f\u65f6\u524d'],
  ['30s', '30\u79d2\u524d'],
  ['1y', '1\u5e74\u524d'],
  ['5m ago', '5\u5206\u949f\u524d'],
  ['10d ago', '10\u5929\u524d'],
  ['1mo ago', '1\u4e2a\u6708\u524d'],
  ['5 minutes ago', '5\u5206\u949f\u524d'],
  ['2 days ago', '2\u5929\u524d'],
  ['1 month ago', '1\u4e2a\u6708\u524d'],
  ['Just now', '\u521a\u521a'],
  ['just now', '\u521a\u521a'],
  ['Today 14:30', '\u4eca\u5929 14:30'],
  ['Today at 14:30', '\u4eca\u5929 14:30'],
  ['Yesterday 09:15', '\u6628\u5929 09:15'],
  ['Yesterday at 09:15', '\u6628\u5929 09:15'],

  // Counters
  ['Subagents 0', '\u5b50\u667a\u80fd\u4f53 0'],
  ['Subagents 3', '\u5b50\u667a\u80fd\u4f53 3'],
  ['Files Changed 3', '\u5df2\u4fee\u6539\u6587\u4ef6 3'],
  ['Artifacts 2', '\u4ea7\u7269 2'],
  ['Uploads 5', '\u5df2\u4e0a\u4f20\u6587\u4ef6 5'],
  ['Background Tasks 1', '\u540e\u53f0\u4efb\u52a1 1'],
  ['MCP Servers 3', 'MCP \u670d\u52a1 3'],
  ['0 files changed', '0 \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539'],
  ['1 file changed', '1 \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539'],
  ['5 files changed', '5 \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539'],
  ['1 subagent', '1 \u4e2a\u5b50\u667a\u80fd\u4f53'],
  ['3 subagents', '3 \u4e2a\u5b50\u667a\u80fd\u4f53'],
  ['No agents running', '0 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d'],
  ['1 agent running', '1 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d'],
  ['4 agents running', '4 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d'],
  ['1 item selected', '\u5df2\u9009 1 \u9879'],
  ['5 items selected', '\u5df2\u9009 5 \u9879'],
  ['1 task', '1 \u4e2a\u4efb\u52a1'],
  ['2 tasks', '2 \u4e2a\u4efb\u52a1'],
  ['1 artifact', '1 \u4e2a\u4ea7\u7269'],
  ['3 artifacts', '3 \u4e2a\u4ea7\u7269'],
  ['1 change', '1 \u5904\u66f4\u6539'],
  ['3 changes', '3 \u5904\u66f4\u6539']
];

let failed = 0;
for (const [input, expected] of testCases) {
  const actual = matchDynamicPatterns(input);
  if (actual !== expected) {
    console.error(`FAILED: '${input}' => Expected: '${expected}', Actual: '${actual}'`);
    failed++;
  }
}

if (failed === 0) {
  console.log(`SUCCESS! All ${testCases.length} dynamic pattern test cases passed cleanly!`);
} else {
  console.error(`Failed count: ${failed}`);
  process.exit(1);
}
