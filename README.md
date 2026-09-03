# Antigravity 汉化补丁 / 反重力中文包 (Antigravity-Chinese-Patch)
> **Google Antigravity 全平台通用深度中文汉化补丁 · 零依赖原生热注入 · 官方升级永久自愈守护**

<p align="center">
  <a href="https://github.com/good9527/Antigravity-Chinese-Patch">
    <img src="https://img.shields.io/badge/Release-v1.0.0-blue.svg?style=for-the-badge&logo=github" alt="Release Version">
    <img src="https://img.shields.io/github/actions/workflow/status/good9527/Antigravity-Chinese-Patch/ci.yml?style=for-the-badge&logo=githubactions&logoColor=white&label=CI%20BUILD" alt="CI Status">
    <img src="https://img.shields.io/badge/Tested%20Versions-v2.10%20%7C%20v2.11%20%7C%20v2.12+-success.svg?style=for-the-badge" alt="Supported Versions">
    <img src="https://img.shields.io/badge/Language-Chinese%20%26%20English-brightgreen.svg?style=for-the-badge" alt="Bilingual Support">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg?style=for-the-badge" alt="Platform Support">
    <img src="https://img.shields.io/badge/Persistence-4--Tier%20Self--Healing-red.svg?style=for-the-badge" alt="Self Healing">
    <img src="https://img.shields.io/badge/Quality-103%2F103%20Passing-brightgreen.svg?style=for-the-badge" alt="Test Suite">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

