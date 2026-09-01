# Antigravity-Chinese-Patch（Antigravity 全平台通用中文汉化补丁）

<p align="center">
  <a href="https://github.com/good9527/Antigravity-Chinese-Patch">
    <img src="https://img.shields.io/badge/Language-Chinese%20%26%20English-brightgreen.svg?style=for-the-badge" alt="Bilingual Support">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg?style=for-the-badge" alt="Platform Support">
    <img src="https://img.shields.io/badge/Engine-Zero--Dependency%20Native%20Patcher-orange.svg?style=for-the-badge" alt="Native Engine">
    <img src="https://img.shields.io/badge/Persistence-3--Tier%20Self--Healing-red.svg?style=for-the-badge" alt="Self Healing">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

这是一个针对 Google 出品的强大智能体编码助手 **Google Antigravity** 桌面客户端的开源、零依赖、永久自愈的通用中文汉化补丁系统与动态 DOM 扫描引擎。

This is an open-source, zero-dependency, permanent self-healing Chinese localization patch and dynamic DOM scanning engine for **Google Antigravity** (Windows, macOS, and Linux).

---

## 📑 目录 | Table of Contents

- [🌟 核心特性 | Features](#-核心特性--features)
- [🏛️ 三级持久化自愈架构 | 3-Tier Persistence Architecture](#️-三级持久化自愈架构--3-tier-persistence-architecture)
- [🚀 快速安装指南 | Installation Guide](#-快速安装指南--installation-guide)
  - [🪟 Windows 安装 (在线 / 本地)](#-windows-安装-在线--本地)
  - [🍎 macOS 安装 (在线 / 本地)](#-macos-安装-在线--本地)
  - [🐧 Linux 安装 (在线 / 本地)](#-linux-安装-在线--本地)
- [🎛️ 交互式控制台菜单 | Interactive Console Menu](#️-交互式控制台菜单--interactive-console-menu)
- [⚙️ CLI 命令行参数与自动化 | CLI Flags & Automation](#️-cli-命令行参数与自动化--cli-flags--automation)
- [🩺 健康检查与诊断报告 | Health Diagnostics](#-健康检查与诊断报告--health-diagnostics)
- [🔄 备份与一键还原 | Backup & Rollback](#-备份与一键还原--backup--rollback)
- [🌐 多源 CDN 瀑布流加速 | Multi-CDN Waterfall Acceleration](#-多源-cdn-瀑布流加速--multi-cdn-waterfall-acceleration)
- [📂 仓库与发行包结构 | Repository Layout](#-仓库与发行包结构--repository-layout)
- [🛡️ 安全隔离与代码保护 | Safety & Code Protection](#️-安全隔离与代码保护--safety--code-protection)
- [⚖️ 免责声明 | Disclaimer](#️-免责声明--disclaimer)

---

## 🌟 核心特性 | Features

### 🇨🇳 100% 深度汉化与动态同步 | 100% Complete UI Localization
- **动态状态秒级同步**：完美覆盖 React 高频刷新的动态状态计时器（如 `Thinking for 1.2s` $\rightarrow$ `思考中 (1.2秒)`，`Working for 5s` $\rightarrow$ `处理中 (5秒)`，`Completed in 320ms` $\rightarrow$ `完成用时 320ms`）。
- **动态计数器与相对时间**：自动转换辅助窗格计数（`Subagents 0` $\rightarrow$ `子智能体 0`，`3 files changed` $\rightarrow$ `3 个文件已修改`）与相对时间戳（`10d` $\rightarrow$ `10天前`，`5m` $\rightarrow$ `5分钟前`，`1mo` $\rightarrow$ `1个月前`）。
- **全属性拦截覆盖**：全面拦截 `placeholder`、`title`（悬停气泡提示）、`aria-label` 以及特殊下拉菜单（`\u00a0` 不换行空格标准化处理）。
- **全设置与模型面板汉化**：100% 翻译了设置描述、模型配额余额面板、安全沙箱权限控制、快捷键功能表与反馈诊断弹窗。

### ⚡ 纯原生零依赖内存注入 | Zero-Dependency Native Engine
- **无需安装 Node.js / npm / Python (Windows)**：Windows 端基于原生 C# / .NET 内存级 ASAR 解析与重构引擎，**50毫秒极速注入**，告别繁重依赖。
- **macOS / Linux 开箱即用**：macOS 和 Linux 端采用内置 Python 3 原生流式 ASAR 引擎，无需第三方包。
- **100% 保留原生宿主文件**：不硬替换官方 `app.asar` 二进制包，而是动态解析并提取当前客户端的 `dist/preload.js` 追加注入，**永不产生版本冲突，完美兼容未来任何官方升级**。
- **零会话中断 (Zero Session Disruption)**：补丁热注入过程无锁、原子写入，运行中的智能体无需强制杀死进程，重启或刷新窗口（`Ctrl+R`）即可生效。

### 🛡️ 官方更新自动跟随守护 | Auto-Healing Daemon
- **一次安装，永久保活**：内置后台守护服务（Windows 计划任务 / 启动项，macOS launchd LaunchAgent，Linux systemd user unit / inotify），当 Google 官方后台静默升级覆盖 `app.asar` 时，后台守护将在 50 毫秒内自动重新注入汉化，**真正实现零维护、永久中文**。

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
| - Win: Task Scheduler |              | - Offline Local Cache |              | - Zero Lock Injection |
|   & HKCU Run Key      |              |   (~/.antigravity-    |              | - Pure ASCII Escapes  |
| - Mac: launchd plist  |              |   chinese-patch/)     |              | - Atomic Temp Swap    |
| - Lin: systemd unit   |              | - CDN 4-Tier Fallback |              | - Sub-50ms Hot Patch  |
| - Instant Re-Patch    |              | - Version-Agnostic    |              | - ContextBridge Safe  |
+-----------------------+              +-----------------------+              +-----------------------+
```

1. **Tier A (实时文件系统监控守护 - Real-Time FileSystemWatcher Daemon)**：
   - 在操作系统层注册后台守护进程。
   - 监听 `resources/app.asar` 的 `Created` 与 `Changed` 事件。
   - 检测到官方更新覆盖后，自动触发内存级重补丁，并在重试退避机制下完成无损热替换。
2. **Tier B (离线本地缓存与启动拦截 - Offline Cache & Launch Resolver)**：
   - 补丁核心与守护脚本同步缓存在本地用户目录（Windows: `%APPDATA%\AntigravityChinesePatch`，macOS/Linux: `~/.antigravity-chinese-patch`）。
   - 无网络环境下仍可 100% 离线自愈与手动安装。
3. **Tier C (无损就地注入引擎 - In-Place Hot Patch Preload Engine)**：
   - 智能解构 ASAR 头部 JSON 索引表，精准定位 `dist/preload.js`。
   - 仅在 preload 入口末尾追加自执行汉化逻辑，剥离历史旧标记，重新计算偏移表并原子重写。

---

## 🚀 快速安装指南 | Installation Guide

### 🪟 Windows 安装 (在线 / 本地)

#### 方式 1：PowerShell 一键在线安装（推荐 ⭐⭐⭐⭐⭐）
打开 **PowerShell** 窗口（按 `Win + X` 选择终端），复制并粘贴运行以下命令：

```powershell
iwr -useb https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.ps1 | iex
```

*(备用 GitHub 官方源)*：
```powershell
iwr -useb https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/install.ps1 | iex
```

#### 方式 2：本地安装包 / 双击运行
1. 从 [Releases 发行页](https://github.com/good9527/Antigravity-Chinese-Patch/releases) 下载 `Antigravity-Chinese-Patch-Elite.zip`。
2. 解压后直接**双击运行 `安装汉化补丁.bat`**。
3. 根据界面提示输入数字 `1` 即可完成一键极速安装。

---

### 🍎 macOS 安装 (在线 / 本地)

#### 方式 1：Terminal 一键在线安装
打开 **Terminal (终端)**，复制并运行：

```bash
curl -fsSL https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.sh | bash
```

*(备用 GitHub 官方源)*：
```bash
curl -fsSL https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/install.sh | bash
```

#### 方式 2：本地离线安装
解压发行包后，在终端中执行：
```bash
chmod +x install.sh
./install.sh
```

---

### 🐧 Linux 安装 (在线 / 本地)

打开终端执行：
```bash
curl -fsSL https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.sh | bash
```

---

## 🎛️ 交互式控制台菜单 | Interactive Console Menu

在 Windows 下双击 `安装汉化补丁.bat` 或执行 `powershell -ExecutionPolicy Bypass -File .\patch_antigravity.ps1`，将打开 Elite Toolkit 控制台管理面板：

```
======================================================================
          Antigravity 中文汉化管理面板 (Elite Toolkit v3.0)
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

### 菜单选项说明
1. **[1] 一键安装 / 更新汉化补丁**：自动检测客户端安装目录，备份官方原版 `app.asar.bak`，50ms 注入汉化代码，并开启后台自愈守护。
2. **[2] 运行环境与健康状态诊断**：全面检查客户端版本、ASAR 补丁状态、备份完整度、守护进程健康度及多 CDN 延迟。
3. **[3] 开启 / 关闭后台自动守护**：管理 Tier A 后台文件监控守护进程，自由切换自愈保活状态。
4. **[4] 一键恢复官方原版备份**：将客户端无损还原至官方未修改状态（100% 字节精确还原）。
5. **[5] 退出**：安全退出管理面板。

---

## ⚙️ CLI 命令行参数与自动化 | CLI Flags & Automation

安装脚本支持全功能的命令行参数，便于脚本集成、CI/CD 自动化及静默部署：

### Windows PowerShell (`install.ps1` / `patch_antigravity.ps1`)

| 参数 / Flag | 缩写 | 说明 / Description |
|---|---|---|
| `--install` | `-i` | 执行一键注入安装，创建备份并激活守护进程 |
| `--uninstall` | `-u` | 还原官方原版备份，清理离线缓存并注销守护服务 |
| `--check` | `-c` | 执行环境与健康状态诊断（退出码 0 表示健康，1 表示异常） |
| `--restore` | `-r` | 从 `app.asar.bak` 一键还原官方原版 |
| `--daemon <enable\|disable\|status>` | - | 配置后台自愈守护进程状态 |
| `--daemon-on` / `--daemon-off` | - | 快捷启用 / 禁用自愈守护 |
| `--quiet` / `--silent` | `-q` | 静默模式，无控制台交互输出 |
| `--json` | - | 与 `--check` 配合使用，输出标准 JSON 格式诊断数据 |
| `--path <dir>` | `-p` | 指定自定义 Antigravity 安装目录 |

#### 示例 / Examples:
```powershell
# 静默安装
powershell -ExecutionPolicy Bypass -File .\install.ps1 --install --quiet

# 运行健康诊断并输出 JSON
powershell -ExecutionPolicy Bypass -File .\install.ps1 --check --json

# 启用后台守护
powershell -ExecutionPolicy Bypass -File .\install.ps1 --daemon enable

# 指定自定义路径进行补丁安装
powershell -ExecutionPolicy Bypass -File .\install.ps1 --path "D:\Antigravity" --install
```

---

### macOS & Linux (`install.sh`)

| 参数 / Flag | 缩写 | 说明 / Description |
|---|---|---|
| `--install` | `-i` | 安装汉化补丁并配置 launchd / systemd 守护 |
| `--uninstall` | `-u` | 还原原版备份并卸载守护配置与缓存 |
| `--check` | `-c` | 执行健康诊断与版本检测 |
| `--restore` | `-r` | 从备份文件还原官方原装 |
| `--daemon <enable\|disable\|status>` | - | 开启 / 关闭 / 查询后台守护服务 |
| `--quiet` / `--silent` | `-q` | 静默模式 |
| `--json` | - | JSON 诊断输出 |
| `--path <dir>` | `-p` | 指定自定义安装路径 |

#### 示例 / Examples:
```bash
# macOS/Linux 静默安装
./install.sh --install --quiet

# 检查当前状态
./install.sh --check

# 一键还原官方原版
./install.sh --restore
```

---

## 🩺 健康检查与诊断报告 | Health Diagnostics

运行 `--check` 参数或在菜单中选择 `[2]`，系统将执行全方位的健康体检：

### 控制台诊断输出示例：
```text
==========================================================
     Antigravity Chinese Patch Health Diagnostics         
==========================================================
  Installation Directory : C:\Users\Username\AppData\Local\Programs\antigravity
  Active ASAR Status     : PATCHED [OK]
  Original Clean Backup  : PRESENT [OK]
  Auto-Healing Daemon    : ENABLED [OK]
==========================================================
  Verdict: HEALTHY (100% Operational & Self-Healing Enabled)
==========================================================
```

### JSON 诊断数据输出示例 (`--check --json`)：
```json
{
  "path": "C:\\Users\\Username\\AppData\\Local\\Programs\\antigravity",
  "asar_exists": true,
  "version": "2.10.0",
  "is_patched": true,
  "backup_exists": true,
  "daemon_enabled": true,
  "healthy": true
}
```

---

## 🔄 备份与一键还原 | Backup & Rollback

- **安全备份机制**：首次安装补丁时，系统会自动将官方原始 `app.asar` 备份为 `app.asar.bak`。
- **一键无损还原**：
  - **图形菜单**：运行 `安装汉化补丁.bat` 选择 `[4] 一键恢复官方原版备份`。
  - **命令行**：运行 `powershell -ExecutionPolicy Bypass -File .\install.ps1 --restore` 或 `./install.sh --restore`。
  - **手动还原**：直接删除 `resources/app.asar`，将同目录下的 `app.asar.bak` 重命名为 `app.asar` 即可。

---

## 🌐 多源 CDN 瀑布流加速 | Multi-CDN Waterfall Acceleration

在线安装器内置智能 4 级 CDN 容灾瀑布流，国内直连毫秒级下载：

```
[1. jsDelivr Fastly CDN]  ---> (超时 / 失败) --->
[2. cdnjs Cloudflare CDN] ---> (超时 / 失败) --->
[3. Ghproxy / Ghfast 镜像] ---> (超时 / 失败) --->
[4. GitHub Raw 官方源]
```

---

## 📂 仓库与发行包结构 | Repository Layout

```text
Antigravity-Chinese-Patch/
├── dist/
│   ├── preload.js          # 核心汉化引擎 (Pure ASCII Unicode escapes / UTF-8)
│   ├── dictionary.json     # 完整汉化词典 (514 核心词条)
│   └── engine.js           # 独立运行时翻译与 DOM 观察器引擎
├── watcher/
│   ├── watcher.ps1         # Windows FileSystemWatcher 实时文件监控守护脚本
│   ├── auto_heal.sh        # macOS / Linux 后台自动守护脚本
│   ├── com.antigravity.chinese.patch.plist # macOS launchd 配置定义
│   ├── antigravity-patch.service           # Linux systemd 服务单元
│   └── antigravity-patch.path              # Linux systemd 路径监听单元
├── tests/
│   ├── test_runner.py      # E2E 测试套件编排与运行器 (79 项全阶测试)
│   ├── test_engine.py      # Tier 1 & Tier 2 DOM 翻译与正则测试
│   ├── test_asar.py        # Tier 1 & Tier 2 ASAR 引擎与无损注入测试
│   ├── test_integration.py # Tier 3 CLI 与 CDN 瀑布流测试
│   └── test_scenarios.py   # Tier 4 真实工作负载与自动升级自愈测试
├── .github/
│   └── workflows/
│       └── release.yml     # Multi-OS CI/CD 自动化构建与发布流水线
├── patch_antigravity.ps1   # Windows Elite 控制台管理面板
├── install.ps1             # Windows 零依赖一键安装与守护脚本 (.NET ASAR 引擎)
├── install.sh              # macOS / Linux 零依赖安装与守护脚本 (Python ASAR 引擎)
├── 安装汉化补丁.bat        # Windows UTF-8 双击批处理启动器
└── README.md               # 项目双语说明文档
```

---

## 🛡️ 安全隔离与代码保护 | Safety & Code Protection

汉化引擎内置严格的安全隔离与代码保护规则：
- **Monaco / 编辑器代码保护**：严禁翻译 `.monaco-editor`、`pre`、`code`、`.hljs`、`.terminal`、`.xterm` 内的任何代码、语法高亮与控制台输出。
- **用户输入保护**：严禁翻译 `textarea`、`input[type="text"]` 及 `[contenteditable="true"]` 用户输入区域中的内容。
- **Shadow DOM 穿透**：无缝穿透 Shadow Root 深度遍历，确保所有自定义 Web Component UI 元素完整汉化。

---

## ⚖️ 免责声明 | Disclaimer

- 本项目为开源无损注入技术研究成果，仅供个人学习与交流使用，不含任何商业用途。
- 补丁所翻译的界面文案及原客户端版权均归 Google 官方所有。若您喜欢该产品，请支持官方正版。
- This project is an open-source non-destructive localization research toolkit for personal learning purposes only. All intellectual properties belong to their respective copyright holders.
