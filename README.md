# Antigravity-Chinese-Patch（Antigravity 全平台通用中文汉化补丁）

<p align="center">
  <a href="https://github.com/good9527/Antigravity-Chinese-Patch">
    <img src="https://img.shields.io/badge/Language-Chinese%20%26%20English-brightgreen.svg?style=for-the-badge" alt="Bilingual Support">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg?style=for-the-badge" alt="Platform Support">
    <img src="https://img.shields.io/badge/Engine-Zero--Dependency%20Native%20Patcher-orange.svg?style=for-the-badge" alt="Native Engine">
    <img src="https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge" alt="MIT License">
  </a>
</p>

这是一个针对 Google 出品的强大智能体编码助手 **Antigravity** 桌面客户端的开源无损汉化补丁与通用动态扫描引擎。

This is an open-source, zero-dependency, universal non-destructive Chinese localization patch and dynamic DOM scanner engine for **Antigravity** (Windows / macOS / Linux).

---

## 🌟 核心特性 | Features

### 🇨🇳 100% 深度汉化与动态同步 | 100% Deep Localization
- **动态状态秒级同步**：完美覆盖 React 高频刷新的动态状态计时器（例如 `Thinking for 1s` $\rightarrow$ `思考中 (1秒)`，`Working for 2.5s` $\rightarrow$ `处理中 (2.5秒)`，`Timed 5s` $\rightarrow$ `已计时 5 秒`）。
- **全属性覆盖**：支持 `placeholder`、`title`（悬停气泡）、`aria-label` 以及特殊下拉菜单（`\u00a0` 不换行空格标准化处理）。
- **设置与模型中心全覆盖**：翻译了 100% 的设置描述、模型余额面板、权限控制、快捷键功能表和问题反馈页面。

### ⚡ 纯原生零依赖内存注入 | Zero-Dependency In-Place Native Engine
- **无需安装 Node.js / Python**：Windows 端基于 .NET 内存级 ASAR 补丁引擎，**0.05 秒极速注入**，告别繁重的依赖安装。
- **100% 保留原生宿主文件**：不直接替换官方 `app.asar` 二进制文件，而是动态提取用户本机当前版本的 `preload.js` 追加注入，**永不产生版本冲突，完美兼容未来一切官方升级**。
- **全平台原生支持**：不仅支持 Windows 10/11，还同步支持 **macOS** 与 **Linux**。

### 🚀 全球 / 国内多 CDN 智能测速容灾 | Multi-CDN Fast Mirror Fallback
- **国内极速直连**：内置 Fastly jsDelivr、Cloudflare 镜像与 GitHub Raw 自动测速故障转移，无论身处何种网络环境，一键安装与字典拉取均稳定顺畅。
- **云端字典热同步**：启动时后台异步静默获取最新翻译词条并本地缓存，无需重新打补丁即可享受持续校对更新。

---

## 💾 快速安装指南 | Installation Guide

### 🪟 Windows 用户 | Windows Users

#### 方式 A：PowerShell 一键在线安装（推荐 ⭐⭐⭐）
以管理员身份打开 **PowerShell** 窗口，复制并运行以下命令（内置国内 CDN 加速，5 秒极速完成）：

```powershell
iwr -useb https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.ps1 | iex
```

*(备用 GitHub 官方源)*：
```powershell
iwr -useb https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/install.ps1 | iex
```

---

#### 方式 B：本地交互式管理面板 (Elite Toolkit v3.0)
1. 前往 [Releases](https://github.com/good9527/Antigravity-Chinese-Patch/releases) 页面下载最新压缩包。
2. 解压后**双击运行 `安装汉化补丁.bat`**。
3. 交互菜单支持：
   - `1` 🚀 **一键极速汉化 / 升级**
   - `2` 🛡️ **一键恢复官方原版备份**
   - `3` 🔍 **检查当前版本与汉化状态**
   - `4` 🚪 **退出管理面板**

---

### 🍎 macOS / 🐧 Linux 用户 | macOS & Linux Users

打开 Terminal 终端，运行以下一键安装命令：

```bash
curl -fsSL https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.sh | bash
```

---

## 📂 仓库结构 | Project Structure

```text
Antigravity-Chinese-Patch/
├── dist/
│   ├── preload.js          # 核心汉化引擎 (支持多 CDN 容灾热更新)
│   └── dictionary.json     # 云端共享 JSON 汉化词典
├── 安装汉化补丁.bat          # Windows 交互式一键批处理启动脚本
├── patch_antigravity.ps1   # Windows Elite Toolkit 控制台管理脚本
├── install.ps1             # Windows 零依赖一键在线安装核心脚本 (原生 .NET ASAR 引擎)
├── install.sh              # macOS / Linux 通用一键在线安装脚本 (原生 Python 引擎)
└── README.md               # 项目全平台使用说明文档
```

---

## ⚖️ 免责声明 | Disclaimer

- 本项目仅为个人学习及 Electron 运行时 DOM 注入技术的开源研究成果，不含任何商业用途。
- 汉化所涉及的界面文案版权归原软件官方所有。若您喜欢该软件，请支持官方正版。
- This project is purely for personal learning and open-source research on Electron DOM injection, without any commercial purpose. All product copyrights belong to their respective owners.
