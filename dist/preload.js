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
        // Return unsubscribe function
        return () => {
            electron_1.ipcRenderer.removeListener('updater:state-changed', handler);
        };
    },
    applyUpdate: () => electron_1.ipcRenderer.invoke('updater:apply'),
    quitAndInstall: () => electron_1.ipcRenderer.invoke('updater:quit-and-install'),
    checkForUpdates: () => electron_1.ipcRenderer.invoke('updater:check-for-updates'),
};
const dialogAPI = {
    showOpenDialog: () => electron_1.ipcRenderer.invoke('dialog:open-workspace'),
};
const notificationAPI = {
    send: (options) => electron_1.ipcRenderer.invoke('notification:send', options),
    openSystemPreferences: () => electron_1.ipcRenderer.invoke('notification:open-system-preferences'),
    onClicked: (callback) => {
        const handler = (_event, payload) => {
            callback(payload);
        };
        electron_1.ipcRenderer.on('notification:clicked', handler);
        return () => {
            electron_1.ipcRenderer.removeListener('notification:clicked', handler);
        };
    },
};
const storageAPI = {
    getItems: () => electron_1.ipcRenderer.invoke('storage:get-items'),
    updateItems: (changes) => electron_1.ipcRenderer.invoke('storage:update-items', changes),
    onChanged: (callback) => {
        const handler = (_event, changes) => {
            callback(changes);
        };
        electron_1.ipcRenderer.on('storage:changed', handler);
        return () => {
            electron_1.ipcRenderer.removeListener('storage:changed', handler);
        };
    },
};
const logsAPI = {
    getElectronLogs: () => electron_1.ipcRenderer.invoke('logs:electron'),
};
const extensionsAPI = {
    sendAuthorities: (authoritiesMap) => electron_1.ipcRenderer.invoke('extensions:send-authorities', authoritiesMap),
};
const deepLinkAPI = {
    onDeepLink: (callback) => {
        const handler = (_event, url) => {
            callback(url);
        };
        electron_1.ipcRenderer.on('deep-link', handler);
        return () => {
            electron_1.ipcRenderer.removeListener('deep-link', handler);
        };
    },
    getStoredDeepLink: () => electron_1.ipcRenderer.invoke('deep-link:get-stored'),
};
const agentAPI = {
    updateActiveAgentCount: (count) => electron_1.ipcRenderer.invoke('agent:update-active-count', count),
};
const electronNativeAPI = {
    getZoomLevel: () => electron_1.webFrame.getZoomFactor(),
    setTitleBarOverlay: (options) => electron_1.ipcRenderer.invoke('window:set-title-bar-overlay', options),
    minimize: () => electron_1.ipcRenderer.invoke('window:minimize'),
    maximize: () => electron_1.ipcRenderer.invoke('window:maximize'),
    unmaximize: () => electron_1.ipcRenderer.invoke('window:unmaximize'),
    isMaximized: () => electron_1.ipcRenderer.invoke('window:is-maximized'),
    close: () => electron_1.ipcRenderer.invoke('window:close'),
    toggleDevTools: () => electron_1.ipcRenderer.invoke('window:toggle-devtools'),
    zoomIn: () => {
        const current = electron_1.webFrame.getZoomLevel();
        electron_1.webFrame.setZoomLevel(current + 0.5);
    },
    zoomOut: () => {
        const current = electron_1.webFrame.getZoomLevel();
        electron_1.webFrame.setZoomLevel(current - 0.5);
    },
    resetZoom: () => {
        electron_1.webFrame.setZoomLevel(0);
    },
    openExternal: (url) => electron_1.ipcRenderer.invoke('shell:open-external', url),
};
const ideAPI = {
    isInstalled: () => electron_1.ipcRenderer.invoke('ide:is-installed'),
};
electron_1.contextBridge.exposeInMainWorld('electronUpdater', updaterAPI);
electron_1.contextBridge.exposeInMainWorld('dialog', dialogAPI);
electron_1.contextBridge.exposeInMainWorld('nativeNotifications', notificationAPI);
electron_1.contextBridge.exposeInMainWorld('nativeStorage', storageAPI);
electron_1.contextBridge.exposeInMainWorld('logs', logsAPI);
electron_1.contextBridge.exposeInMainWorld('extensions', extensionsAPI);
electron_1.contextBridge.exposeInMainWorld('deepLink', deepLinkAPI);
electron_1.contextBridge.exposeInMainWorld('agent', agentAPI);
electron_1.contextBridge.exposeInMainWorld('electronNative', electronNativeAPI);
electron_1.contextBridge.exposeInMainWorld('ide', ideAPI);

