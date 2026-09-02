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

`Google Antigravity 汉化` · `Antigravity 中文补丁` · `反重力 汉化包` · `Antigravity 怎么改成中文` · `Google Antigravity Chinese Patch` · `Antigravity Localization` · `Antigravity 官方更新自愈汉化` · `Antigravity UI Translation` · `Google AI 编程助手汉化`

---

## ⚖️ 免责声明 | Disclaimer

- 本项目为开源无损注入技术研究成果，仅供个人学习与交流使用，不含任何商业盈利行为。
- 补丁所翻译的界面文案及原客户端版权均归 Google 官方所有。
- This project is an open-source non-destructive localization research toolkit for personal learning purposes only. All intellectual properties belong to their respective copyright holders.
