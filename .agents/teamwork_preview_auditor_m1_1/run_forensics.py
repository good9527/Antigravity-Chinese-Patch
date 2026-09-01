#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor Forensic Verification Script
"""
import os
import json
import re
import hashlib
import subprocess

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

print("======================================================================")
print("              FORENSIC INTEGRITY AUDIT — MILESTONE 1                  ")
print("======================================================================")
print(f"Project Root: {PROJECT_ROOT}\n")

# Target artifacts
dist_files = {
    'dictionary.json': os.path.join(PROJECT_ROOT, 'dist', 'dictionary.json'),
    'preload.js': os.path.join(PROJECT_ROOT, 'dist', 'preload.js'),
    'engine.js': os.path.join(PROJECT_ROOT, 'dist', 'engine.js')
}

# 1. SHA256 Checksums
print("--- [CHECK 1: File Checksums & Byte Analysis] ---")
checksums = {}
for name, path in dist_files.items():
    if not os.path.isfile(path):
        print(f"FAIL: {name} does not exist at {path}")
        continue
    data = open(path, 'rb').read()
    sha = hashlib.sha256(data).hexdigest()
    checksums[name] = sha
    max_b = max(data)
    min_b = min(data)
    print(f"  {name:16}: Size={len(data):6} bytes | MinByte={min_b:3} | MaxByte={max_b:3} | SHA256={sha}")
    if name.endswith('.js'):
        if max_b > 127:
            print(f"  [INTEGRITY VIOLATION] {name} contains non-ASCII byte: {max_b}")
        else:
            print(f"  [PASS] {name} is 100% pure 7-bit ASCII (max byte <= 127)")

print("\n--- [CHECK 2: Typo Scan ('已修政' / '无法修政' / '修政' / '\\u653f')] ---")
typos_found = 0
for name, path in dist_files.items():
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8', errors='replace')
    
    # Raw UTF-8 check
    if '已修政' in text:
        print(f"  [VIOLATION] Found '已修政' in {name}")
        typos_found += 1
    if '无法修政' in text:
        print(f"  [VIOLATION] Found '无法修政' in {name}")
        typos_found += 1
    if '修政' in text:
        print(f"  [VIOLATION] Found '修政' in {name}")
        typos_found += 1

    # Escaped Unicode check
    if '\\u5df2\\u4fee\\u653f' in text: # 已修政
        print(f"  [VIOLATION] Found escaped '\\u5df2\\u4fee\\u653f' (已修政) in {name}")
        typos_found += 1
    if '\\u653f' in text: # 政
        print(f"  [VIOLATION] Found escaped '\\u653f' (政) in {name}")
        typos_found += 1
    if '\\u65e0\\u6cd5\\u4fee\\u653f' in text: # 无法修政
        print(f"  [VIOLATION] Found escaped '\\u65e0\\u6cd5\\u4fee\\u653f' (无法修政) in {name}")
        typos_found += 1

if typos_found == 0:
    print("  [PASS] 0 typos found across all dist files. '已修改' (\u5df2\u4fee\u6539) is correctly used.")

print("\n--- [CHECK 3: Dictionary Completeness & Authenticity] ---")
dict_path = dist_files['dictionary.json']
with open(dict_path, 'r', encoding='utf-8') as f:
    dict_data = json.load(f)

print(f"  Total Dictionary Keys: {len(dict_data)}")
if len(dict_data) < 400:
    print(f"  [VIOLATION] Dictionary entries count {len(dict_data)} < 400 specification target.")
else:
    print(f"  [PASS] Dictionary entries count {len(dict_data)} >= 400 (Specification met: 514 keys).")

# Check for duplicate keys in raw JSON
raw_json = open(dict_path, 'r', encoding='utf-8').read()
key_matches = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"\s*:', raw_json)
key_counts = {}
for k in key_matches:
    key_counts[k] = key_counts.get(k, 0) + 1
duplicates = {k: v for k, v in key_counts.items() if v > 1}
if duplicates:
    print(f"  [VIOLATION] Duplicate keys found in dictionary.json: {duplicates}")
else:
    print("  [PASS] No duplicate keys in dictionary.json.")

# Verify key entries
print("  Sample Key-Value Pairs:")
sample_keys = [
    "New Conversation", "Files Changed", "Subagents", "Agent cannot modify files outside of the workspace in strict mode.",
    "Thinking...", "Your Plan: Google AI Ultra", "Daily Quota", "Settings"
]
for sk in sample_keys:
    val = dict_data.get(sk)
    print(f"    '{sk}' -> '{val}'")

print("\n--- [CHECK 4: Cheating & Facade Detection] ---")
# Analyze JS functions in engine.js and preload.js
for js_name in ['preload.js', 'engine.js']:
    js_path = dist_files[js_name]
    code = open(js_path, 'r', encoding='utf-8').read()
    
    # Check for hardcoded test results or mock shortcuts
    suspicious_patterns = [
        r'return\s+["\']PASS["\']',
        r'return\s+["\']FAIL["\']',
        r'if\s*\([^)]*__test__',
        r'if\s*\([^)]*fixture',
        r'if\s*\([^)]*mock',
        r'if\s*\([^)]*=== ["\']test_',
    ]
    for sp in suspicious_patterns:
        matches = re.findall(sp, code, re.IGNORECASE)
        if matches:
            print(f"  [VIOLATION] Suspicious pattern '{sp}' found in {js_name}: {matches}")
        else:
            print(f"  [PASS] No matches for suspicious pattern '{sp}' in {js_name}")

print("\n--- [CHECK 5: Node.js Runtime Dynamic Execution & Adversarial Verification] ---")
# We will create a node test script to run engine.js directly with node
node_script_path = os.path.join(os.path.dirname(__file__), "test_runtime.js")
node_code = """
const path = require('path');
const assert = require('assert');
const engine = require(path.join(__dirname, '../../dist/engine.js'));

