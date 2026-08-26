"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Preload script — runs in every BrowserWindow before the page loads.
 * Exposes a minimal, secure API via contextBridge so the renderer can
 * communicate with the main-process auto-updater without nodeIntegration.
 */
const electron_1 = require("electron");
const updaterAPI = {
    onStateChanged: (callback) => {
        const handler = (_event, state) => {
            callback(state);
        };
        electron_1.ipcRenderer.on('updater:state-changed', handler);
        return () => {
            electron_1.ipcRenderer.removeListener('updater:state-changed', handler);
        };
    },
    checkForUpdates: () => electron_1.ipcRenderer.invoke('updater:check'),
    quitAndInstall: () => electron_1.ipcRenderer.invoke('updater:quit-and-install'),
    getUpdateChannel: () => electron_1.ipcRenderer.invoke('updater:get-channel'),
    setUpdateChannel: (channel) => electron_1.ipcRenderer.invoke('updater:set-channel', channel),
};
const ideAPI = {
    launch: (appPath, projectPath) => electron_1.ipcRenderer.invoke('ide:launch', appPath, projectPath),
    getAvailableApps: () => electron_1.ipcRenderer.invoke('ide:get-available-apps'),
    getDefaultIde: () => electron_1.ipcRenderer.invoke('ide:get-default-ide'),
    setDefaultIde: (bundleId) => electron_1.ipcRenderer.invoke('ide:set-default-ide', bundleId),
    installAgyCli: () => electron_1.ipcRenderer.invoke('ide:install-agy-cli'),
};
const electronNativeAPI = {
    getPlatform: () => process.platform,
    getDeepLink: () => electron_1.ipcRenderer.invoke('deep-link:get-stored'),
    onDeepLinkReceived: (callback) => {
        const handler = (_event, link) => {
            callback(link);
        };
        electron_1.ipcRenderer.on('deep-link:received', handler);
        return () => {
            electron_1.ipcRenderer.removeListener('deep-link:received', handler);
        };
    },
};
electron_1.contextBridge.exposeInMainWorld('updater', updaterAPI);
electron_1.contextBridge.exposeInMainWorld('electronNative', electronNativeAPI);
electron_1.contextBridge.exposeInMainWorld('ide', ideAPI);

