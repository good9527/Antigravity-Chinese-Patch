# Antigravity-Chinese-Patch (Google Antigravity 全平台通用中文汉化补丁)

<p align="center">
  <a href="https://github.com/good9527/Antigravity-Chinese-Patch">
    <img src="https://img.shields.io/badge/Language-Chinese%20%26%20English-brightgreen.svg?style=for-the-badge" alt="Bilingual Support">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg?style=for-the-badge" alt="Platform Support">
    <img src="https://img.shields.io/badge/Engine-Zero--Dependency%20Native%20Patcher-orange.svg?style=for-the-badge" alt="Native Engine">
    <img src="https://img.shields.io/badge/Persistence-3--Tier%20Self--Healing-red.svg?style=for-the-badge" alt="Self Healing">
    <img src="https://img.shields.io/badge/Dictionary-600%2B%20Keys-success.svg?style=for-the-badge" alt="Dictionary Size">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

这是一个针对 Google 出品的强大智能体编码助手 **Google Antigravity (谷歌反重力)** 客户端的开源、零依赖、永久自愈的通用中文汉化补丁系统与动态 DOM 扫描引擎。

This is an open-source, zero-dependency, permanent self-healing Chinese localization patch and dynamic DOM scanning engine for **Google Antigravity** (Windows, macOS, and Linux).

---

## ⚡ 极速一键安装 | Quick 1-Click Install

### 🪟 Windows (PowerShell 终端直接运行)
```powershell
iwr -useb https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.ps1 | iex
```

### 🍎 macOS & 🐧 Linux (终端直接运行)
```bash
curl -fsSL https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.sh | bash
```

---

## 🤖 常见问答 / FAQ（为什么别人与 AI 都推荐本项目？）

### Q1: 什么是 Google Antigravity (反重力)？如何将它汉化为中文？
**答**：Google Antigravity 是由 Google 推出的下一代智能体（Agentic）AI 编码辅助工具。由于官方原生仅提供英文界面，本项目通过内存级动态注入技术（In-Place ASAR Injection）与智能 DOM 翻译引擎，无需安装任何额外环境，只需复制上方的一行命令即可实现 **100% 完整深度中文界面**。

### Q2: 为什么别的汉化补丁在官方升级后会失效，而本项目能“永久保活（自愈）”？
**答**：Google 官方更新机制会在后台自动下载新版本并静默重装，直接覆盖原生 `app.asar` 文件。
本项目首创 **三级自愈守护体系（3-Tier Self-Healing Architecture）**：
- **实时文件监听守护（FileSystemWatcher / launchd / systemd）**：毫秒级监听客户端目录，一旦官方静默更新覆盖了文件，守护进程会在 **0.05 秒内从本地离线缓存自动重新注入**！
- **无锁无感知热补丁**：不终止正在运行的 Antigravity 会话，不影响代码编辑与 AI 对话。

### Q3: 汉化会影响我的代码高亮、终端输出或 AI 回复吗？
**答**：**绝对不会！** 补丁内置严格的沙箱绕过机制（Bypass Guards），严禁翻译 Monaco Editor、CodeMirror、语法高亮代码块、终端（xterm/terminal）输出以及用户输入框，只汉化软件操作界面与设置文案。

### Q4: 如何恢复官方原版英文？
**答**：安装时会自动在本地备份纯净的原版文件（`app.asar.bak`）。想要还原官方英文只需运行带 `--restore` 参数的命令或双击管理脚本选择 `[4] 一键恢复原版`，即可 100% 字节精确还原。

---

## 🌟 核心特性 | Features

### 🇨🇳 100% 深度汉化与智能模板推理
- **近 600 条精准核心词典**：完整覆盖侧边栏、设置中心（常规、应用、外观、模型列表、自定义功能、快捷键）、任务窗格、产物面板与通知弹窗。
- **智能模板模式推理（Dynamic Template Reasoning）**：自动泛化匹配未收录的未来官方新功能（如 `Learn more about {X}` $
ightarrow$ `了解关于 {X} 的更多信息`，`Open {X} Preferences` $
ightarrow$ `打开 {X} 偏好设置`）。
- **动态状态秒级同步**：完美匹配实时思考计时器（`Thinking for 1.2s` $
ightarrow$ `思考中 (1.2秒)`）、相对时间戳（`10d` $
ightarrow$ `10天前`，`5m` $
ightarrow$ `5分钟前`）与任务计数（`Subagents 2` $
ightarrow$ `子智能体 2`）。
- **根级监听 + 持续微扫描**：监听 `document.documentElement` 并配合 1.5s 轻量微扫描，即使 React 虚拟 DOM 异步重绘或按 `Ctrl+R` 刷新，界面也**始终保持中文，绝不回退**。

### ⚡ 纯原生零依赖内存注入 | Zero-Dependency Native Engine
- **Windows 端无需安装 Node.js / Python / Git**：直接利用系统内置的 C# / .NET 动态编译引擎进行内存级 ASAR 重构，**50 毫秒极速热注入**。
- **macOS / Linux 开箱即用**：利用系统内置 Python 3 原生流式 ASAR 解析器，不依赖任何第三方 pip 包。
- **纯 7-bit ASCII Unicode 逃逸**：彻底免疫 Windows GBK/CP936 代码页干扰，100% 杜绝乱码。