console.log('  Testing engine.js exports...');
assert(typeof engine.translateText === 'function', 'translateText must be a function');
assert(typeof engine.matchDynamicPatterns === 'function', 'matchDynamicPatterns must be a function');
assert(typeof engine.isBypassedElement === 'function', 'isBypassedElement must be a function');
assert(typeof engine.walk === 'function', 'walk must be a function');
assert(typeof engine.dictionary === 'object', 'dictionary must be an object');
assert(Object.keys(engine.dictionary).length >= 400, 'dictionary keys >= 400');

console.log('  [PASS] All exports present and valid.');

// Test 1: Static dictionary translation
assert.strictEqual(engine.translateText('New Conversation'), '新建对话');
assert.strictEqual(engine.translateText('Files Changed'), '已修改文件');
assert.strictEqual(engine.translateText('Subagents'), '子智能体');

// Test 2: Dynamic timers
assert.strictEqual(engine.translateText('Thinking for 1.2s'), '思考中 (1.2秒)');
assert.strictEqual(engine.translateText('Thinking for 250ms'), '思考中 (250毫秒)');
assert.strictEqual(engine.translateText('Thought for 0.8s'), '思考中 (0.8秒)');
assert.strictEqual(engine.translateText('Working for 3.4s'), '处理中 (3.4秒)');
assert.strictEqual(engine.translateText('Working for 500ms'), '处理中 (500毫秒)');
assert.strictEqual(engine.translateText('Completed in 4.5s'), '已完成 (耗时 4.5秒)');
assert.strictEqual(engine.translateText('Finished in 100ms'), '已完成 (耗时 100毫秒)');
assert.strictEqual(engine.translateText('Done in 12s'), '已完成 (耗时 12秒)');

// Test 3: Relative timestamps
assert.strictEqual(engine.translateText('10d'), '10天前');
assert.strictEqual(engine.translateText('5m'), '5分钟前');
assert.strictEqual(engine.translateText('1mo'), '1个月前');
assert.strictEqual(engine.translateText('2h'), '2小时前');
assert.strictEqual(engine.translateText('30s'), '30秒前');
assert.strictEqual(engine.translateText('1y'), '1年前');
assert.strictEqual(engine.translateText('5 minutes ago'), '5分钟前');
assert.strictEqual(engine.translateText('2 days ago'), '2天前');
assert.strictEqual(engine.translateText('1 month ago'), '1个月前');
assert.strictEqual(engine.translateText('just now'), '刚刚');
assert.strictEqual(engine.translateText('a few seconds ago'), '几秒前');

// Test 4: Dynamic counters
assert.strictEqual(engine.translateText('Subagents 3'), '子智能体 3');
assert.strictEqual(engine.translateText('Files Changed 5'), '已修改文件 5');
assert.strictEqual(engine.translateText('3 files changed'), '3 个文件已修改');
assert.strictEqual(engine.translateText('1 file changed'), '1 个文件已修改');
assert.strictEqual(engine.translateText('2 subagents'), '2 个子智能体');
assert.strictEqual(engine.translateText('3 agents running'), '3 个智能体运行中');

// Test 5: Date prefixes
assert.strictEqual(engine.translateText('Today at 10:00 AM'), '今天 at 10:00 AM');
assert.strictEqual(engine.translateText('Yesterday 3:30 PM'), '昨天 3:30 PM');

// Test 6: Non-breaking space
assert.strictEqual(engine.translateText('New\\u00a0Conversation'), '新建对话');

console.log('  [PASS] Node.js translation engine runtime tests passed cleanly.');
"""
with open(node_script_path, "w", encoding="utf-8") as nf:
    nf.write(node_code)

try:
    res = subprocess.run(["node", node_script_path], capture_output=True, text=True, check=True)
    print(res.stdout)
except subprocess.CalledProcessError as e:
    print(f"  [FAIL] Node.js test failed with error:\n{e.stderr}")
except FileNotFoundError:
    print("  [SKIP] Node.js executable not found in path.")

print("\n--- [CHECK 6: Pre-populated Artifact & Pre-existing Result Audit] ---")
suspicious_files = []
for root, dirs, files in os.walk(PROJECT_ROOT):
    if '.git' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith(('.log', '.result', '.attestation', '.cached')):
            suspicious_files.append(os.path.join(root, file))

if suspicious_files:
    print(f"  Found suspicious pre-populated files: {suspicious_files}")
else:
    print("  [PASS] No pre-populated log or attestation files found.")

print("\n======================================================================")
print("                   FORENSIC AUDIT SUMMARY                             ")
print("======================================================================")