// Antigravity Chinese Localization Patch
(function() {
  const dictionary = {
    "New Conversation": "新建对话",
    "Conversation History": "历史对话",
    "Scheduled Tasks": "计划任务",
    "Projects": "项目列表",
    "Conversations": "近期对话",
    "Settings": "设置",
    "Untitled Conversation": "未命名对话",
    "No conversations yet": "暂无对话",
    "See all": "查看全部",
    "Install IDE": "安装 IDE",
    "Close": "关闭",
    "Cancel": "取消",
    "Save": "保存",
    "Delete": "删除",
    "Rename": "重命名",
    "Ask anything, @ to mention, / for actions": "问我任何问题，用 @ 提及文件，用 / 执行动作",
    "Open": "打开",
    "Edit": "编辑",
    "Customize": "定制",
    "Account": "账户设置",
    "Permissions": "权限控制",
    "Appearance": "外观样式",
    "Customizations": "自定义功能",
    "Browser": "浏览器助手",
    "App": "客户端设置",
    "Not in Project": "非项目对话",
    "Provide Feedback": "提交反馈",
    "File": "文件",
    "View": "视图",
    "Window": "窗口",
    "Help": "帮助",
    "New Window": "新建窗口",
    "Create Project": "创建项目",
    "Command Palette": "命令面板",
    "Check for Updates": "检查更新",
    "Feedback Type": "反馈类型",
    "Bug Report": "缺陷报告",
    "Feature Request": "功能需求",
    "Auth and Billing": "账户与账单",
    "General Feedback": "常规反馈",
    "Description": "问题描述",
    "Steps to reproduce the issue": "重现步骤",
    "Expected behavior": "期望结果",
    "Actual behavior": "实际结果",
    "Any error messages": "错误提示信息",
    "Any relevant information": "其他相关信息",
    "Describe the bug you encountered...": "请详细描述您遇到的缺陷(Bug)...",
    "Steps to Reproduce": "重现步骤说明",
    "RECOMMENDED": "推荐快捷键",
    "NAVIGATION": "界面导航",
    "CONVERSATION": "对话交互",
    "Open Conversation Picker": "打开对话选择器",
    "Open File Search": "打开文件搜索",
    "Focus Input": "聚焦输入框",
    "Toggle History": "切换历史面板",
    "Toggle File Tree": "切换文件树",
    "Toggle Terminal": "切换终端窗口",
    "Toggle Artifacts": "切换产物面板",
    "New Task": "新建任务",
    "Open Settings": "打开设置",
    "Open Documentation": "打开官方文档",
    "Open Logs Folder": "打开日志目录",
    "Restart Language Server": "重启语言服务端",
    "About Antigravity": "关于 Antigravity",
    "Documentation": "官方文档",
    "Report an Issue": "报告问题",
    "Community Discord": "加入 Discord 社区",
    "Terms of Service": "服务条款",
    "Privacy Policy": "隐私政策",
    "Subagents": "子智能体",
    "Files Changed": "已修政文件",
    "Artifacts": "产物",
    "Uploads": "已上传文件",
    "Background Tasks": "后台任务",
    "MCP Error": "MCP 异常",
    "MCP Servers": "MCP 服务",
    "Installed MCP Servers": "已部署的 MCP 服务",
    "Recent Conversations": "近期对话",
    "Active Conversations": "活跃对话",
    "Archived Conversations": "归档对话",
    "Clear Conversations": "清除对话记录",
    "Delete Conversation": "删除对话",
    "Delete All Conversations": "删除所有对话",
    "Export Conversation": "导出对话",
    "Import Conversation": "导入对话",
    "Pin Conversation": "置顶对话",
    "Unpin Conversation": "取消置顶",
    "Collapse All": "全部折叠",
    "Expand All": "全部展开",
    "Review": "审核",
    "Accept": "接受",
    "Reject": "拒绝",
    "Accept Step": "接受步骤",
    "Reject Step": "拒绝步骤",
    "Action Required": "需要操作",
    "Add Custom Model": "添加自定义模型",
    "Add MCP Servers": "添加 MCP 服务",
    "Add Workspace": "添加工作区",
    "Add context": "添加上下文",
    "Add to Chat": "添加到对话",
    "Add to Chat/Quote": "添加到对话/引用",
    "All conversations": "全部对话",
    "All models": "全部模型",
    "Allow": "允许",
    "Deny": "拒绝",
    "Always Allow": "始终允许",
    "Always Deny": "始终拒绝",
    "Always Proceed": "始终继续",
    "Always Ask": "每次询问",
    "Ask before running": "运行前询问",
    "Apply Changes": "应用更改",
    "Discard Changes": "放弃更改",
    "Revert Changes": "撤销更改",
    "Review Changes": "审核更改",
    "Review my design": "审核我的设计",
    "Review this code": "审核此代码",
    "Thinking...": "思考中...",
    "Working...": "处理中...",
    "Agent finished": "智能体已完成",
    "Agent execution failed": "智能体执行失败",
    "Agent execution failed.": "智能体执行失败。",
    "Agent response": "智能体回复",
    "Agent Security Settings": "智能体安全设置",
    "Agent Team": "智能体协作团队",
    "Agent always asks for review.": "智能体将始终请求审核。",
    "Agent cannot modify files outside of the workspace in strict mode.": "在严格模式下，智能体无法修政工作区外的文件。",
    "Agent will always ask to review in strict mode.": "在严格模式下，智能体将始终请求审核。",
    "Agents have full access to your machine and external resources.": "智能体对您的计算机和外部资源拥有完全访问权限。",
    "A shell setup script run before every command the agent executes.": "在智能体执行每条命令前运行的 Shell 初始化脚本。",
    "Absolute path to the Chrome/Chromium executable": "Chrome/Chromium 可执行文件的绝对路径",
    "Agent Auto-Fix Lints": "智能体自动修复代码 Lint 错误",
    "Agent Non-Workspace File Access": "智能体工作区外文件访问权限",
    "Agent Script Command Configuration": "智能体脚本与命令配置",
    "Terminal Command Execution Policy": "终端命令执行策略",
    "Terminal Execution Policy": "终端执行策略",
    "File Access Policy": "文件访问策略",
    "Network Access Policy": "网络访问策略",
    "Allow commands outside sandbox": "允许在沙箱外部执行命令",
    "Requires confirmation for dangerous operations": "危险操作需要用户二次确认",
    "Read-only mode": "只读模式",
    "Read and Write": "读写模式",
    "Full Access": "完全访问",
    "Restricted Access": "受限访问",
    "Blocked by Policy": "已被安全策略拦截",
    "Selected Model": "当前选中模型",
    "Switch Model": "切换模型",
    "Select a model": "选择一个模型",
    "Model Parameters": "模型参数配置",
    "Temperature": "随机性 (Temperature)",
    "Top P": "采样阈值 (Top P)",
    "Max Tokens": "最大 Token 数量",
    "Quota Exceeded": "配额已用尽",
    "Credits Balance": "账户点数余额",
    "Daily Quota": "每日免费配额",
    "Monthly Quota": "每月配额",
    "Unlimited": "无限制",
    "Rate Limit Reached": "已达到速率限制",
    "Please try again later": "请稍后再试",
    "Your Plan: Google AI Ultra": "订阅计划：Google AI 旗舰版",
    "View your available model quota and AI credits. Model quota refreshes periodically based on your plan. Enable AI Credit Overages to continue using models when your quota is exhausted.": "查看您可用的模型配额和 AI 点数。模型配额会根据您的订阅计划定期重置。开启允许超出额度后扣除点数，可在配额耗尽后继续使用模型。",
    "Theme Mode": "配色主题模式",
    "Follow System Theme": "跟随系统主题",
    "Light Theme": "浅色主题",
    "Dark Theme": "深色主题",
    "High Contrast Theme": "高对比度主题",
    "Font Family": "界面字体",
    "Font Size": "字号大小",
    "Line Height": "行高",
    "Zoom Factor": "缩放比例",
    "Custom CSS": "自定义样式表 (CSS)",
    "Clear All": "清除全部",
    "Clear History": "清除历史记录",
    "Search": "搜索",
    "Copy": "复制",
    "Copied!": "已复制！",
    "Stop generating": "停止生成",
    "Regenerate": "重新生成",
    "Retry": "重试",
    "Advanced Settings": "高级设置",
    "Updates": "更新"
};

  const substringReplacements = [
    { search: 'Minimize', replace: '\u6700\u5c0f\u5316' },
    { search: 'Maximize', replace: '\u6700\u5927\u5316' },
    { search: 'Toggle Developer Tools', replace: '\u5207\u6362\u5f00\u53d1\u8005\u5de5\u5177' },
    { search: 'Default', replace: '\u9ed8\u8ba4' },
    { search: 'Full Machine', replace: '\u6574\u673a\u6388\u6743' },
    { search: 'Turbo Mode', replace: '\u6781\u901f\u6a21\u5f0f' },
    { search: 'Turbo mode', replace: '\u6781\u901f\u6a21\u5f0f' },
    { search: 'Custom', replace: '\u81ea\u5b9a\u4e49' },
    { search: 'System', replace: '\u8ddf\u968f\u7cfb\u7edf' }
  ];

  function normalize(str) {
    if (!str) return '';
    return str.replace(/\u00a0/g, ' ');
  }

  function translateText(text) {
    if (!text || typeof text !== 'string') return null;
    const normalized = normalize(text);
    const trimmed = normalized.trim();
    if (!trimmed) return null;

    // 1. Direct dictionary match
    if (dictionary[trimmed]) {
      return normalized.replace(trimmed, dictionary[trimmed]);
    }
    if (dictionary[normalized]) {
      return dictionary[normalized];
    }

    // 2. Pattern: Subagents N, Files Changed N, Artifacts N, Uploads N, Background Tasks N
    const paneMatch = trimmed.match(/^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks)\s+(\d+)$/i);
    if (paneMatch) {
      const typeMap = {
        'subagents': '\u5b50\u667a\u80fd\u4f53',
        'files changed': '\u5df2\u4fee\u653f\u6587\u4ef6',
        'artifacts': '\u4ea7\u7269',
        'uploads': '\u5df2\u4e0a\u4f20\u6587\u4ef6',
        'background tasks': '\u540e\u53f0\u4efb\u52a1'
      };
      const label = typeMap[paneMatch[1].toLowerCase()] || paneMatch[1];
      return normalized.replace(trimmed, `${label} ${paneMatch[2]}`);
    }

    // 3. Pattern: N files changed
    const filesChangedMatch = trimmed.match(/^(\d+)\s+files?\s+changed$/i);
    if (filesChangedMatch) {
      return normalized.replace(trimmed, `${filesChangedMatch[1]} \u4e2a\u6587\u4ef6\u5df2\u4fee\u653f`);
    }

    // 4. Pattern: Relative timestamps (5m, 23m, 10d, 1mo, 2mo)
    const timeMatch = trimmed.match(/^(\d+)\s*(mo|d|m|h|s|y)$/i);
    if (timeMatch) {
      const num = timeMatch[1];
      const unit = timeMatch[2].toLowerCase();
      const unitMap = {
        'mo': '\u4e2a\u6708\u524d',
        'd': '\u5929\u524d',
        'm': '\u5206\u949f\u524d',
        'h': '\u5c0f\u65f6\u524d',
        's': '\u79d2\u524d',
        'y': '\u5e74\u524d'
      };
      return normalized.replace(trimmed, `${num}${unitMap[unit]}`);
    }

    // 5. Pattern: Upload dates
    if (trimmed.startsWith('Today ')) {
      return normalized.replace('Today ', '\u4eca\u5929 ');
    }
    if (trimmed.startsWith('Yesterday ')) {
      return normalized.replace('Yesterday ', '\u6628\u5929 ');
    }

    // 6. Pattern: Thinking for Ns
    if (trimmed.startsWith('Thinking for ')) {
      const match = trimmed.match(/^Thinking\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i);
      if (match) {
        const num = match[1];
        const unit = match[2] || 's';
        const cnUnit = unit.toLowerCase().startsWith('ms') ? '\u6beb\u79d2' : '\u79d2';
        return normalized.replace(trimmed, `\u601d\u8003\u4e2d (${num}${cnUnit})`);
      }
    }

    // 7. Pattern: Working for Ns
    if (trimmed.startsWith('Working for ')) {
      const match = trimmed.match(/^Working\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i);
      if (match) {
        const num = match[1];
        const unit = match[2] || 's';
        const cnUnit = unit.toLowerCase().startsWith('ms') ? '\u6beb\u79d2' : '\u79d2';
        return normalized.replace(trimmed, `\u5904\u7406\u4e2d (${num}${cnUnit})`);
      }
    }

    // 8. Pattern: Completed/Finished/Done in Ns
    if (trimmed.startsWith('Completed in ') || trimmed.startsWith('Finished in ') || trimmed.startsWith('Done in ')) {
      const match = trimmed.match(/^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i);
      if (match) {
        const num = match[2];
        const unit = match[3] || 's';
        const cnUnit = unit.toLowerCase().startsWith('ms') ? '\u6beb\u79d2' : '\u79d2';
        return normalized.replace(trimmed, `\u5df2\u5b8c\u6210 (\u8017\u65f6 ${num}${cnUnit})`);
      }
    }

    // 9. Substring replacements
    let newText = normalized;
    let modified = false;
    for (const item of substringReplacements) {
      if (newText.includes(item.search)) {
        newText = newText.replaceAll(item.search, item.replace);
        modified = true;
      }
    }
    if (modified) return newText;

    return null;
  }

  function walk(node) {
    if (!node) return;
    if (node.nodeType === 3) {
      const text = node.nodeValue;
      const trans = translateText(text);
      if (trans !== null && trans !== text) {
        node.nodeValue = trans;
      }
    } else if (node.nodeType === 1) {
      const tag = node.tagName ? node.tagName.toLowerCase() : '';
      if (tag === 'script' || tag === 'style' || tag === 'noscript' || tag === 'textarea') {
        return;
      }

      ['placeholder', 'title', 'aria-label', 'value'].forEach(attr => {
        if (node.hasAttribute && node.hasAttribute(attr)) {
          const val = node.getAttribute(attr);
          const trans = translateText(val);
          if (trans !== null && trans !== val) {
            node.setAttribute(attr, trans);
          }
        }
      });

      for (let child = node.firstChild; child; child = child.nextSibling) {
        walk(child);
      }
    }
  }

  let observer = null;
  function startObserver() {
    if (observer) return;
    observer = new MutationObserver(mutations => {
      for (const m of mutations) {
        if (m.type === 'childList') {
          for (let i = 0; i < m.addedNodes.length; i++) {
            walk(m.addedNodes[i]);
          }
        } else if (m.type === 'characterData') {
          const node = m.target;
          const trans = translateText(node.nodeValue);
          if (trans !== null && trans !== node.nodeValue) {
            node.nodeValue = trans;
          }
        } else if (m.type === 'attributes') {
          const el = m.target;
          const attr = m.attributeName;
          if (el.getAttribute) {
            const val = el.getAttribute(attr);
            const trans = translateText(val);
            if (trans !== null && trans !== val) {
              el.setAttribute(attr, trans);
            }
          }
        }
      }
    });

    if (document.body) {
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true,
        attributes: true,
        attributeFilter: ['placeholder', 'title', 'aria-label', 'value']
      });
    }
  }

  // Hook into DOM loading
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      walk(document.body);
      startObserver();
    });
  } else {
    walk(document.body);
    startObserver();
  }
})();
