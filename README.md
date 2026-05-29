# Antigravity-Chinese-Patch（Antigravity 中文汉化）

<p align="center">
  <a href="https://github.com/good9527/Antigravity-Chinese-Patch">
    <img src="https://img.shields.io/badge/Language-Chinese%20%26%20English-brightgreen.svg?style=for-the-badge" alt="Bilingual Support">
    <img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg?style=for-the-badge" alt="Platform Support">
    <img src="https://img.shields.io/badge/License-MIT-orange.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

这是一个针对 Google 出品的强大智能体编码助手 **Antigravity** 桌面客户端的开源无损汉化补丁与动态扫描引擎。

This is an open-source, non-destructive Chinese localization patch and dynamic DOM scanner engine for **Antigravity**, the powerful agentic AI coding assistant desktop client by Google.

---

## 🌟 核心特性 | Features

### 🇨🇳 100% 完美汉化 | 100% Deep Localization
- **动态状态秒级同步**：完美覆盖 React 高频刷新的动态状态计时器（例如 `Thinking for 1s` $\rightarrow$ `思考中 (1秒)`，`Working for 2.5s` $\rightarrow$ `处理中 (2.5秒)`）。
- **下拉菜单完全覆盖**：针对 React 列表中特殊的 `\u00a0`（不换行空格）编码进行了入口标准化处理，实现 `"Full Machine"` $\rightarrow$ **“整机授权”** 的完美翻译。
- **超链接完美拼接**：优雅分流并翻译被 React 分裂渲染的行内文本和超链接，告别中英混杂。
- **设置中心全覆盖**：翻译了 100% 的设置描述、模型余额面板、快捷键功能表和问题反馈页面。

### ☁️ 云端字典自动升级 | Live Cloud Updates (New ✨)
- **零延迟启动与热升级**：本补丁采用 `localStorage` 建立本地字典缓存。每次启动时在后台**异步自动拉取 GitHub 最新翻译词库**（`dictionary.json`）并静默合并，**无需重新运行补丁即可享受到最新的翻译校对！**
- **网络防断性兜底**：在离线或 GitHub 网络受限时，补丁自动无缝切换为内置离线字典，100% 可靠。

### 🛡️ 绝对稳定与安全 | Absolute Stability & Safety
- **主进程 0 修改**：补丁代码 **100% 隔离在渲染进程的注入层 (`preload.js`) 中**。我们保持客户端核心二进制文件和主进程 Node.js 原始状态不变，**绝对不会导致客户端闪退或更新损坏**。
- **智能兼容与无损还原**：一键安装脚本会在应用补丁前自动为您备份原版文件，随时可以双击一键还原。

---

## 💾 快速安装指南 | Installation Guide

> [!IMPORTANT]
> **本补丁已实现完全通用化！** 脚本会自动解析您系统的 AppData 目录和当前运行路径，适用于任何 Windows 用户。

### 方式 A：云端一键在线安装（最简单、最智能 ⭐⭐⭐）| Method A: Online Web Installer (Easiest)
不需要手动下载任何安装包或 Bat 脚本！直接在 Windows 中以管理员身份打开 **PowerShell** 窗口，复制并运行以下命令，即可在 5 秒内完成全自动云端极速汉化与热启动：

```powershell
iwr -useb https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/install.ps1 | iex
```

---

### 方式 B：本地一键离线替换 | Method B: Local Offline Replacer
1. 前往 [Releases](https://github.com/good9527/Antigravity-Chinese-Patch/releases) 页面，下载最新的汉化压缩包。
2. 将压缩包内的所有文件（`dist/` 目录、`安装汉化补丁.bat` 和 `patch_antigravity.ps1`）解压至任意目录。
3. **双击运行 `安装汉化补丁.bat`** 即可。脚本会自动识别您的客户端路径，关闭程序、备份原版、应用补丁并自动重启！

---

### 方式 C：极客/开发者（本地动态注入）| Method C: Developers (Dynamic Local Injection)
如果您安装了 Node.js，我们的安装脚本会自动启用 **ASAR 动态注入模式**！它会动态提取您当前的 `app.asar`，仅将汉化脚本注入其中并重新打包。**这能保证即使官方客户端发布升级，您的汉化补丁依然 100% 兼容！**

1. 克隆本仓库：
   ```bash
   git clone https://github.com/good9527/Antigravity-Chinese-Patch.git
   ```
2. 在仓库根目录下双击运行 `安装汉化补丁.bat` 即可完成本地动态注入。

---

## 📂 仓库结构 | Project Structure

```text
Antigravity-Chinese-Patch/
├── dist/
│   ├── preload.js          # 核心汉化注入脚本 (支持本地/云端双轨自愈)
│   └── dictionary.json     # 云端共享 JSON 汉化字典 (便于社区维护贡献)
├── 安装汉化补丁.bat          # Windows 一键执行批处理文件
├── patch_antigravity.ps1   # 动态 Asar 解包/打包及自动路径识别 PowerShell 核心脚本
├── install.ps1             # 云端一键在线安装核心脚本
└── README.md               # 项目双语使用说明书
```

---

## ⚖️ 免责声明 | Disclaimer

- 本项目仅为个人学习及 Electron 运行时 DOM 注入技术的开源研究成果，不含任何商业用途。
- 汉化所涉及的界面文案版权归原软件官方所有。若您喜欢该软件，请支持官方正版。
- This project is purely for personal learning and open-source research on Electron DOM injection, without any commercial purpose. All product copyrights belong to their respective owners.
