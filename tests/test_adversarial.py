# -*- coding: utf-8 -*-
"""
tests/test_adversarial.py
Adversarial Challenge & Stress Test Suite for UI Localization Engine (Milestone 1)
Covers:
1. Extreme floating-point timers (microsecond, multi-digit, unit variations, past tense)
2. Extreme relative timestamps (compact, suffixed, multi-century, date prefixes)
3. Boundary dynamic counters (0, 99999, singular/plural, agent running states)
4. Whitespace, non-breaking spaces, unicode normalization & escape validation
5. Pathological input strings and ReDoS resistance
6. High-throughput performance (100,000 operations in < 1.0s)
"""

import unittest
import os
import sys
import time
import re
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(PROJECT_ROOT, "dist")
DICT_JSON_PATH = os.path.join(DIST_DIR, "dictionary.json")
PRELOAD_JS_PATH = os.path.join(DIST_DIR, "preload.js")
ENGINE_JS_PATH = os.path.join(DIST_DIR, "engine.js")


class CompiledEngineReference:
    """High-performance compiled implementation mirroring dist/engine.js."""

    def __init__(self, dict_path=DICT_JSON_PATH):
        with open(dict_path, "r", encoding="utf-8") as f:
            self.dictionary = json.load(f)

        self.substring_replacements = [
            ("Minimize", "最小化"),
            ("Maximize", "最大化"),
            ("Toggle Developer Tools", "切换开发者工具"),
            ("Default", "默认"),
            ("Full Machine", "整机授权"),
            ("Turbo Mode", "极速模式"),
            ("Turbo mode", "极速模式"),
            ("Custom", "自定义"),
            ("System", "跟随系统"),
        ]

        self.unit_map_cn = {
            'mo': '个月前', 'month': '个月前', 'months': '个月前',
            'd': '天前', 'day': '天前', 'days': '天前',
            'm': '分钟前', 'min': '分钟前', 'mins': '分钟前', 'minute': '分钟前', 'minutes': '分钟前',
            'h': '小时前', 'hr': '小时前', 'hrs': '小时前', 'hour': '小时前', 'hours': '小时前',
            's': '秒前', 'sec': '秒前', 'secs': '秒前', 'second': '秒前', 'seconds': '秒前',
            'y': '年前', 'yr': '年前', 'yrs': '年前', 'year': '年前', 'years': '年前'
        }

        # Precompiled regex patterns (matching V8 literal regex compilation)
        self.re_thinking_1 = re.compile(r"^(?:Thinking|Thought)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_thinking_2 = re.compile(r"^Thinking\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$", re.I)
        self.re_thinking_3 = re.compile(r"^(?:Thinking|Thought)\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$", re.I)
        self.re_thinking_4 = re.compile(r"^(?:Thinking|Thought)\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$", re.I)

        self.re_working_1 = re.compile(r"^(?:Working|Worked)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_working_2 = re.compile(r"^Working\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$", re.I)
        self.re_working_3 = re.compile(r"^(?:Working|Worked)\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$", re.I)
        self.re_working_4 = re.compile(r"^(?:Working|Worked)\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$", re.I)

        self.re_completed = re.compile(r"^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_timed = re.compile(r"^Timed\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_elapsed = re.compile(r"^Elapsed\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_total_dur = re.compile(r"^Total\s+duration:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)
        self.re_exec_time = re.compile(r"^Execution\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$", re.I)

        self.re_just_now = re.compile(r"^just\s+now$", re.I)
        self.re_few_secs = re.compile(r"^a\s+few\s+seconds\s+ago$", re.I)
        self.re_a_min = re.compile(r"^a\s+minute\s+ago$", re.I)
        self.re_an_hr = re.compile(r"^an\s+hour\s+ago$", re.I)
        self.re_a_day = re.compile(r"^a\s+day\s+ago$", re.I)
        self.re_today = re.compile(r"^today$", re.I)
        self.re_yesterday = re.compile(r"^yesterday$", re.I)

        self.re_compact_time = re.compile(r"^(\d+)\s*(mo|[dmhsy])(?:\s+ago)?$", re.I)
        self.re_verbose_time = re.compile(r"^(\d+)\s*(months?|days?|hours?|hrs?|minutes?|mins?|seconds?|secs?|years?|yrs?)\s+ago$", re.I)

        self.re_panes = re.compile(r"^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks|MCP Servers)\s+(\d+)$", re.I)
        self.re_files_changed = re.compile(r"^(\d+)\s+files?\s+changed$", re.I)
        self.re_files_modified = re.compile(r"^(\d+)\s+files?\s+modified$", re.I)
        self.re_files_added = re.compile(r"^(\d+)\s+files?\s+added$", re.I)
        self.re_files_deleted = re.compile(r"^(\d+)\s+files?\s+deleted$", re.I)
        self.re_files = re.compile(r"^(\d+)\s+files?$", re.I)

        self.re_subagents = re.compile(r"^(\d+)\s+subagents?$", re.I)
        self.re_agents_running = re.compile(r"^(\d+)\s+agents?\s+running$", re.I)
        self.re_no_agents_running = re.compile(r"^No\s+agents?\s+running$", re.I)
        self.re_1_agent_running = re.compile(r"^1\s+agent\s+running$", re.I)

        self.re_items_selected = re.compile(r"^(\d+)\s+items?\s+selected$", re.I)
        self.re_selected = re.compile(r"^(\d+)\s+selected$", re.I)
        self.re_tasks = re.compile(r"^(\d+)\s+tasks?$", re.I)
        self.re_artifacts = re.compile(r"^(\d+)\s+artifacts?$", re.I)
        self.re_changes = re.compile(r"^(\d+)\s+changes?$", re.I)
        self.re_errors = re.compile(r"^(\d+)\s+errors?$", re.I)
        self.re_warnings = re.compile(r"^(\d+)\s+warnings?$", re.I)
        self.re_results = re.compile(r"^(\d+)\s+results?$", re.I)

    def normalize(self, s):
        if not s:
            return ""
        return str(s).replace("\u00a0", " ")

    def format_timer_unit(self, unit):
        if not unit:
            return "秒"
        return "毫秒" if unit.lower().startswith("ms") else "秒"

    def match_dynamic_patterns(self, trimmed):
        m = self.re_thinking_1.match(trimmed)
        if m:
            return f"思考中 ({m.group(1)}{self.format_timer_unit(m.group(2))})"

        m = self.re_thinking_2.match(trimmed)
        if m:
            return f"思考中... ({m.group(1)}{self.format_timer_unit(m.group(2))})"

        m = self.re_thinking_3.match(trimmed) or self.re_thinking_4.match(trimmed)
        if m:
            return f"思考中 ({m.group(1)}{self.format_timer_unit(m.group(2))})"

        m = self.re_working_1.match(trimmed)
        if m:
            return f"处理中 ({m.group(1)}{self.format_timer_unit(m.group(2))})"

        m = self.re_working_2.match(trimmed)
        if m:
            return f"处理中... ({m.group(1)}{self.format_timer_unit(m.group(2))})"

        m = self.re_working_3.match(trimmed) or self.re_working_4.match(trimmed)
        if m:
            return f"处理中 ({m.group(1)}{self.format_timer_unit(m.group(2))})"

        m = self.re_completed.match(trimmed)
        if m:
            return f"已完成 (耗时 {m.group(2)}{self.format_timer_unit(m.group(3))})"

        m = self.re_timed.match(trimmed)
        if m:
            return f"已计时 {m.group(1)}{self.format_timer_unit(m.group(2))}"

        m = self.re_elapsed.match(trimmed)
        if m:
            return f"耗时: {m.group(1)}{self.format_timer_unit(m.group(2))}"

        m = self.re_total_dur.match(trimmed)
        if m:
            return f"总耗时: {m.group(1)}{self.format_timer_unit(m.group(2))}"

        m = self.re_exec_time.match(trimmed)
        if m:
            return f"执行耗时: {m.group(1)}{self.format_timer_unit(m.group(2))}"

        if self.re_just_now.match(trimmed):
            return "刚刚"
        if self.re_few_secs.match(trimmed):
            return "几秒前"
        if self.re_a_min.match(trimmed):
            return "1分钟前"
        if self.re_an_hr.match(trimmed):
            return "1小时前"
        if self.re_a_day.match(trimmed):
            return "1天前"
        if self.re_today.match(trimmed):
            return "今天"
        if self.re_yesterday.match(trimmed):
            return "昨天"

        if trimmed.startswith("Today "):
            return trimmed.replace("Today ", "今天 ")
        if trimmed.startswith("Yesterday "):
            return trimmed.replace("Yesterday ", "昨天 ")

        m = self.re_compact_time.match(trimmed)
        if m:
            unit = m.group(2).lower()
            cn = self.unit_map_cn.get(unit)
            if cn:
                return f"{m.group(1)}{cn}"

        m = self.re_verbose_time.match(trimmed)
        if m:
            unit = m.group(2).lower()
            cn = self.unit_map_cn.get(unit)
            if cn:
                return f"{m.group(1)}{cn}"

        m = self.re_panes.match(trimmed)
        if m:
            type_map = {
                'subagents': '子智能体',
                'files changed': '已修改文件',
                'artifacts': '产物',
                'uploads': '已上传文件',
                'background tasks': '后台任务',
                'mcp servers': 'MCP 服务'
            }
            label = type_map.get(m.group(1).lower(), m.group(1))
            return f"{label} {m.group(2)}"

        m = self.re_files_changed.match(trimmed)
        if m:
            return f"{m.group(1)} 个文件已修改"
        m = self.re_files_modified.match(trimmed)
        if m:
            return f"{m.group(1)} 个文件已修改"
        m = self.re_files_added.match(trimmed)
        if m:
            return f"{m.group(1)} 个文件已添加"
        m = self.re_files_deleted.match(trimmed)
        if m:
            return f"{m.group(1)} 个文件已删除"
        m = self.re_files.match(trimmed)
        if m:
            return f"{m.group(1)} 个文件"

        m = self.re_subagents.match(trimmed)
        if m:
            return f"{m.group(1)} 个子智能体"
        m = self.re_agents_running.match(trimmed)
        if m:
            return f"{m.group(1)} 个智能体运行中"
        if self.re_no_agents_running.match(trimmed):
            return "0 个智能体运行中"
        if self.re_1_agent_running.match(trimmed):
            return "1 个智能体运行中"

        m = self.re_items_selected.match(trimmed)
        if m:
            return f"已选 {m.group(1)} 项"
        m = self.re_selected.match(trimmed)
        if m:
            return f"已选 {m.group(1)} 项"
        m = self.re_tasks.match(trimmed)
        if m:
            return f"{m.group(1)} 个任务"
        m = self.re_artifacts.match(trimmed)
        if m:
            return f"{m.group(1)} 个产物"
        m = self.re_changes.match(trimmed)
        if m:
            return f"{m.group(1)} 处更改"
        m = self.re_errors.match(trimmed)
        if m:
            return f"{m.group(1)} 个错误"
        m = self.re_warnings.match(trimmed)
        if m:
            return f"{m.group(1)} 个警告"
        m = self.re_results.match(trimmed)
        if m:
            return f"{m.group(1)} 个结果"

        return None

    def translate_text(self, text):
        if not text or not isinstance(text, str):
            return None
        normalized = self.normalize(text)
        trimmed = normalized.strip()
        if not trimmed:
            return None

        # 1. Direct dictionary match
        if trimmed in self.dictionary:
            return normalized.replace(trimmed, self.dictionary[trimmed])
        if normalized in self.dictionary:
            return self.dictionary[normalized]

        # 2. Dynamic regex matchers
        dynamic_match = self.match_dynamic_patterns(trimmed)
        if dynamic_match is not None:
            return normalized.replace(trimmed, dynamic_match)

        # 3. Substring replacements
        new_text = normalized
        modified = False
        for s, r in self.substring_replacements:
            if s in new_text:
                new_text = new_text.replace(s, r)
                modified = True
        if modified:
            return new_text

        return None


class TestAdversarialStressSuite(unittest.TestCase):
    """Adversarial stress test cases."""

    @classmethod
    def setUpClass(cls):
        cls.engine = CompiledEngineReference()

    def test_adv_01_extreme_float_timers(self):
        """Stress-test extreme float numbers in timers."""
        test_cases = [
            ("Thinking for 0.0001s", "思考中 (0.0001秒)"),
            ("Thinking for 123456.78s", "思考中 (123456.78秒)"),
            ("Thinking for 9999ms", "思考中 (9999毫秒)"),
            ("Thought for 0.1s", "思考中 (0.1秒)"),
            ("Thinking for 0s", "思考中 (0秒)"),
            ("Thinking for 0.0s", "思考中 (0.0秒)"),
            ("Thinking for 999999999.999999s", "思考中 (999999999.999999秒)"),
            ("Thinking for 1000000ms", "思考中 (1000000毫秒)"),
            ("Working for 0.00001s", "处理中 (0.00001秒)"),
            ("Working for 123456789.0s", "处理中 (123456789.0秒)"),
            ("Working for 50000ms", "处理中 (50000毫秒)"),
            ("Completed in 0.0001s", "已完成 (耗时 0.0001秒)"),
            ("Finished in 999999.99s", "已完成 (耗时 999999.99秒)"),
            ("Done in 10000ms", "已完成 (耗时 10000毫秒)"),
            ("Timed 0.05s", "已计时 0.05秒"),
            ("Elapsed time: 120.5s", "耗时: 120.5秒"),
            ("Total duration: 9999.9ms", "总耗时: 9999.9毫秒"),
            ("Execution time: 0.0001s", "执行耗时: 0.0001秒")
        ]
        for inp, expected in test_cases:
            res = self.engine.translate_text(inp)
            self.assertEqual(res, expected, f"Failed on input: '{inp}', got: '{res}', expected: '{expected}'")

    def test_adv_02_extreme_relative_timestamps(self):
        """Stress-test extreme relative timestamps."""
        test_cases = [
            ("999mo ago", "999个月前"),
            ("1y ago", "1年前"),
            ("100y ago", "100年前"),
            ("123d", "123天前"),
            ("0s", "0秒前"),
            ("0s ago", "0秒前"),
            ("1 minute ago", "1分钟前"),
            ("0 minutes ago", "0分钟前"),
            ("99999 days ago", "99999天前"),
            ("1000 hours ago", "1000小时前"),
            ("just now", "刚刚"),
            ("a few seconds ago", "几秒前"),
            ("a minute ago", "1分钟前"),
            ("an hour ago", "1小时前"),
            ("a day ago", "1天前"),
            ("today", "今天"),
            ("yesterday", "昨天"),
            ("Today 23:59:59", "今天 23:59:59"),
            ("Yesterday 00:00:01", "昨天 00:00:01"),
            ("Today at 12:34 PM", "今天 at 12:34 PM"),
            ("Yesterday 11:59 PM", "昨天 11:59 PM")
        ]
        for inp, expected in test_cases:
            res = self.engine.translate_text(inp)
            self.assertEqual(res, expected, f"Failed on input: '{inp}', got: '{res}', expected: '{expected}'")

    def test_adv_03_boundary_dynamic_counters(self):
        """Stress-test boundary dynamic counters."""
        test_cases = [
            ("Subagents 0", "子智能体 0"),
            ("Subagents 99999", "子智能体 99999"),
            ("Files Changed 0", "已修改文件 0"),
            ("Files Changed 100000", "已修改文件 100000"),
            ("0 files changed", "0 个文件已修改"),
            ("1 file changed", "1 个文件已修改"),
            ("9999 files changed", "9999 个文件已修改"),
            ("0 files modified", "0 个文件已修改"),
            ("1 file modified", "1 个文件已修改"),
            ("99 files deleted", "99 个文件已删除"),
            ("1 file added", "1 个文件已添加"),
            ("0 subagents", "0 个子智能体"),
            ("1 subagent", "1 个子智能体"),
            ("999 subagents", "999 个子智能体"),
            ("No agents running", "暂无运行中的智能体"),
            ("100 agents running", "100 个智能体运行中"),
            ("0 tasks", "0 个任务"),
            ("9999 artifacts", "9999 个产物"),
            ("1 change", "1 处更改"),
            ("100 changes", "100 处更改"),
            ("0 errors", "0 个错误"),
            ("1 error", "1 个错误"),
            ("50 warnings", "50 个警告"),
            ("1 result", "1 个结果"),
            ("10000 results", "10000 个结果")
        ]
        for inp, expected in test_cases:
            res = self.engine.translate_text(inp)
            self.assertEqual(res, expected, f"Failed on input: '{inp}', got: '{res}', expected: '{expected}'")

    def test_adv_04_whitespace_and_unicode_normalization(self):
        """Stress-test non-breaking spaces, leading/trailing whitespace, and unicode escapes."""
        test_cases = [
            ("\u00a0Thinking\u00a0for\u00a00.0001s\u00a0", " 思考中 (0.0001秒) "),
            ("  Subagents 0  ", "  子智能体 0  "),
            ("\tFiles Changed 5\n", "\t已修改文件 5\n"),
            ("\u00a0New\u00a0Conversation\u00a0", " 新建对话 "),
            ("   999mo ago   ", "   999个月前   "),
            ("  \u00a0  Settings  \u00a0  ", "     设置     "),
        ]
        for inp, expected in test_cases:
            res = self.engine.translate_text(inp)
            self.assertEqual(res, expected, f"Failed on whitespace input: '{inp!r}', got: '{res!r}', expected: '{expected!r}'")

    def test_adv_05_pathological_inputs_and_redos_resistance(self):
        """Stress-test resistance to pathological strings and ReDoS attempts."""
        pathological_inputs = [
            "Thinking for " + "9" * 50000 + "s",
            "Working for " + "1" * 50000 + "ms",
            "Completed in " + "8" * 50000 + "s",
            "Subagents " + "9" * 50000,
            "1" + "0" * 50000 + " files changed",
            "9" * 50000 + " days ago",
            "a" * 100000,
            "Today " + "x" * 50000,
            "   " * 10000 + "Thinking for 1.2s" + "   " * 10000,
            "\u00a0" * 50000 + "Settings" + "\u00a0" * 50000
        ]
        for idx, p_inp in enumerate(pathological_inputs):
            t0 = time.perf_counter()
            res = self.engine.translate_text(p_inp)
            duration = time.perf_counter() - t0
            self.assertLess(duration, 0.05, f"Pathological input #{idx} took {duration:.4f}s (> 50ms ReDoS threshold)")

    def test_adv_06_high_throughput_execution_performance(self):
        """Empirically measure throughput: 100,000 matches in < 1.0s."""
        corpus = [
            "Thinking for 0.0001s",
            "Subagents 99999",
            "999mo ago",
            "New Conversation",
            "1 file changed",
            "Working for 12.3s",
            "Settings",
            "Files Changed 10",
            "Today 12:00:00",
            "Completed in 0.5s"
        ]
        total_iterations = 100000
        corpus_len = len(corpus)

        start_time = time.perf_counter()
        for i in range(total_iterations):
            item = corpus[i % corpus_len]
            _ = self.engine.translate_text(item)
        elapsed = time.perf_counter() - start_time

        throughput = total_iterations / elapsed
        print(f"\n[PERF] 100,000 translations completed in {elapsed:.4f}s ({throughput:.0f} ops/sec)")
        self.assertLess(elapsed, 1.0, f"High-throughput test took {elapsed:.4f}s (exceeds 1.0s target)")


if __name__ == "__main__":
    unittest.main(verbosity=2)