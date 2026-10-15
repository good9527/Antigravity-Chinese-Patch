#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Script to synchronize translations across:
- dist/dictionary.json (UTF-8)
- dist/preload.js (Pure 7-bit ASCII \uXXXX)
- dist/engine.js (Pure 7-bit ASCII \uXXXX)
"""

import json
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_PATH = os.path.join(ROOT, "dist", "dictionary.json")
PRELOAD_PATH = os.path.join(ROOT, "dist", "preload.js")
ENGINE_PATH = os.path.join(ROOT, "dist", "engine.js")

with open(DICT_PATH, "r", encoding="utf-8") as f:
    dictionary = json.load(f)

new_entries = {
    # Slash Commands (with and without trailing period)
    "Ask a quick question without interrupting the main conversation.": "快速提问一个简短问题，无需中断主对话。",
    "Ask a quick question without interrupting the main conversation": "快速提问一个简短问题，无需中断主对话",
    "Run until the specified goal is completely finished.": "持续自主运行，直至指定的长任务目标彻底完成。",
    "Run until the specified goal is completely finished": "持续自主运行，直至指定的长任务目标彻底完成",
    "Compact the conversation now (summarize history to free up the context window).": "立即压缩上下文（总结对话历史以释放上下文窗口）。",
    "Compact the conversation now (summarize history to free up the context window)": "立即压缩上下文（总结对话历史以释放上下文窗口）",
    "Run an instruction on a recurring schedule or as a one-time timer.": "按定时周期（Cron）或单次计时器执行指定指令。",
    "Run an instruction on a recurring schedule or as a one-time timer": "按定时周期（Cron）或单次计时器执行指定指令",
    "Invoke a browser agent for web tasks.": "唤起网页浏览器智能体，自主执行网络交互与爬取任务。",
    "Invoke a browser agent for web tasks": "唤起网页浏览器智能体，自主执行网络交互与爬取任务",
    "Plan carefully before executing a task.": "在执行复杂任务前，进行严密细致的分步规划。",
    "Plan carefully before executing a task": "在执行复杂任务前，进行严密细致的分步规划",
    "Interview me to align on a plan.": "对我进行交互式提问访谈，对齐并完善设计方案。",
    "Interview me to align on a plan": "对我进行交互式提问访谈，对齐并完善设计方案",
    "Invoke a team of agents to autonomously tackle large projects.": "调用多智能体协同军团，自主分工攻克大型复杂项目。",
    "Invoke a team of agents to autonomously tackle large projects": "调用多智能体协同军团，自主分工攻克大型复杂项目",
    "Reflect on recent successes or corrections to capture reusable skills or rules.": "反思近期成功经验或纠正记录，沉淀为可复用的技能或规则。",
    "Reflect on recent successes or corrections to capture reusable skills or rules": "反思近期成功经验或纠正记录，沉淀为可复用的技能或规则",
    "Invoke the Boost multi-agent orchestrator for complex tasks.": "调用 Boost 多智能体编排器，以高算力深度思考攻克复杂任务。",
    "Invoke the Boost multi-agent orchestrator for complex tasks": "调用 Boost 多智能体编排器，以高算力深度思考攻克复杂任务",
    
    # Customization skills & workflows
    "Interactive guide to design and create a scheduled background automation.": "交互式引导设计并创建计划后台自动化任务。",
    "Interactive guide to design and create a scheduled background automation": "交互式引导设计并创建计划后台自动化任务",
    "How to manage and create plugins — namespaced bundles of skills, agents, rules, MCP servers and hooks that install, enable and disable as a single unit.": "管理与创建插件——包含技能、智能体、规则、MCP 服务与钩子的集成包。",
    "How to manage and create plugins — namespaced bundles of skills, agents, rules, MCP servers and hooks that install, enable and disable as a single unit": "管理与创建插件——包含技能、智能体、规则、MCP 服务与钩子的集成包",
    
    # Command menu & palette labels
    "Commands": "命令",
    "Slash Commands": "快捷斜杠命令",
}

for k, v in new_entries.items():
    dictionary[k] = v

print(f"Total dictionary entries: {len(dictionary)}")

# 1. Update dist/dictionary.json
with open(DICT_PATH, "w", encoding="utf-8") as f:
    json.dump(dictionary, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"Updated {DICT_PATH}")

# 2. Serialize for JS (pure 7-bit ASCII unicode escapes)
js_dict_str = json.dumps(dictionary, indent=2, ensure_ascii=True)

# 3. Update dist/preload.js and dist/engine.js
for path in [PRELOAD_PATH, ENGINE_PATH]:
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # Find dictionary boundaries
    prefix = "const dictionary = "
    suffix = ";\n\n  // 2."
    
    start_idx = code.find(prefix)
    if start_idx == -1:
        raise ValueError(f"Could not find '{prefix}' in {path}")
    
    end_idx = code.find(suffix, start_idx)
    if end_idx == -1:
        raise ValueError(f"Could not find '{suffix}' in {path}")
    
    new_code = code[:start_idx + len(prefix)] + js_dict_str + code[end_idx:]
    
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_code)
    
    # Verify 7-bit ASCII
    with open(path, "rb") as f:
        raw_bytes = f.read()
    non_ascii = [b for b in raw_bytes if b > 127]
    if non_ascii:
        raise ValueError(f"CRITICAL: {path} contains {len(non_ascii)} non-ASCII bytes!")
    print(f"Verified {path}: 100% 7-bit ASCII clean ({len(raw_bytes)} bytes)")

print("All files synchronized successfully!")