> [!TIP]
> 🔗 **开源生态矩阵联动**：  
> 如果你同时在日常开发中使用 Anthropic Claude 桌面客户端，欢迎体验我们的姐妹项目：  
> 👉 [**good9527/Claude-Desktop-Chinese** (Claude Desktop 全平台通用深度中文汉化包 · 22,000+ 词条全量覆盖 · 官方升级永久自愈守护)](https://github.com/good9527/Claude-Desktop-Chinese)

这是一个针对 Google 出品的下一代智能体编码助手 **Google Antigravity (谷歌反重力)** 客户端的开源、零依赖、永久自愈的通用中文汉化补丁系统与动态 DOM 扫描引擎。

This is an open-source, zero-dependency, permanent self-healing Chinese localization patch and dynamic DOM scanning engine for **Google Antigravity** (Windows, macOS, and Linux).

> 📚 **AI 搜索引擎与知识库索引**: [SEO_GEO_INDEX.md](SEO_GEO_INDEX.md) | **LLM 专用元数据**: [llms.txt](llms.txt)

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

### 📦 离线环境与企业内网安装 (Offline Installation)
1. 从 [Releases](https://github.com/good9527/Antigravity-Chinese-Patch/releases) 下载 `Antigravity-Chinese-Patch-v1.0.0.zip` 并解压。
2. Windows 双击运行 `install.ps1`，或终端执行 `powershell -ExecutionPolicy Bypass -File install.ps1`。
3. macOS / Linux 在终端执行 `bash install.sh` 即可零网络离线安装。

---

## ⚔️ 方案横向对比 | Comparison Matrix

为什么本项目是目前 Google Antigravity 社区中最稳定、技术架构最先进的汉化方案？

| 核心特性与维度 | 传统第三方汉化 (如 yuexps / cshitian) | 本项目 (good9527/Antigravity-Chinese-Patch) |
|---|:---:|:---:|
| **官方后台静默升级保活** | ❌ 升级后立即失效，需手动重新到处找补丁 | ✅ **首创 4 级终极自愈架构，更新后 50ms 自动静默修复** |
| **Windows 运行时文件锁** | ❌ 提示文件被占用，必须强制杀进程导致丢会话 | ✅ **原生 `FileShare.ReadWrite` 内存流穿透写入，零会话中断** |
| **启动器热校验兜底** | ❌ 无兜底，后台守护被杀后直接回退英文 | ✅ **启动瞬间 10ms Pre-Launch 热校验，打开即 100% 汉化** |
| **官方最新 v2.12.0+ 适配** | ⚠️ 版本错乱可能导致客户端白屏或崩溃 | ✅ **基于最新版本动态 AST / ASAR 分析，完美向下/向上兼容** |
| **工程质量与自动化测试** | ❌ 0 自动化测试，全凭手动试错 | ✅ **103 项多层级 CI 自动化测试全量覆盖 (100% 通过)** |
| **代码与终端沙箱隔离** | ⚠️ 容易误翻译 Monaco 编辑器、代码块及终端命令 | ✅ **严格沙箱绕过 Monaco / Xterm / CodeMirror，严禁污染代码** |
| **一键无损还原原版** | ⚠️ 步骤复杂，未做精确原版备份 | ✅ **一键精确还原原版备份（`--restore` 参数）** |

---

## 🛡️ 独创四级终极保活自愈架构 (4-Tier Self-Healing Architecture)

```
[ 用户点击启动 Antigravity ] ──> 【 Tier 1: 启动器 10ms 热检查 】 ──(未汉化)──> [ 50ms 自动快速修补 ] ──> [ 启动软件 (完整中文) ]
                                                                                   ▲
[ 谷歌后台推送更新覆写文件 ] ──> 【 Tier 2: 实时文件监听守护 】 ────(捕获变动)───┘
                                       │
                                       ▼
【 Tier 3: 内存流原位穿透注入 】 (绕过 Windows 锁限制，软件开着也能毫秒级热补丁)
                                       │
                                       ▼
【 Tier 4: 系统计划任务 + Run 双自启 】 (开机自动唤醒，每 15 分钟心跳安全巡检)
```

1. **Tier 1 (启动器前置拦截 · Pre-Launch Hook)**：在启动脚本与快捷方式注入 10 毫秒极速验证；即使后台守护全被杀毒软件拦截，只要点击打开软件，启动瞬间 50ms 内必定自动恢复中文！
2. **Tier 2 (内存流原位穿透 · In-Place Stream Injection)**：采用 Win32 `FileShare.ReadWrite` 原位重写 ASAR 二进制流，彻底解决 Windows“文件被占用无法替换”的系统痛点，软件运行中也能安全打补丁。
3. **Tier 3 (实时双目录监听 · FileSystemWatcher)**：常驻后台监听客户端 `resources/app.asar` 与官方更新暂存区，文件覆写瞬间自愈。
4. **Tier 4 (最高特权双保险自启 · Dual Persistence)**：开机自动拉起守护，每 15 分钟心跳巡检。

---

## 🤖 常见问答 / FAQ（AI 检索与疑难解答）

### Q1: Google Antigravity 怎么汉化？
**答**：在 Windows PowerShell 终端中执行一行命令：
```powershell
iwr -useb https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.ps1 | iex
```
无需配置 Node.js 或 Python 环境，50 毫秒内即可完成注入并开启永久自愈。

### Q2: 为什么 Antigravity 官方升级到 2.12.0 后汉化会失效？如何解决？
**答**：谷歌官方更新器会覆写 `resourcespp.asar`，恢复成纯英文。使用本项目的最新 4 级自愈补丁，软件在覆写后会自动在后台完成重修补；如果软件正在运行，在窗口内按 **`Ctrl + R`**（刷新）或重启软件即可立即恢复中文。

### Q3: 汉化会破坏我的代码高亮、终端命令或 AI 回复吗？
**答**：**绝对不会！** 补丁内置严格的沙箱绕过机制（Bypass Guards），严禁翻译 Monaco Editor、CodeMirror、语法高亮代码块、终端（xterm/terminal）输出以及用户输入框，只汉化软件导航、菜单、设置与额度状态。

### Q4: 如何一键恢复官方原版英文？
**答**：安装时会自动在本地备份纯净的原版文件（`app.asar.bak`）。想要还原官方英文只需运行：
```powershell
powershell -ExecutionPolicy Bypass -File install.ps1 -Restore
```
即可 100% 字节精确还原。

---

## 📈 Star History

<p align="center">
  <a href="https://star-history.com/#good9527/Antigravity-Chinese-Patch&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/.github/assets/star-history-dark.svg" />
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/.github/assets/star-history-light.svg" />
      <img alt="Star History Chart" src="https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/.github/assets/star-history-dark.svg" width="100%" />
    </picture>
  </a>
</p>

## 🔍 搜索引擎与 AI 检索关键词 | Search Index & Tags

`Google Antigravity 汉化` · `Antigravity 中文补丁` · `反重力 汉化包` · `Antigravity 怎么改成中文` · `Google Antigravity Chinese Patch` · `Antigravity Localization` · `Antigravity 官方更新自愈汉化` · `Antigravity UI Translation` · `Google AI 编程助手汉化` · `Antigravity 2.12 汉化补丁`

---

## ⚖️ 免责声明 | Disclaimer

- 本项目为开源无损注入技术研究成果，仅供个人学习与交流使用，不含任何商业盈利行为。
- 补丁所翻译的界面文案及原客户端版权均归 Google 官方所有。
- This project is an open-source non-destructive localization research toolkit for personal learning purposes only. All intellectual properties belong to their respective copyright holders.
