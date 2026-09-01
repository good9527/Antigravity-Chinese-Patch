#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adversarial Stress Test Suite for Localization Logic
"""
import re
import json

# Extract regexes and logic directly matching preload.js
UNIT_MAP_CN = {
    'mo': '个月前', 'month': '个月前', 'months': '个月前',
    'd': '天前', 'day': '天前', 'days': '天前',
    'm': '分钟前', 'min': '分钟前', 'mins': '分钟前', 'minute': '分钟前', 'minutes': '分钟前',
    'h': '小时前', 'hr': '小时前', 'hrs': '小时前', 'hour': '小时前', 'hours': '小时前',
    's': '秒前', 'sec': '秒前', 'secs': '秒前', 'second': '秒前', 'seconds': '秒前',
    'y': '年前', 'yr': '年前', 'yrs': '年前', 'year': '年前', 'years': '年前'
}

with open('dist/dictionary.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

substringReplacements = [
    ('Minimize', '最小化'),
    ('Maximize', '最大化'),
    ('Toggle Developer Tools', '切换开发者工具'),
    ('Default', '默认'),
    ('Full Machine', '整机授权'),
    ('Turbo Mode', '极速模式'),
    ('Turbo mode', '极速模式'),
    ('Custom', '自定义'),
    ('System', '跟随系统')
]

def formatTimerUnit(unit):
    if not unit: return '秒'
    return '毫秒' if unit.lower().startswith('ms') else '秒'

def matchDynamicPatterns(trimmed):
    m = re.match(r'^(?:Thinking|Thought)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.IGNORECASE)
    if m:
        return f"思考中 ({m.group(1)}{formatTimerUnit(m.group(2))})"
    
    m = re.match(r'^Thinking\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$', trimmed, re.IGNORECASE)
    if m:
        return f"思考中... ({m.group(1)}{formatTimerUnit(m.group(2))})"

    m = re.match(r'^(?:Thinking|Thought)\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$', trimmed, re.IGNORECASE)
    if not m:
        m = re.match(r'^(?:Thinking|Thought)\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$', trimmed, re.IGNORECASE)
    if m:
        return f"思考中 ({m.group(1)}{formatTimerUnit(m.group(2))})"

    m = re.match(r'^(?:Working|Worked)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.IGNORECASE)
    if m:
        return f"处理中 ({m.group(1)}{formatTimerUnit(m.group(2))})"

    m = re.match(r'^Working\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$', trimmed, re.IGNORECASE)
    if m:
        return f"处理中... ({m.group(1)}{formatTimerUnit(m.group(2))})"

    m = re.match(r'^(?:Working|Worked)\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$', trimmed, re.IGNORECASE)
    if not m:
        m = re.match(r'^(?:Working|Worked)\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$', trimmed, re.IGNORECASE)
    if m:
        return f"处理中 ({m.group(1)}{formatTimerUnit(m.group(2))})"

    m = re.match(r'^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.IGNORECASE)
    if m:
        return f"已完成 (耗时 {m.group(2)}{formatTimerUnit(m.group(3))})"

    m = re.match(r'^Timed\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.IGNORECASE)
    if m:
        return f"已计时 {m.group(1)}{formatTimerUnit(m.group(2))}"

    m = re.match(r'^Elapsed\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.IGNORECASE)
    if m:
        return f"耗时: {m.group(1)}{formatTimerUnit(m.group(2))}"

    m = re.match(r'^Total\s+duration:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.IGNORECASE)
    if m:
        return f"总耗时: {m.group(1)}{formatTimerUnit(m.group(2))}"

    m = re.match(r'^Execution\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$', trimmed, re.IGNORECASE)
    if m:
        return f"执行耗时: {m.group(1)}{formatTimerUnit(m.group(2))}"

    if re.match(r'^just\s+now$', trimmed, re.IGNORECASE):
        return '刚刚'
    if re.match(r'^a\s+few\s+seconds\s+ago$', trimmed, re.IGNORECASE):
        return '几秒前'
    if re.match(r'^a\s+minute\s+ago$', trimmed, re.IGNORECASE):
        return '1分钟前'
    if re.match(r'^an\s+hour\s+ago$', trimmed, re.IGNORECASE):
        return '1小时前'
    if re.match(r'^a\s+day\s+ago$', trimmed, re.IGNORECASE):
        return '1天前'
    if re.match(r'^today$', trimmed, re.IGNORECASE):
        return '今天'
    if re.match(r'^yesterday$', trimmed, re.IGNORECASE):
        return '昨天'

    if trimmed.startswith('Today '):
        return trimmed.replace('Today ', '今天 ', 1)
    if trimmed.startswith('Yesterday '):
        return trimmed.replace('Yesterday ', '昨天 ', 1)

    m = re.match(r'^(\d+)\s*(mo|[dmhsy])(?:\s+ago)?$', trimmed, re.IGNORECASE)
    if m:
        u = m.group(2).lower()
        if u in UNIT_MAP_CN:
            return f"{m.group(1)}{UNIT_MAP_CN[u]}"

    m = re.match(r'^(\d+)\s*(months?|days?|hours?|hrs?|minutes?|mins?|seconds?|secs?|years?|yrs?)\s+ago$', trimmed, re.IGNORECASE)
    if m:
        u = m.group(2).lower()
        if u in UNIT_MAP_CN:
            return f"{m.group(1)}{UNIT_MAP_CN[u]}"

    m = re.match(r'^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks|MCP Servers)\s+(\d+)$', trimmed, re.IGNORECASE)
    if m:
        type_map = {
            'subagents': '子智能体',
            'files changed': '已修改文件',
            'artifacts': '产物',
            'uploads': '已上传文件',
            'background tasks': '后台任务',
            'mcp servers': 'MCP 服务'
        }
        lbl = type_map.get(m.group(1).lower(), m.group(1))
        return f"{lbl} {m.group(2)}"

    m = re.match(r'^(\d+)\s+files?\s+changed$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个文件已修改"
    m = re.match(r'^(\d+)\s+files?\s+modified$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个文件已修改"
    m = re.match(r'^(\d+)\s+files?\s+added$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个文件已添加"
    m = re.match(r'^(\d+)\s+files?\s+deleted$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个文件已删除"
    m = re.match(r'^(\d+)\s+files?$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个文件"

    m = re.match(r'^(\d+)\s+subagents?$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个子智能体"
    m = re.match(r'^(\d+)\s+agents?\s+running$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个智能体运行中"
    if re.match(r'^No\s+agents?\s+running$', trimmed, re.IGNORECASE):
        return '0 个智能体运行中'
    if re.match(r'^1\s+agent\s+running$', trimmed, re.IGNORECASE):
        return '1 个智能体运行中'
    m = re.match(r'^(\d+)\s+items?\s+selected$', trimmed, re.IGNORECASE)
    if m: return f"已选 {m.group(1)} 项"
    m = re.match(r'^(\d+)\s+selected$', trimmed, re.IGNORECASE)
    if m: return f"已选 {m.group(1)} 项"
    m = re.match(r'^(\d+)\s+tasks?$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个任务"
    m = re.match(r'^(\d+)\s+artifacts?$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个产物"
    m = re.match(r'^(\d+)\s+changes?$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 处更改"
    m = re.match(r'^(\d+)\s+errors?$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个错误"
    m = re.match(r'^(\d+)\s+warnings?$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个警告"
    m = re.match(r'^(\d+)\s+results?$', trimmed, re.IGNORECASE)
    if m: return f"{m.group(1)} 个结果"

    return None

def normalize(s):
    if not s: return ''
    return s.replace('\u00a0', ' ')

def translate(text):
    if not text or not isinstance(text, str): return None
    norm = normalize(text)
    trimmed = norm.strip()
    if not trimmed: return None
    if trimmed in dictionary:
        return norm.replace(trimmed, dictionary[trimmed])
    if norm in dictionary:
        return dictionary[norm]
    dyn = matchDynamicPatterns(trimmed)
    if dyn is not None:
        return norm.replace(trimmed, dyn)
    new_text = norm
    modified = False
    for s_str, r_str in substringReplacements:
        if s_str in new_text:
            new_text = new_text.replace(s_str, r_str)
            modified = True
    if modified: return new_text
    return None

# Adversarial Test Cases
test_cases = [
    # 1. Edge case floats
    ("Thinking for 0.001s", "思考中 (0.001秒)"),
    ("Thinking for 100.25ms", "思考中 (100.25毫秒)"),
    ("Thought for 0s", "思考中 (0秒)"),
    ("Working for 999.999s", "处理中 (999.999秒)"),
    ("Completed in 0.05ms", "已完成 (耗时 0.05毫秒)"),
    ("Finished in 1.00s", "已完成 (耗时 1.00秒)"),
    
    # 2. Capitalization variations
    ("thinking for 5s", "思考中 (5秒)"),
    ("THINKING FOR 5S", "思考中 (5秒)"),
    ("working for 2ms", "处理中 (2毫秒)"),
    ("COMPLETED IN 10S", "已完成 (耗时 10秒)"),
    ("10D", "10天前"),
    ("5 MINUTES AGO", "5分钟前"),
    ("SUBAGENTS 0", "子智能体 0"),
    ("FILES CHANGED 12", "已修改文件 12"),
    
    # 3. Non-breaking space inputs
    ("Thinking\u00a0for\u00a02.5s", "思考中 (2.5秒)"),
    ("New\u00a0Conversation", "新建对话"),
    ("Files\u00a0Changed\u00a03", "已修改文件 3"),
    
    # 4. Singular vs Plural
    ("1 file changed", "1 个文件已修改"),
    ("2 files changed", "2 个文件已修改"),
    ("1 subagent", "1 个子智能体"),
    ("5 subagents", "5 个子智能体"),
    ("1 item selected", "已选 1 项"),
    ("10 items selected", "已选 10 项"),
    ("1 agent running", "1 个智能体正在运行"),
    ("0 agents running", "0 个智能体运行中"),
    ("No agents running", "暂无运行中的智能体"),
    
    # 5. Untranslated / Safe passthrough (should return None or unchanged)
    ("const x = 42;", None),
    ("function foo() { return true; }", None),
    ("import React from 'react';", None),
    ("console.log('hello')", None),
    ("", None),
    ("   ", None),
]

passed = 0
failed = 0
for inp, exp in test_cases:
    res = translate(inp)
    if res == exp:
        passed += 1
    else:
        failed += 1
        print(f"[FAIL] Input: '{inp}' -> Got: '{res}' | Expected: '{exp}'")

print(f"\nAdversarial Stress Test: Total={len(test_cases)}, Passed={passed}, Failed={failed}")
assert failed == 0, f"{failed} adversarial test cases failed!"