// Antigravity Chinese Localization Patch
(function() {
  const dictionary = {
    'New Conversation': '新建对话',
    'Conversation History': '历史对话',
    'Scheduled Tasks': '计划任务',
    'Projects': '项目列表',
    'Conversations': '近期对话',
    'Settings': '设置',
    'Untitled Conversation': '无标题对话',
    'No conversations yet': '暂无对话',
    'See all': '查看全部',
    'Install IDE': '安装 IDE',
    'Close': '关闭',
    'Cancel': '取消',
    'Save': '保存',
    'Delete': '删除',
    'Rename': '重命名',
    'Ask anything, @ to mention, / for actions': '问我任何问题，用 @ 提及文件，用 / 执行动作',
    'Open': '打开',
    'Edit': '编辑',
    'Customize': '定制',
    
    // Sidebar items
    'Account': '账户设置',
    'Permissions': '权限控制',
    'Appearance': '外观样式',
    'Customizations': '自定义功能',
    'Browser': '浏览器助手',
    'App': '客户端设置',
    'Not in Project': '非项目对话',
    'Provide Feedback': '提交反馈',
    '模型列表': '模型列表',
    '通用设置': '通用设置',
    '项目列表': '项目列表',
    '近期对话': '近期对话',
    '快捷键': '快捷键',
    
    // Top Menus (DOM fallback)
    'File': '文件',
    'View': '视图',
    'Window': '窗口',
    'Help': '帮助',
    'New Window': '新建窗口',
    'Create Project': '创建项目',
    'Command Palette': '命令面板',
    'Check for Updates': '检查更新',
    
    // Feedback Page
    'Feedback Type': '反馈类型',
    'Bug Report': '缺陷报告',
    'Feature Request': '功能需求',
    'Auth and Billing': '账户与账单',
    'General Feedback': '常规反馈',
    'Description': '问题描述',
    'Steps to reproduce the issue': '重现步骤',
    'Expected behavior': '预期结果',
    'Actual behavior': '实际结果',
    'Any error messages': '错误提示信息',
    'Any relevant information': '其他相关信息',
    'Describe the bug you encountered...': '请详细描述您遇到的缺陷(Bug)...',
    'Steps to Reproduce': '重现步骤说明',
    
    // Shortcuts Page
    'RECOMMENDED': '推荐快捷键',
    'NAVIGATION': '界面导航',
    'CONVERSATION': '对话交互',
    'Open Conversation Picker': '打开对话选择器',
    'Open File Search': '打开文件搜索',
    'Focus Input': '聚焦输入框',
    'Go Back': '后退',
    'Go Forward': '前进',
    'File Picker': '打开文件选择器',
    'Select Previous Conversation': '选择上一个对话',
    'Select Next Conversation': '选择下一个对话',
    'Open Settings': '打开设置中心',
    
    // Recent Conversations & Permissions Page
    'Agent Settings': '智能体设置',
    'Security Preset': '安全预设等级',
    'Turbo Mode': '极速模式',
    'Agent Behavior': '智能体动作行为',
    'Artifact Review Policy': '产物审核机制',
    'Always Proceed': '始终继续 (不提示)',
    'Always Ask': '每次均询问',
    'Local Permissions': '本地工作区授权',
    'global settings': '全局设置',
    'File Access Rules': '文件系统读写规则',
    'Network Access Rules': '网络请求访问规则',
    'Terminal Commands': '终端指令执行规则',
    'Commands Outside Sandbox': '沙箱外执行命令',
    'MCP Tools': 'MCP 外部工具扩展',
    
    // Project Settings Page
    'Folders': '项目文件夹',
    '+ Add Folder': '+ 添加文件夹',
    
    // App Settings Page
    'App Settings': '客户端应用设置',
    'Prevent Sleep': '阻止系统自动休眠',
    'Keep In Menu Bar': '最小化至菜单栏(常驻后台)',
    'Notifications': '系统通知提醒',
    'Notification Settings': '应用通知设置',
    'Open System Preferences': '打开系统偏好设置',
    
    // Browser Settings Page
    'Browser Settings': '浏览器自动化设置',
    'Browser Javascript Execution Policy': '浏览器 JavaScript 脚本执行策略',
    'Actuation Permissions': '自动化执行授权',
    'Browser Actuation Rules': '浏览器网页操作规则',
    
    // Customizations Page
    'Token Usage': 'Token 消耗额度分析',
    'Installed MCP Servers': '已部署的 MCP 服务列表',
    'Add MCP +': '+ 部署 MCP 服务',
    'Refresh': '刷新列表',
    'No MCP Servers': '暂无 MCP 服务',
    'Build With Google Plugins': '基于 Google 官方插件构建',
    
    // Models Page
    'Model Credits': 'AI 模型点数余额',
    'Enable AI Credit Overages': '允许超出额度后扣除点数',
    'See Activity': '查看消费明细',
    'Get More AI Credits': '充值/获取更多点数',
    'Model Quota': '免费模型使用配额',
    
    // Appearance Page
    'Chat Settings': '聊天窗口偏好',
    'Verbose agent chat': '展示智能体完整思考步骤',
    'Preset': '预设主题色',
    'Default Light': '默认浅色',
    'Default Dark': '默认深色',
    'Background': '背景底色',
    'Foreground': '前景文字字色',
    'Accent': '全局强调色',
    'Dark Theme': '深色模式配色',
    
    // Permissions Summary Page
    'Project-Specific Settings': '项目特定权限配置',
    'Go To Projects': '前往项目管理中心',
    'File Permissions': '文件系统访问权限',
    'Network Permissions': '网络请求权限',
    'Terminal & Tooling Permissions': '系统终端与调试工具授权',
    
    // Account Page
    'Marketing Emails': '接收产品推广与技术周报',
    'Upgrade': '订阅升级',
    'Sign Out': '退出当前账户',
    'Terms of Service': '服务条款说明',
    'Email': '邮箱账号',
    
    // Context @ menu
    'Add Context': '添加上下文',
    'Media': '媒体文件 (图片/视频)',
    'Mentions': '提及项 (@ 符号)',
    'Actions': '动作指令 (/ 符号)',
    
    // Toggles and Options
    'Minimize': '最小化',
    'Maximize': '最大化',
    'Toggle Developer Tools': '切换开发者工具',
    
    // Safety Presets Specific
    'Default': '默认',
    'Full Machine': '整机授权',
    'Custom': '自定义',
    'Danger Zone': '危险区域',
    'Delete Project': '删除项目',
    'Requires manual review for all terminal commands and file accesses outside of the working folders': '对工作区外的所有终端命令和文件访问均需要手动审核',
    'All terminal commands require review. The agent can read or write to any file in the machine': '所有终端命令都需要审核。智能体可以读取或写入系统中的任何文件',
    'Disables all safety barriers for maximal iteration velocity': '禁用所有安全屏障以换取最大迭代速度',
    'Permanently delete this project and all of its conversations': '永久删除此项目及其所有的对话记录',
    
    // Fragment translations (for HTML inline links)
    'Inherits from': '继承自',
    'Local permissions have higher priority': '本地权限具有更高优先级',
    'Learn more': '了解更多',
    '. Local permissions have higher priority': '。本地权限具有更高优先级',
    'Learn more about ': '了解更多关于 ',
    'Learn more about': '了解更多关于',
    'Turbo mode': '极速模式',
    'Turbo Mode': '极速模式',
    
    // Theme options
    'System': '跟随系统',
    'Light': '浅色',
    'Dark': '深色',

    // Feedback specifics
    'Attach a screenshot (optional)': '添加截图 (可选)',
    'Attach Antigravity server logs': '附带 Antigravity 服务端日志',
    'Submit': '提交',
    'Please list the steps to reproduce the issue': '请列出重现此问题的步骤',
    'Please describe the issue in detail. The more actionable your feedback, the quicker our team can address your request. Some helpful information includes': '请详细描述您遇到的问题。您的反馈越具体，我们的团队就能越快地处理您的请求。一些有帮助的信息包括',
    
    // Additional UI elements
    'Search conversations...': '搜索对话...',
    'Filter': '筛选',
    'Enable Telemetry': '允许收集匿名使用数据',
    'Manually customize individual settings.': '手动配置具体的权限规则。',
    
    // Agent status indicators
    'Working..': '正在处理..',
    'Working...': '正在处理...',
    'Working': '正在处理',
    'Thinking..': '正在思考..',
    'Thinking...': '正在思考...',
    'Thinking': '正在思考',
    'Analyzing..': '正在分析..',
    'Analyzing...': '正在分析...',
    'Analyzing': '正在分析',
    
    // Agent Action Logs & Buttons
    'Review': '审核',
    'Schedule timer: Timer has expired': '调度定时器：定时器已过期',
    'Repack app.asar finished': '打包 app.asar 已完成',

    // Sidebar exact matches
    'General': '通用设置',
    'Models': '模型列表',
    'Shortcuts': '快捷键',

    // Safety Presets & Descriptions
    'Agent settings and permissions for conversations outside of projects': '项目外部对话的智能体设置 and 权限',
    'Choose a predefined security preset for the agent. This controls terminal auto-execution policy, and file access policy': '为智能体选择预设的安全级别。这控制了终端命令自动执行策略和文件访问策略',
    'Learn more about Turbo mode': '了解关于 Turbo 极速模式的详情',
    'Specifies Agent\'s behavior when asking for review on artifacts, which are documents it creates to enable a richer conversation experience': '指定智能体在请求审核其创建的产物（即为了提供更丰富对话体验而生成的文档）时的动作行为',
    'Inherits from global settings. Local permissions have higher priority. Learn more': '继承自全局设置。工作区本地权限具有更高的优先级。了解更多',
    'Configure allowed and denied paths for file reads and writes': '配置允许和拒绝的文件读取及写入路径',
    'Configure allowed and denied URLs for reading': '配置允许和拒绝访问的网络链接 (URL)',
    'Configure allowed terminal commands': '配置允许在系统终端执行的命令白名单',
    'Configure allowed commands outside the sandbox': '配置允许在沙箱环境外部直接执行的系统命令',
    'Manage project folders, agent settings, and permissions': '管理当前工作区的项目文件夹、智能体设定以及访问控制权限',
    'Manage application settings': '管理本客户端应用程序的全局基础设置',
    'Prevent the computer from sleeping while the app is running': '阻止计算机在 Antigravity 应用运行期间自动进入系统睡眠状态',
    'The app will be accessible from the menu bar and will keep running in the background when all windows are closed': '关闭所有窗口后，应用仍可通过顶部菜单栏/系统托盘进行访问，并在系统后台静默运行',
    'To modify notification settings, open your operating system\'s system preferences': '若需自定义修改应用通知设置，请打开您计算机操作系统的系统首选项进行调整',
    'Configure the browser subagent. It requires Google Chrome to be installed. The browser subagent can be invoked by typing /browser in the conversation input box': '配置浏览器子智能体服务（需要安装 Google Chrome 浏览器）。在聊天窗口中输入 /browser 即可召唤浏览器助手',
    'Controls whether the agent can run custom JavaScript to automate complex browser actions': '控制智能体是否可以通过执行自定义的 JavaScript 脚本来自动化处理复杂的网页浏览操作',
    'Configure allowed and denied URLs for browser actuation': '配置允许和拒绝浏览器助手进行模拟网页交互的网址(URL)规则',
    'Configure default behaviors, skills, and MCP servers. Learn more': '统一配置智能体的默认动作行为、专属技能以及 Model Context Protocol (MCP) 服务器。点击了解更多',
    'The breakdown below shows token usage from customizations like skills, rules, and MCP. If the budget is exceeded, large customizations will be truncated automatically': '下方表格展示了自定义技能、规则库以及 MCP 等扩展功能的 Token 消耗明细。若超出限额，较长的自定义内容会被底层截断',
    'No customizations found for this workspace': '当前工作区尚未发现任何自定义技能、规则或服务器设置',
    'You currently don\'t have any MCP Servers installed. Add an MCP server above': '您当前尚未部署任何 MCP 服务器。请通过上方的按钮添加一个 MCP 服务',
    'Configure AI models and view your quota': '在此处配置您专属的 AI 语言模型，并实时查询各模型的配额余量',
    'When toggled on, Antigravity will use your AI credits to fulfill model requests once you\'re out of model quota. Antigravity will always use your model quota first before using AI credits': '开启此开关后，若您的每日免费额度耗尽，Antigravity 将使用您的付费 AI 账户点数继续处理请求。系统会始终优先消耗您的每日免费配额',
    'Configure the agent\'s visual theme and display preferences': '配置智能体的整体视觉配色主题与窗口显示偏好',
    'Display and preserve intermediate thinking steps': '在聊天界面实时渲染并保留智能体在执行任务时的完整思考过程 (Thinking Steps)',
    'Select light, dark, or inherit system settings': '选择明亮主题、深色主题，或直接同步您操作系统的双色外观',
    'Configure global allowed and denied resource permissions. Learn more': '配置系统全局允许或禁止的硬件及软件资源访问权限。点击了解更多',
    'Modify scoped permissions, folders, and agent settings like Sandbox and Terminal Command Execution': '全局配置特定工作区的独立授权、挂载文件夹，以及命令沙箱执行等高阶环境设定',
    'Configure external tools via Model Context Protocol': '通过业内通用的 Model Context Protocol (MCP) 统一配置和扩展外部调试工具',
    'Manage your plan, credentials, and general preferences': '便捷管理您的账户订阅计划、安全凭证以及全局通用系统偏好',
    'When toggled on, Antigravity collects usage data to help Google enhance performance and features': '开启此选项后，Antigravity 将收集部分匿名使用数据，以帮助 Google 持续优化大模型性能与客户端交互功能',
    'Receive product updates, tips, and promotions from Google Antigravity via email': '允许通过电子邮箱定期接收来自 Google Antigravity 的产品迭代动态、使用技巧以及活动信息',
    'You can upgrade to a Google AI Ultra plan to receive the highest rate limits': '您可以随时升级至 Google AI 旗舰版 (Ultra Plan) 以获取极速响应和无限制的配额限流额度',
    'By using this app, you agree to its Terms of Service': '继续使用本客户端应用程序，即代表您完全知晓并同意其用户服务协议与隐私条款',
    'Keyboard shortcuts for quick navigation and control': '使用精心设计的键盘快捷键来快速导航、切换窗口并控制智能体的高频操作',
    'Toggle Model Selector': '切换模型选择器',
    'Toggle Voice Recording': '开启/关闭语音录制',
    'Find in Pane': '在窗格中查找',
    'LAYOUT CONTROLS': '布局控制',
    'Toggle Sidebar': '开启/关闭侧边栏',
    'Toggle Auxiliary Pane': '开启/关闭辅助窗格',
    'Zoom In': '放大',
    'Zoom Out': '缩小',
    'Reset Zoom': '重置缩放',
    'Go To Projects': '前往项目管理中心',
    'By using this app, you agree to its': '继续使用本客户端应用程序，即代表您同意其',
    'Your Plan: Google AI Pro': '订阅计划：Google AI 专业版',
    'Your Plan: Google AI Ultra': '订阅计划：Google AI 旗舰版',
    'Configure global allowed and denied resource permissions.': '配置全局允许和拒绝的资源权限。',
    'Configure default behaviors, skills, and MCP servers.': '配置默认行为、技能和 MCP 服务。',
    'Configure the browser subagent. It requires': '配置浏览器子智能体。运行此功能需要安装',
    'to be installed. The browser subagent can be invoked by typing /browser in the conversation input box.': '。您可以在输入框中输入 /browser 来召唤浏览器助手。',
    'View your available model quota and AI credits. Model quota refreshes periodically based on your plan. Enable AI Credit Overages to continue using models when your quota is exhausted.': '查看您可用的模型配额和 AI 点数。模型配额会根据您的订阅计划定期重置。开启允许超出额度后扣除点数，可在配额耗尽后继续使用模型。',
    'Light Theme': '浅色主题',
    'Dark Theme': '深色主题',
    'Clear All': '清除全部',
    'Clear History': '清除历史记录',
    'Search': '搜索',
    'Copy': '复制',
    'Copied!': '已复制！',
    'Stop generating': '停止生成',
    'Regenerate': '重新生成',
    'Retry': '重试',
    'Advanced Settings': '高级设置',
    'Updates': '更新'
  };

  const substringReplacements = [
    // Toggles & Presets
    { search: 'Minimize', replace: '最小化' },
    { search: 'Maximize', replace: '最大化' },
    { search: 'Toggle Developer Tools', replace: '切换开发者工具' },
    { search: 'Default', replace: '默认' },
    { search: 'Full Machine', replace: '整机授权' },
    { search: 'Turbo Mode', replace: '极速模式' },
    { search: 'Turbo mode', replace: '极速模式' },
    { search: 'Custom', replace: '自定义' },
    { search: 'System', replace: '跟随系统' },
    { search: 'Learn more about ', replace: '了解更多关于 ' },
    { search: 'Learn more about', replace: '了解更多关于' },
    { search: 'Enable Telemetry', replace: '允许收集匿名使用数据' },
    { search: 'Manually customize individual settings.', replace: '手动配置具体的权限规则。' },
    { search: 'Working..', replace: '正在处理..' },
    { search: 'Working...', replace: '正在处理...' },
    { search: 'Working.', replace: '正在处理...' },
    { search: 'Thinking..', replace: '正在思考..' },
    { search: 'Thinking...', replace: '正在思考...' },
    { search: 'Analyzing..', replace: '正在分析..' },
    { search: 'Analyzing...', replace: '正在分析...' },
    
    // Danger Zone
    { search: 'Danger Zone', replace: '危险区域' },
    { search: 'Delete Project', replace: '删除项目' },
    { search: 'Permanently delete this project and all of its conversations', replace: '永久删除此项目及其所有的对话记录' },
    
    // Autocomplete fallback
    { search: 'Add Context', replace: '添加上下文' },
    { search: 'Media', replace: '媒体文件 (图片/视频)' },
    { search: 'Mentions', replace: '提及项 (@ 符号)' },
    { search: 'Actions', replace: '动作指令 (/ 符号)' },
    
    // Shortcuts page fallback
    { search: 'Toggle Model Selector', replace: '切换模型选择器' },
    { search: 'Toggle Voice Recording', replace: '开启/关闭语音录制' },
    { search: 'Find in Pane', replace: '在窗格中查找' },
    { search: 'LAYOUT CONTROLS', replace: '布局控制' },
    { search: 'Toggle Sidebar', replace: '开启/关闭侧边栏' },
    { search: 'Toggle Auxiliary Pane', replace: '开启/关闭辅助窗格' },
    { search: 'Zoom In', replace: '放大' },
    { search: 'Zoom Out', replace: '缩小' },
    { search: 'Reset Zoom', replace: '重置缩放' },
    { search: 'Go To Projects', replace: '前往项目管理中心' },
    { search: 'Light Theme', replace: '浅色主题' },
    { search: 'Dark Theme', replace: '深色主题' }
  ];

  const punctuationMap = {
    '.': '。',
    ':': '：',
    '?': '？',
    '!': '！',
    ',': '，'
  };

  function translateText(text) {
    if (!text) return null;
    // Normalize non-breaking spaces (React select elements / options often use \u00a0)
    let normalized = text.replaceAll('\u00a0', ' ');
    const trimmed = normalized.trim();
    if (!trimmed) return null;
    
    // 1. Exact Match
    if (dictionary[trimmed]) {
      return normalized.replace(trimmed, dictionary[trimmed]);
    }
    
    // 2. Exact Match with stripped trailing punctuation
    let core = trimmed;
    let suffix = '';
    const lastChar = trimmed[trimmed.length - 1];
    if (punctuationMap[lastChar]) {
      core = trimmed.slice(0, -1).trim();
      suffix = punctuationMap[lastChar];
      if (dictionary[core]) {
        return normalized.replace(trimmed, dictionary[core] + suffix);
      }
    }
    
    // 3. Pattern: See all (12)
    if (trimmed.startsWith('See all (')) {
      const match = trimmed.match(/See all \((\d+)\)/);
      if (match) {
        return normalized.replace(trimmed, `查看全部 (${match[1]})`);
      }
    }
    
    // 4. Pattern: Refreshes in N hours, M minutes
    if (trimmed.startsWith('Refreshes in ')) {
      let newText = trimmed;
      newText = newText.replace('Refreshes in', '额度重置倒计时：');
      newText = newText.replace('hours', '小时');
      newText = newText.replace('minutes', '浅色' === '' ? '分钟' : '分钟'); // dummy to keep simple replace
      newText = newText.replace('minutes', '分钟');
      newText = newText.replace('hour', '小时');
      newText = newText.replace('minute', '分钟');
      newText = newText.replaceAll(', ', ' '); // Remove comma for natural Chinese reading
      return normalized.replace(trimmed, newText);
    }

    // 5. Pattern: Your Plan
    if (trimmed.startsWith('Your Plan: ')) {
      return normalized.replace(trimmed, trimmed.replace('Your Plan: ', '订阅计划：').replace('Google AI Pro', 'Google AI 专业版').replace('Google AI Ultra', 'Google AI 旗舰版'));
    }

    // 6. Pattern: Available AI Credits
    if (trimmed.startsWith('Available AI Credits: ')) {
      return normalized.replace(trimmed, trimmed.replace('Available AI Credits: ', '可用 AI 点数余额: '));
    }

    // 7. Pattern: Token budget
    if (trimmed.includes('of the customization budget is available.')) {
      return normalized.replace(trimmed, trimmed.replace('of the customization budget is available.', '的自定义 Token 预算当前可用。'));
    }

    // 8. Pattern: Version X.Y.Z
    if (trimmed.startsWith('Version ')) {
      return normalized.replace(trimmed, trimmed.replace('Version ', '版本 '));
    }

    // 9. Pattern: Send feedback as email
    if (trimmed.startsWith('Send feedback as ')) {
      return normalized.replace(trimmed, trimmed.replace('Send feedback as ', '以 ').concat(' 的身份发送反馈'));
    }

    // 10. Pattern: Explored N files/tasks
    if (trimmed.startsWith('Explored ')) {
      const fileMatch = trimmed.match(/^Explored\s+(\d+)\s+files?$/i);
      if (fileMatch) return normalized.replace(trimmed, `已探索 ${fileMatch[1]} 个文件`);
      const taskMatch = trimmed.match(/^Explored\s+(\d+)\s+tasks?$/i);
      if (taskMatch) return normalized.replace(trimmed, `已探索 ${taskMatch[1]} 个任务`);
    }

    // 11. Pattern: Edited N files
    if (trimmed.startsWith('Edited ')) {
      const fileMatch = trimmed.match(/^Edited\s+(\d+)\s+files?$/i);
      if (fileMatch) return normalized.replace(trimmed, `已编辑 ${fileMatch[1]} 个文件`);
    }

    // 12. Pattern: Timed N seconds
    if (trimmed.startsWith('Timed ')) {
      const secMatch = trimmed.match(/^Timed\s+(\d+)\s+seconds?$/i);
      if (secMatch) return normalized.replace(trimmed, `已计时 ${secMatch[1]} 秒`);
    }

    // 13. Pattern: Thinking for Ns (dynamic thinking states)
    if (trimmed.startsWith('Thinking for ')) {
      const match = trimmed.match(/^Thinking\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i);
      if (match) {
        const num = match[1];
        const unit = match[2] || 's';
        let cnUnit = '秒';
        if (unit.toLowerCase().startsWith('ms')) {
          cnUnit = '毫秒';
        }
        return normalized.replace(trimmed, `思考中 (${num}${cnUnit})`);
      }
    }

    // 14. Pattern: Working for Ns (dynamic working states)
    if (trimmed.startsWith('Working for ')) {
      const match = trimmed.match(/^Working\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i);
      if (match) {
        const num = match[1];
        const unit = match[2] || 's';
        let cnUnit = '秒';
        if (unit.toLowerCase().startsWith('ms')) {
          cnUnit = '毫秒';
        }
        return normalized.replace(trimmed, `处理中 (${num}${cnUnit})`);
      }
    }

    // 15. Pattern: Completed/Finished/Done in Ns
    if (trimmed.startsWith('Completed in ') || trimmed.startsWith('Finished in ') || trimmed.startsWith('Done in ')) {
      const match = trimmed.match(/^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i);
      if (match) {
        const num = match[2];
        const unit = match[3] || 's';
        let cnUnit = '秒';
        if (unit.toLowerCase().startsWith('ms')) {
          cnUnit = '毫秒';
        }
        return normalized.replace(trimmed, `已完成 (耗时 ${num}${cnUnit})`);
      }
    }

    // 16. Pattern: Generated image in Ns
    if (trimmed.startsWith('Generated image in ')) {
      const match = trimmed.match(/^Generated\s+image\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i);
      if (match) {
        const num = match[1];
        const unit = match[2] || 's';
        let cnUnit = '秒';
        if (unit.toLowerCase().startsWith('ms')) {
          cnUnit = '毫秒';
        }
        return normalized.replace(trimmed, `已生成图片 (耗时 ${num}${cnUnit})`);
      }
    }

    // 17. Substring translation for complex descriptions
    let newText = normalized;
    let modified = false;
    for (const item of substringReplacements) {
      if (newText.includes(item.search)) {
        newText = newText.replaceAll(item.search, item.replace);
        modified = true;
      }
    }
    if (modified) {
      return newText;
    }
    
    return null;
  }

  function walk(node) {
    if (!node) return;
    if (node.nodeType === 3) { // Node.TEXT_NODE
      const translated = translateText(node.nodeValue);
      if (translated !== null) {
        node.nodeValue = translated;
      }
    } else if (node.nodeType === 1) { // Node.ELEMENT_NODE
      if (node.placeholder) {
        const translated = translateText(node.placeholder);
        if (translated !== null) {
          node.placeholder = translated;
        }
      }
      if (node.tagName === 'INPUT' && (node.type === 'button' || node.type === 'submit')) {
        const translated = translateText(node.value);
        if (translated !== null) {
          node.value = translated;
        }
      }
      // Support Shadow DOM traversal
      if (node.shadowRoot) {
        walk(node.shadowRoot);
      }
      for (let child = node.firstChild; child; child = child.nextSibling) {
        walk(child);
      }
    } else if (node.nodeType === 11) { // Node.DOCUMENT_FRAGMENT_NODE (e.g. ShadowRoot)
      for (let child = node.firstChild; child; child = child.nextSibling) {
        walk(child);
      }
    }
  }

  const observer = new MutationObserver((mutations) => {
    observer.disconnect();
    for (const mutation of mutations) {
      if (mutation.type === 'childList') {
        for (const addedNode of mutation.addedNodes) {
          walk(addedNode);
        }
      } else if (mutation.type === 'characterData') {
        const translated = translateText(mutation.target.nodeValue);
        if (translated !== null) {
          mutation.target.nodeValue = translated;
        }
      } else if (mutation.type === 'attributes') {
        const target = mutation.target;
        if (mutation.attributeName === 'placeholder' && target.placeholder) {
          const translated = translateText(target.placeholder);
          if (translated !== null) {
            target.placeholder = translated;
          }
        }
      }
    }
    startObserver();
  });

  function startObserver() {
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['placeholder', 'value']
    });
  }

  // Hook Title Changes
  try {
    const originalTitleDescriptor = Object.getOwnPropertyDescriptor(Document.prototype, 'title');
    if (originalTitleDescriptor && originalTitleDescriptor.set) {
      Object.defineProperty(document, 'title', {
        get: function() {
          return originalTitleDescriptor.get.call(this);
        },
        set: function(val) {
          if (!val) {
            originalTitleDescriptor.set.call(this, val);
            return;
          }
          const trimmed = val.trim();
          let translated = val;
          if (dictionary[trimmed]) {
            translated = val.replace(trimmed, dictionary[trimmed]);
          } else if (trimmed.includes(' - Antigravity')) {
            const part = trimmed.replace(' - Antigravity', '').trim();
            if (dictionary[part]) {
              translated = `${dictionary[part]} - Antigravity`;
            }
          }
          originalTitleDescriptor.set.call(this, translated);
        }
      });
    }
  } catch (e) {
    console.error('Failed to hook document title:', e);
  }
  // Dynamic Cloud Dictionary Auto-Updater (Cached via localStorage for instant startup)
  try {
    const cachedDict = localStorage.getItem('antigravity_chinese_patch_dict');
    if (cachedDict) {
      const data = JSON.parse(cachedDict);
      Object.assign(dictionary, data);
    }
  } catch (e) {
    console.error('Failed to load cached cloud dictionary:', e);
  }

  // Fetch the latest dictionary in the background
  fetch('https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/dist/dictionary.json')
    .then(res => {
      if (res.ok) return res.json();
      throw new Error('Network response was not ok');
    })
    .then(data => {
      if (data && typeof data === 'object') {
        localStorage.setItem('antigravity_chinese_patch_dict', JSON.stringify(data));
        Object.assign(dictionary, data);
        console.log('Antigravity Chinese Patch: Cloud dictionary updated successfully! Total keys: ' + Object.keys(data).length);
        
        // Force refresh current body translation to apply updates instantly
        if (document.body) {
          walk(document.body);
        }
      }
    })
    .catch(err => {
      console.warn('Antigravity Chinese Patch: Cloud update failed or offline. Using local dictionary. Details:', err);
    });

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