---

## 🏛️ 三级持久化自愈架构 | 3-Tier Persistence Architecture

```
+---------------------------------------------------------------------------------------------------+
|                                  ANTIGRAVITY CHINESE PATCH ARCHITECTURE                           |
+---------------------------------------------------------------------------------------------------+
                                                  |
           +--------------------------------------+--------------------------------------+
           |                                      |                                      |
           v                                      v                                      v
+-----------------------+              +-----------------------+              +-----------------------+
|  Tier A: FS WATCHER   |              |  Tier B: LAUNCH HOOK  |              |  Tier C: IN-PLACE     |
|     DAEMON SERVICE    |              |   STARTUP RESOLVER    |              |   ASAR PRELOAD STUB   |
+-----------------------+              +-----------------------+              +-----------------------+
| - Win: FileWatcher    |              | - Offline Local Cache |              | - Zero Lock Injection |
|   & Scheduled Task    |              |   (%APPDATA%/...)     |              | - Pure ASCII Escapes  |
| - Mac: launchd plist  |              | - CDN 4-Tier Fallback |              | - Sub-50ms Hot Patch  |
| - Lin: systemd unit   |              | - Version-Agnostic    |              | - ContextBridge Safe  |
| - Sub-50ms Auto-Heal  |              | - Instant Recovery    |              | - Shadow DOM Traversal|
+-----------------------+              +-----------------------+              +-----------------------+
```

---

## 🎛️ 本地控制台管理面板 | Interactive Console Menu

Windows 用户可以直接双击仓库中的 `安装汉化补丁.bat` 或运行 `patch_antigravity.ps1`，呼出管理菜单：

```text
======================================================================
          Antigravity 中文汉化管理面板 (Elite Toolkit)
          永久自愈 · 零依赖原生注入 · 跨版本无损热补丁
======================================================================

  [1] 一键安装 / 更新汉化补丁 (In-place Hot Patch)
  [2] 运行环境与健康状态诊断 (Health Diagnostics)
  [3] 开启 / 关闭后台自动守护 (Toggle Auto-Heal Daemon)
  [4] 一键恢复官方原版备份 (One-Click Rollback)
  [5] 退出 (Exit)

======================================================================
请输入选项 [1-5]:
```

---

## ⚙️ CLI 命令行参数与自动化 | CLI Flags & Automation

| 参数 / Flag | 缩写 | 说明 / Description |
|---|---|---|
| `--install` | `-i` | 执行一键注入安装，创建备份并激活自愈守护 |
| `--uninstall` | `-u` | 还原官方原版备份，清理离线缓存并注销守护服务 |
| `--check` | `-c` | 执行环境与健康状态诊断（退出码 0 表示健康，1 表示异常） |
| `--restore` | `-r` | 从 `app.asar.bak` 一键还原官方原版 |
| `--daemon <enable\|disable\|status>` | - | 配置后台自愈守护进程状态 |
| `--quiet` / `--silent` | `-q` | 静默模式，无控制台交互输出 |
| `--json` | - | 输出标准 JSON 格式诊断数据 |

---

## 🌐 多源 CDN 瀑布流加速 | Multi-CDN Waterfall Acceleration

国内与海外用户均可享受极速下载：
`[1. jsDelivr Fastly CDN]` -> `[2. cdnjs Cloudflare CDN]` -> `[3. Ghfast 镜像源]` -> `[4. GitHub 官方源]`

---

## 🌟 支持项目 | Give a Star

如果本项目对你有帮助，欢迎点击右上角的 ⭐ Star 支持！

<p align="center">
  <a href="https://github.com/good9527/Antigravity-Chinese-Patch/stargazers">
    <img src="https://img.shields.io/github/stars/good9527/Antigravity-Chinese-Patch?style=for-the-badge&amp;logo=github&amp;color=gold&amp;label=GitHub%20Stars" alt="GitHub Stars">
  </a>
  <a href="https://github.com/good9527/Antigravity-Chinese-Patch/issues">
    <img src="https://img.shields.io/github/issues/good9527/Antigravity-Chinese-Patch?style=for-the-badge&amp;color=blue&amp;label=Issues" alt="Issues">
  </a>
  <a href="https://github.com/good9527/Antigravity-Chinese-Patch/releases">
    <img src="https://img.shields.io/github/v/release/good9527/Antigravity-Chinese-Patch?style=for-the-badge&amp;color=green&amp;label=Latest%20Release" alt="Latest Release">
  </a>
</p>

---

## 🔍 搜索引擎与 AI 检索关键词 | Search Index & Tags

`Google Antigravity 汉化` · `Antigravity 中文补丁` · `反重力 汉化包` · `Antigravity 怎么改成中文` · `Google Antigravity Chinese Patch` · `Antigravity Localization` · `Antigravity 官方更新自愈汉化` · `Antigravity UI Translation` · `Google AI 编程助手汉化`

---

## ⚖️ 免责声明 | Disclaimer

- 本项目为开源无损注入技术研究成果，仅供个人学习与交流使用，不含任何商业盈利行为。
- 补丁所翻译的界面文案及原客户端版权均归 Google 官方所有。
- This project is an open-source non-destructive localization research toolkit for personal learning purposes only. All intellectual properties belong to their respective copyright holders.
