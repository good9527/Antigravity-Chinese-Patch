import re

UNIT_MAP_CN = {
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
}

def format_timer_unit(unit):
    if not unit:
        return '\u79d2' # 秒
    return '\u6beb\u79d2' if unit.lower().startswith('ms') else '\u79d2'

def match_dynamic_patterns(trimmed):
    # 1. Thinking timers
    m = re.match(r'^Thinking\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u601d\u8003\u4e2d ({m.group(1)}{format_timer_unit(m.group(2))})"
    m = re.match(r'^Thought\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u5df2\u601d\u8003 ({m.group(1)}{format_timer_unit(m.group(2))})"
    m = re.match(r'^Thinking\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$', trimmed, re.I)
    if m:
        return f"\u601d\u8003\u4e2d... ({m.group(1)}{format_timer_unit(m.group(2))})"
    m = re.match(r'^Thinking\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$', trimmed, re.I) or re.match(r'^Thinking\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$', trimmed, re.I)
    if m:
        return f"\u601d\u8003\u4e2d ({m.group(1)}{format_timer_unit(m.group(2))})"
    m = re.match(r'^Thought\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$', trimmed, re.I)
    if m:
        return f"\u5df2\u601d\u8003 ({m.group(1)}{format_timer_unit(m.group(2))})"

    # 2. Working timers
    m = re.match(r'^Working\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u5904\u7406\u4e2d ({m.group(1)}{format_timer_unit(m.group(2))})"
    m = re.match(r'^Worked\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u5df2\u5904\u7406 ({m.group(1)}{format_timer_unit(m.group(2))})"
    m = re.match(r'^Working\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$', trimmed, re.I)
    if m:
        return f"\u5904\u7406\u4e2d... ({m.group(1)}{format_timer_unit(m.group(2))})"
    m = re.match(r'^Working\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$', trimmed, re.I) or re.match(r'^Working\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$', trimmed, re.I)
    if m:
        return f"\u5904\u7406\u4e2d ({m.group(1)}{format_timer_unit(m.group(2))})"

    # 3. Completion & Duration
    m = re.match(r'^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u5df2\u5b8c\u6210 (\u8017\u65f6 {m.group(2)}{format_timer_unit(m.group(3))})"
    m = re.match(r'^Timed\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u5df2\u8ba1\u65f6 {m.group(1)}{format_timer_unit(m.group(2))}"
    m = re.match(r'^Elapsed\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u8017\u65f6: {m.group(1)}{format_timer_unit(m.group(2))}"
    m = re.match(r'^Total\s+duration:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u603b\u8017\u65f6: {m.group(1)}{format_timer_unit(m.group(2))}"
    m = re.match(r'^Execution\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.I)
    if m:
        return f"\u6267\u884c\u8017\u65f6: {m.group(1)}{format_timer_unit(m.group(2))}"

    # 4. Relative Timestamps
    if re.match(r'^just\s+now$', trimmed, re.I):
        return '\u521a\u521a'
    if re.match(r'^a\s+few\s+seconds\s+ago$', trimmed, re.I):
        return '\u51e0\u79d2\u524d'
    if re.match(r'^a\s+minute\s+ago$', trimmed, re.I):
        return '1\u5206\u949f\u524d'
    if re.match(r'^an\s+hour\s+ago$', trimmed, re.I):
        return '1\u5c0f\u65f6\u524d'
    if re.match(r'^a\s+day\s+ago$', trimmed, re.I):
        return '1\u5929\u524d'
    if re.match(r'^yesterday$', trimmed, re.I):
        return '\u6628\u5929'
    if re.match(r'^today$', trimmed, re.I):
        return '\u4eca\u5929'
    m = re.match(r'^Today\s+(?:at\s+)?(.+)$', trimmed, re.I)
    if m:
        return f"\u4eca\u5929 {m.group(1)}"
    m = re.match(r'^Yesterday\s+(?:at\s+)?(.+)$', trimmed, re.I)
    if m:
        return f"\u6628\u5929 {m.group(1)}"

    # Compact relative
    m = re.match(r'^(\d+)\s*(mo|[dmhsy])(?:\s+ago)?$', trimmed, re.I)
    if m:
        unit = m.group(2).lower()
        cn = UNIT_MAP_CN.get(unit)
        if cn:
            return f"{m.group(1)}{cn}"

    # Verbose relative
    m = re.match(r'^(\d+)\s*(months?|days?|hours?|hrs?|minutes?|mins?|seconds?|secs?|years?|yrs?)\s+ago$', trimmed, re.I)
    if m:
        unit = m.group(2).lower()
        cn = UNIT_MAP_CN.get(unit)
        if cn:
            return f"{m.group(1)}{cn}"

    # 5. Dynamic Pane Badges & Counters
    m = re.match(r'^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks|MCP Servers)\s+(\d+)$', trimmed, re.I)
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

    m = re.match(r'^(\d+)\s+files?\s+changed$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539"
    m = re.match(r'^(\d+)\s+files?\s+modified$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539"
    m = re.match(r'^(\d+)\s+files?\s+added$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u6587\u4ef6\u5df2\u6dfb\u52a0"
    m = re.match(r'^(\d+)\s+files?\s+deleted$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u6587\u4ef6\u5df2\u5220\u9664"
    m = re.match(r'^(\d+)\s+files?$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u6587\u4ef6"
    m = re.match(r'^(\d+)\s+subagents?$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u5b50\u667a\u80fd\u4f53"
    m = re.match(r'^(\d+)\s+agents?\s+running$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d"
    if re.match(r'^No\s+agents?\s+running$', trimmed, re.I):
        return '0 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d'
    if re.match(r'^1\s+agent\s+running$', trimmed, re.I):
        return '1 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d'

    if re.match(r'^(\d+)\s+items?\s+selected$', trimmed, re.I):
        m = re.match(r'^(\d+)\s+items?\s+selected$', trimmed, re.I)
        return f"\u5df2\u9009 {m.group(1)} \u9879"
    if re.match(r'^(\d+)\s+selected$', trimmed, re.I):
        m = re.match(r'^(\d+)\s+selected$', trimmed, re.I)
        return f"\u5df2\u9009 {m.group(1)} \u9879"
    m = re.match(r'^(\d+)\s+tasks?$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u4efb\u52a1"
    m = re.match(r'^(\d+)\s+artifacts?$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u4ea7\u7269"
    m = re.match(r'^(\d+)\s+changes?$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u5904\u66f4\u6539"
    m = re.match(r'^(\d+)\s+errors?$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u9519\u8bef"
    m = re.match(r'^(\d+)\s+warnings?$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u8b66\u544a"
    m = re.match(r'^(\d+)\s+results?$', trimmed, re.I)
    if m:
        return f"{m.group(1)} \u4e2a\u7ed3\u679c"

    return None

test_cases = [
    # Timers
    ('Thinking for 1.2s', '思考中 (1.2秒)'),
    ('Thinking for 0.4s', '思考中 (0.4秒)'),
    ('Thinking for 850ms', '思考中 (850毫秒)'),
    ('Thinking for 1 second', '思考中 (1秒)'),
    ('Thinking for 2 seconds', '思考中 (2秒)'),
    ('Thought for 1.2s', '已思考 (1.2秒)'),
    ('Thought for 500ms', '已思考 (500毫秒)'),
    ('Thinking... 1.2s', '思考中... (1.2秒)'),
    ('Thinking (1.5s)', '思考中 (1.5秒)'),
    ('Working for 3.4s', '处理中 (3.4秒)'),
    ('Working for 800ms', '处理中 (800毫秒)'),
    ('Worked for 3.4s', '已处理 (3.4秒)'),
    ('Working... 3.4s', '处理中... (3.4秒)'),
    ('Completed in 12.3s', '已完成 (耗时 12.3秒)'),
    ('Completed in 500ms', '已完成 (耗时 500毫秒)'),
    ('Finished in 1.5s', '已完成 (耗时 1.5秒)'),
    ('Done in 0.8s', '已完成 (耗时 0.8秒)'),
    ('Timed 1.2s', '已计时 1.2秒'),

    # Timestamps
    ('10d', '10天前'),
    ('5m', '5分钟前'),
    ('1mo', '1个月前'),
    ('2mo', '2个月前'),
    ('2h', '2小时前'),
    ('30s', '30秒前'),
    ('1y', '1年前'),
    ('5m ago', '5分钟前'),
    ('10d ago', '10天前'),
    ('1mo ago', '1个月前'),
    ('5 minutes ago', '5分钟前'),
    ('2 days ago', '2天前'),
    ('1 month ago', '1个月前'),
    ('Just now', '刚刚'),
    ('just now', '刚刚'),
    ('Today 14:30', '今天 14:30'),
    ('Today at 14:30', '今天 14:30'),
    ('Yesterday 09:15', '昨天 09:15'),
    ('Yesterday at 09:15', '昨天 09:15'),

    # Counters
    ('Subagents 0', '子智能体 0'),
    ('Subagents 3', '子智能体 3'),
    ('Files Changed 3', '已修改文件 3'),
    ('Artifacts 2', '产物 2'),
    ('Uploads 5', '已上传文件 5'),
    ('Background Tasks 1', '后台任务 1'),
    ('MCP Servers 3', 'MCP 服务 3'),
    ('0 files changed', '0 个文件已修改'),
    ('1 file changed', '1 个文件已修改'),
    ('5 files changed', '5 个文件已修改'),
    ('1 subagent', '1 个子智能体'),
    ('3 subagents', '3 个子智能体'),
    ('No agents running', '0 个智能体运行中'),
    ('1 agent running', '1 个智能体运行中'),
    ('4 agents running', '4 个智能体运行中'),
    ('1 item selected', '已选 1 项'),
    ('5 items selected', '已选 5 项'),
    ('1 task', '1 个任务'),
    ('2 tasks', '2 个任务'),
    ('1 artifact', '1 个产物'),
    ('3 artifacts', '3 个产物'),
    # Edge cases: case-insensitivity, verbose abbreviations, non-breaking space
    ('10D', '10天前'),
    ('5M', '5分钟前'),
    ('1MO', '1个月前'),
    ('2H', '2小时前'),
    ('30S', '30秒前'),
    ('1Y', '1年前'),
    ('5 MINS AGO', '5分钟前'),
    ('2 HRS AGO', '2小时前'),
    ('30 SECS AGO', '30秒前'),
    ('1 YR AGO', '1年前'),
    ('10 mins ago', '10分钟前'),
    ('1 min ago', '1分钟前'),
    ('2 hrs ago', '2小时前'),
    ('1 hr ago', '1小时前'),
    ('30 secs ago', '30秒前'),
    ('1 sec ago', '1秒前'),
    ('1 yr ago', '1年前'),
    ('2 yrs ago', '2年前'),
    ('Thinking for 500MS', '思考中 (500毫秒)'),
    ('Thinking for 1.2 SECONDS', '思考中 (1.2秒)'),
    ('Thinking   for   1.2s', '思考中 (1.2秒)'),
    ('Completed   in   5s', '已完成 (耗时 5秒)')
]

passed = 0
for inp, exp in test_cases:
    act = match_dynamic_patterns(inp)
    if act != exp:
        print(f"FAILED: '{inp}' -> Expected '{exp}', Got '{act}'")
    else:
        passed += 1

print(f"Passed {passed}/{len(test_cases)} tests!")
assert passed == len(test_cases)
