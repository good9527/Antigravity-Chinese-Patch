"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
/**
 * Preload script -- runs in every BrowserWindow before the page loads.
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
  'use strict';

  // 1. Static Translation Dictionary (Pure ASCII Unicode Escapes)
  const dictionary = {
  "New Conversation": "\u65b0\u5efa\u5bf9\u8bdd",
  "Conversation History": "\u5386\u53f2\u5bf9\u8bdd",
  "Scheduled Tasks": "\u8ba1\u5212\u4efb\u52a1",
  "Projects": "\u9879\u76ee\u5217\u8868",
  "Conversations": "\u8fd1\u671f\u5bf9\u8bdd",
  "Settings": "\u8bbe\u7f6e",
  "Untitled Conversation": "\u672a\u547d\u540d\u5bf9\u8bdd",
  "Untitled": "\u672a\u547d\u540d",
  "No conversations yet": "\u6682\u65e0\u5bf9\u8bdd",
  "No conversations found": "\u672a\u627e\u5230\u76f8\u5173\u5bf9\u8bdd",
  "See all": "\u67e5\u770b\u5168\u90e8",
  "See all conversations": "\u67e5\u770b\u5168\u90e8\u5bf9\u8bdd",
  "All conversations": "\u5168\u90e8\u5bf9\u8bdd",
  "Recent Conversations": "\u8fd1\u671f\u5bf9\u8bdd",
  "Active Conversations": "\u6d3b\u8dc3\u5bf9\u8bdd",
  "Archived Conversations": "\u5f52\u6863\u5bf9\u8bdd",
  "Pinned Conversations": "\u7f6e\u9876\u5bf9\u8bdd",
  "Clear Conversations": "\u6e05\u9664\u5bf9\u8bdd\u8bb0\u5f55",
  "Clear History": "\u6e05\u9664\u5386\u53f2\u8bb0\u5f55",
  "Clear All": "\u6e05\u9664\u5168\u90e8",
  "Clear all history": "\u6e05\u9664\u5168\u90e8\u5386\u53f2\u8bb0\u5f55",
  "Delete Conversation": "\u5220\u9664\u5bf9\u8bdd",
  "Delete All Conversations": "\u5220\u9664\u6240\u6709\u5bf9\u8bdd",
  "Delete Project": "\u5220\u9664\u9879\u76ee",
  "Export Conversation": "\u5bfc\u51fa\u5bf9\u8bdd",
  "Import Conversation": "\u5bfc\u5165\u5bf9\u8bdd",
  "Pin Conversation": "\u7f6e\u9876\u5bf9\u8bdd",
  "Unpin Conversation": "\u53d6\u6d88\u7f6e\u9876",
  "Pin to top": "\u7f6e\u9876\u5230\u9876\u90e8",
  "Unpin from top": "\u53d6\u6d88\u7f6e\u9876",
  "Collapse All": "\u5168\u90e8\u6298\u53e0",
  "Expand All": "\u5168\u90e8\u5c55\u5f00",
  "Collapse sidebar": "\u6298\u53e0\u4fa7\u8fb9\u680f",
  "Expand sidebar": "\u5c55\u5f00\u4fa7\u8fb9\u680f",
  "Toggle Sidebar": "\u5207\u6362\u4fa7\u8fb9\u680f",
  "Toggle History": "\u5207\u6362\u5386\u53f2\u9762\u677f",
  "Toggle File Tree": "\u5207\u6362\u6587\u4ef6\u6811",
  "Toggle Terminal": "\u5207\u6362\u7ec8\u7aef\u7a97\u53e3",
  "Toggle Artifacts": "\u5207\u6362\u4ea7\u7269\u9762\u677f",
  "Search conversations...": "\u641c\u7d22\u5bf9\u8bdd...",
  "Search history...": "\u641c\u7d22\u5386\u53f2...",
  "Search files...": "\u641c\u7d22\u6587\u4ef6...",
  "Filter by project": "\u6309\u9879\u76ee\u7b5b\u9009",
  "Filter by date": "\u6309\u65e5\u671f\u7b5b\u9009",
  "Sort by Date": "\u6309\u65e5\u671f\u6392\u5e8f",
  "Sort by Name": "\u6309\u540d\u79f0\u6392\u5e8f",
  "Select Next Conversation": "\u9009\u62e9\u4e0b\u4e00\u4e2a\u5bf9\u8bdd",
  "Select Previous Conversation": "\u9009\u62e9\u4e0a\u4e00\u4e2a\u5bf9\u8bdd",
  "Close Conversation": "\u5173\u95ed\u5bf9\u8bdd",
  "Rename Conversation": "\u91cd\u547d\u540d\u5bf9\u8bdd",
  "Duplicate Conversation": "\u590d\u5236\u5bf9\u8bdd",
  "Share Conversation": "\u5206\u4eab\u5bf9\u8bdd",
  "Copy Link": "\u590d\u5236\u94fe\u63a5",
  "Copy conversation link": "\u590d\u5236\u5bf9\u8bdd\u94fe\u63a5",
  "Subagents": "\u5b50\u667a\u80fd\u4f53",
  "Files Changed": "\u5df2\u4fee\u6539\u6587\u4ef6",
  "Artifacts": "\u4ea7\u7269",
  "Uploads": "\u5df2\u4e0a\u4f20\u6587\u4ef6",
  "Background Tasks": "\u540e\u53f0\u4efb\u52a1",
  "Active Tasks": "\u8fdb\u884c\u4e2d\u4efb\u52a1",
  "Completed Tasks": "\u5df2\u5b8c\u6210\u4efb\u52a1",
  "Failed Tasks": "\u5df2\u5931\u8d25\u4efb\u52a1",
  "Task Details": "\u4efb\u52a1\u8be6\u60c5",
  "Task Output": "\u4efb\u52a1\u8f93\u51fa",
  "Task History": "\u4efb\u52a1\u5386\u53f2",
  "Task Logs": "\u4efb\u52a1\u65e5\u5fd7",
  "Stop Task": "\u505c\u6b62\u4efb\u52a1",
  "Restart Task": "\u91cd\u65b0\u8fd0\u884c\u4efb\u52a1",
  "Cancel Task": "\u53d6\u6d88\u4efb\u52a1",
  "Kill Task": "\u7ec8\u6b62\u4efb\u52a1",
  "Running Tasks": "\u8fd0\u884c\u4e2d\u4efb\u52a1",
  "No background tasks": "\u6682\u65e0\u540e\u53f0\u4efb\u52a1",
  "No subagents running": "\u6682\u65e0\u8fd0\u884c\u4e2d\u7684\u5b50\u667a\u80fd\u4f53",
  "No files changed yet": "\u6682\u65e0\u4fee\u6539\u7684\u6587\u4ef6",
  "No artifacts generated": "\u6682\u65e0\u751f\u6210\u7684\u4ea7\u7269",
  "No uploads found": "\u6682\u65e0\u4e0a\u4f20\u6587\u4ef6",
  "Artifact Preview": "\u4ea7\u7269\u9884\u89c8",
  "Artifact History": "\u4ea7\u7269\u5386\u53f2",
  "Artifact Review Policy": "\u4ea7\u7269\u5ba1\u6838\u7b56\u7565",
  "Download Artifact": "\u4e0b\u8f7d\u4ea7\u7269",
  "Open Artifact": "\u6253\u5f00\u4ea7\u7269",
  "Save Artifact": "\u4fdd\u5b58\u4ea7\u7269",
  "Copy Artifact": "\u590d\u5236\u4ea7\u7269",
  "View Raw Artifact": "\u67e5\u770b\u539f\u59cb\u4ea7\u7269",
  "File Changes": "\u6587\u4ef6\u53d8\u66f4",
  "Diff View": "\u5dee\u5f02\u89c6\u56fe",
  "Split Diff": "\u5206\u680f\u5dee\u5f02",
  "Unified Diff": "\u7edf\u4e00\u5dee\u5f02",
  "Inline Diff": "\u884c\u5185\u5dee\u5f02",
  "Next Change": "\u4e0b\u4e00\u4e2a\u53d8\u66f4",
  "Previous Change": "\u4e0a\u4e00\u4e2a\u53d8\u66f4",
  "Revert File": "\u8fd8\u539f\u6587\u4ef6",
  "Revert All Files": "\u8fd8\u539f\u5168\u90e8\u6587\u4ef6",
  "Accept All Changes": "\u63a5\u53d7\u5168\u90e8\u66f4\u6539",
  "Reject All Changes": "\u62d2\u7edd\u5168\u90e8\u66f4\u6539",
  "MCP Servers": "MCP \u670d\u52a1",
  "Installed MCP Servers": "\u5df2\u90e8\u7f72\u7684 MCP \u670d\u52a1",
  "Add MCP Servers": "\u6dfb\u52a0 MCP \u670d\u52a1",
  "Add MCP Server": "\u6dfb\u52a0 MCP \u670d\u52a1",
  "Configure MCP Server": "\u914d\u7f6e MCP \u670d\u52a1",
  "Edit MCP Server": "\u7f16\u8f91 MCP \u670d\u52a1",
  "Remove MCP Server": "\u79fb\u9664 MCP \u670d\u52a1",
  "Enable MCP Server": "\u542f\u7528 MCP \u670d\u52a1",
  "Disable MCP Server": "\u7981\u7528 MCP \u670d\u52a1",
  "MCP Server Status": "MCP \u670d\u52a1\u72b6\u6001",
  "MCP Server Settings": "MCP \u670d\u52a1\u8bbe\u7f6e",
  "MCP Tools": "MCP \u5de5\u5177",
  "MCP Resources": "MCP \u8d44\u6e90",
  "MCP Prompts": "MCP \u63d0\u793a\u8bcd\u6a21\u677f",
  "MCP Error": "MCP \u5f02\u5e38",
  "No MCP Servers": "\u6682\u65e0 MCP \u670d\u52a1",
  "No MCP servers configured": "\u672a\u914d\u7f6e\u4efb\u4f55 MCP \u670d\u52a1",
  "Configure external tools via Model Context Protocol": "\u901a\u8fc7\u6a21\u578b\u4e0a\u4e0b\u6587\u534f\u8bae (MCP) \u914d\u7f6e\u5916\u90e8\u6269\u5c55\u5de5\u5177",
  "Configure default behaviors, skills, and MCP servers.": "\u914d\u7f6e\u9ed8\u8ba4\u884c\u4e3a\u3001\u6280\u80fd\u4e0e MCP \u670d\u52a1\u3002",
  "Configure default behaviors, skills, and MCP servers. Learn more": "\u914d\u7f6e\u9ed8\u8ba4\u884c\u4e3a\u3001\u6280\u80fd\u4e0e MCP \u670d\u52a1\u3002\u4e86\u89e3\u66f4\u591a",
  "Server Name": "\u670d\u52a1\u540d\u79f0",
  "Server Command": "\u542f\u52a8\u547d\u4ee4",
  "Server Arguments": "\u542f\u52a8\u53c2\u6570",
  "Server Environment Variables": "\u73af\u5883\u53d8\u91cf",
  "Server Transport": "\u4f20\u8f93\u534f\u8bae",
  "Stdio Transport": "\u6807\u51c6\u8f93\u5165\u8f93\u51fa (Stdio)",
  "SSE Transport": "\u670d\u52a1\u7aef\u63a8\u9001\u4e8b\u4ef6 (SSE)",
  "Server URL": "\u670d\u52a1\u5730\u5740 (URL)",
  "Connect MCP Server": "\u8fde\u63a5 MCP \u670d\u52a1",
  "Disconnect MCP Server": "\u65ad\u5f00 MCP \u670d\u52a1",
  "Reconnect MCP Server": "\u91cd\u65b0\u8fde\u63a5 MCP \u670d\u52a1",
  "MCP Server Connected": "MCP \u670d\u52a1\u5df2\u8fde\u63a5",
  "MCP Server Disconnected": "MCP \u670d\u52a1\u5df2\u65ad\u5f00",
  "MCP Server Connecting...": "MCP \u670d\u52a1\u8fde\u63a5\u4e2d...",
  "MCP Server Failed": "MCP \u670d\u52a1\u542f\u52a8\u5931\u8d25",
  "Tool Approval Policy": "\u5de5\u5177\u8c03\u7528\u5ba1\u6279\u7b56\u7565",
  "Always Approve Tool": "\u59cb\u7ec8\u6279\u51c6\u8be5\u5de5\u5177",
  "Ask Before Executing Tool": "\u6267\u884c\u5de5\u5177\u524d\u8be2\u95ee",
  "Block Tool Execution": "\u963b\u6b62\u8be5\u5de5\u5177\u6267\u884c",
  "Tool Call Parameters": "\u5de5\u5177\u8c03\u7528\u53c2\u6570",
  "Tool Call Result": "\u5de5\u5177\u8c03\u7528\u8fd4\u56de\u7ed3\u679c",
  "Tool Execution Timeout": "\u5de5\u5177\u6267\u884c\u8d85\u65f6",
  "Tool Execution Error": "\u5de5\u5177\u6267\u884c\u62a5\u9519",
  "Create Project": "\u521b\u5efa\u9879\u76ee",
  "Open Project": "\u6253\u5f00\u9879\u76ee",
  "Open Workspace": "\u6253\u5f00\u5de5\u4f5c\u533a",
  "Add Workspace": "\u6dfb\u52a0\u5de5\u4f5c\u533a",
  "Add Folder to Workspace": "\u6dfb\u52a0\u6587\u4ef6\u5939\u5230\u5de5\u4f5c\u533a",
  "Remove Folder from Workspace": "\u4ece\u5de5\u4f5c\u533a\u79fb\u9664\u6587\u4ef6\u5939",
  "Workspace Settings": "\u5de5\u4f5c\u533a\u8bbe\u7f6e",
  "Workspace Root": "\u5de5\u4f5c\u533a\u6839\u76ee\u5f55",
  "Multi-Folder Workspace": "\u591a\u6587\u4ef6\u5939\u5de5\u4f5c\u533a",
  "Project Settings": "\u9879\u76ee\u8bbe\u7f6e",
  "Project-Specific Settings": "\u9879\u76ee\u4e13\u5c5e\u8bbe\u7f6e",
  "Not in Project": "\u975e\u9879\u76ee\u5bf9\u8bdd",
  "In Project": "\u5f53\u524d\u9879\u76ee",
  "Switch Project": "\u5207\u6362\u9879\u76ee",
  "Close Project": "\u5173\u95ed\u9879\u76ee",
  "File Picker": "\u6587\u4ef6\u9009\u62e9\u5668",
  "File Access Rules": "\u6587\u4ef6\u8bbf\u95ee\u89c4\u5219",
  "File Permissions": "\u6587\u4ef6\u6743\u9650",
  "Open File": "\u6253\u5f00\u6587\u4ef6",
  "Open Folder": "\u6253\u5f00\u6587\u4ef6\u5939",
  "Reveal in File Explorer": "\u5728\u8d44\u6e90\u7ba1\u7406\u5668\u4e2d\u663e\u793a",
  "Reveal in Finder": "\u5728\u8bbf\u8fbe\u4e2d\u663e\u793a",
  "Copy Path": "\u590d\u5236\u8def\u5f84",
  "Copy Relative Path": "\u590d\u5236\u76f8\u5bf9\u8def\u5f84",
  "Refresh File Tree": "\u5237\u65b0\u6587\u4ef6\u6811",
  "New File": "\u65b0\u5efa\u6587\u4ef6",
  "New Folder": "\u65b0\u5efa\u6587\u4ef6\u5939",
  "Rename File": "\u91cd\u547d\u540d\u6587\u4ef6",
  "Delete File": "\u5220\u9664\u6587\u4ef6",
  "Save File": "\u4fdd\u5b58\u6587\u4ef6",
  "Save All Files": "\u4fdd\u5b58\u6240\u6709\u6587\u4ef6",
  "Open in Terminal": "\u5728\u7ec8\u7aef\u4e2d\u6253\u5f00",
  "Open in External Editor": "\u5728\u5916\u90e8\u7f16\u8f91\u5668\u4e2d\u6253\u5f00",
  "Open in VS Code": "\u5728 VS Code \u4e2d\u6253\u5f00",
  "Open in Antigravity IDE": "\u5728 Antigravity IDE \u4e2d\u6253\u5f00",
  "Models": "\u6a21\u578b\u5217\u8868",
  "All models": "\u5168\u90e8\u6a21\u578b",
  "Selected Model": "\u5f53\u524d\u9009\u4e2d\u6a21\u578b",
  "Switch Model": "\u5207\u6362\u6a21\u578b",
  "Select a model": "\u9009\u62e9\u4e00\u4e2a\u6a21\u578b",
  "Add Custom Model": "\u6dfb\u52a0\u81ea\u5b9a\u4e49\u6a21\u578b",
  "Edit Custom Model": "\u7f16\u8f91\u81ea\u5b9a\u4e49\u6a21\u578b",
  "Delete Custom Model": "\u5220\u9664\u81ea\u5b9a\u4e49\u6a21\u578b",
  "Toggle Model Selector": "\u5207\u6362\u6a21\u578b\u9009\u62e9\u5668",
  "Model Parameters": "\u6a21\u578b\u53c2\u6570\u914d\u7f6e",
  "Model Configuration": "\u6a21\u578b\u914d\u7f6e",
  "Model Quota": "\u6a21\u578b\u914d\u989d",
  "Model Credits": "\u6a21\u578b\u70b9\u6570",
  "Temperature": "\u6e29\u5ea6\u53c2\u6570",
  "Top P": "Top P \u91c7\u6837",
  "Top K": "\u5019\u9009\u6570\u91cf (Top K)",
  "Max Tokens": "\u6700\u5927 Token \u6570",
  "Max Output Tokens": "\u6700\u5927\u8f93\u51fa Token \u6570",
  "Context Window": "\u4e0a\u4e0b\u6587\u7a97\u53e3",
  "Token Usage": "Token \u4f7f\u7528\u91cf",
  "Prompt Tokens": "\u63d0\u793a\u8bcd Token \u6570",
  "Completion Tokens": "\u8865\u5168 Token \u6570",
  "Total Tokens": "\u603b Token \u6570",
  "Quota Exceeded": "\u914d\u989d\u5df2\u7528\u5c3d",
  "Daily Quota Exceeded": "\u6bcf\u65e5\u914d\u989d\u5df2\u7528\u5c3d",
  "Monthly Quota Exceeded": "\u6bcf\u6708\u914d\u989d\u5df2\u7528\u5c3d",
  "Rate Limit Reached": "\u5df2\u8fbe\u5230\u901f\u7387\u9650\u5236",
  "Please try again later": "\u8bf7\u7a0d\u540e\u518d\u8bd5",
  "Credits Balance": "\u8d26\u6237\u70b9\u6570\u4f59\u989d",
  "Available AI Credits": "\u53ef\u7528 AI \u70b9\u6570",
  "Available AI Credits:": "\u53ef\u7528 AI \u70b9\u6570\uff1a",
  "Get More AI Credits": "\u83b7\u53d6\u66f4\u591a AI \u70b9\u6570",
  "Purchase Credits": "\u8d2d\u4e70\u70b9\u6570",
  "Daily Quota": "\u6bcf\u65e5\u514d\u8d39\u914d\u989d",
  "Monthly Quota": "\u6bcf\u6708\u914d\u989d",
  "Unlimited": "\u65e0\u9650\u5236",
  "Refreshes in": "\u91cd\u7f6e\u5012\u8ba1\u65f6",
  "Refreshes daily": "\u6bcf\u65e5\u91cd\u7f6e",
  "Refreshes monthly": "\u6bcf\u6708\u91cd\u7f6e",
  "Your Plan: Google AI Ultra": "\u8ba2\u9605\u8ba1\u5212\uff1aGoogle AI \u65d7\u8230\u7248 (Ultra)",
  "Your Plan: Google AI Pro": "\u8ba2\u9605\u8ba1\u5212\uff1aGoogle AI \u4e13\u4e1a\u7248 (Pro)",
  "Your Plan: Free Tier": "\u8ba2\u9605\u8ba1\u5212\uff1a\u514d\u8d39\u7248",
  "Upgrade Plan": "\u5347\u7ea7\u8ba2\u9605\u8ba1\u5212",
  "Manage Subscription": "\u7ba1\u7406\u8ba2\u9605",
  "AI Credit Overages": "\u5141\u8bb8\u8d85\u51fa\u914d\u989d\u540e\u6263\u9664\u70b9\u6570",
  "Enable AI Credit Overages": "\u5f00\u542f\u70b9\u6570\u8d85\u989d\u6263\u8d39",
  "Disable AI Credit Overages": "\u5173\u95ed\u70b9\u6570\u8d85\u989d\u6263\u8d39",
  "View your available model quota and AI credits. Model quota refreshes periodically based on your plan. Enable AI Credit Overages to continue using models when your quota is exhausted.": "\u67e5\u770b\u60a8\u53ef\u7528\u7684\u6a21\u578b\u914d\u989d\u548c AI \u70b9\u6570\u3002\u6a21\u578b\u914d\u989d\u4f1a\u6839\u636e\u60a8\u7684\u8ba2\u9605\u8ba1\u5212\u5b9a\u671f\u91cd\u7f6e\u3002\u5f00\u542f\u5141\u8bb8\u8d85\u51fa\u989d\u5ea6\u540e\u6263\u9664\u70b9\u6570\uff0c\u53ef\u5728\u914d\u989d\u8017\u5c3d\u540e\u7ee7\u7eed\u4f7f\u7528\u6a21\u578b\u3002",
  "You can upgrade to a Google AI Ultra plan to receive the highest rate limits": "\u60a8\u53ef\u4ee5\u5347\u7ea7\u5230 Google AI Ultra \u65d7\u8230\u8ba1\u5212\u4ee5\u83b7\u53d6\u6700\u9ad8\u901f\u7387\u9650\u5236\u4e0e\u4f18\u5148\u5e76\u53d1\u5904\u7406",
  "High demand: rate limits currently lowered": "\u5f53\u524d\u8bf7\u6c42\u91cf\u8f83\u5927\uff1a\u901f\u7387\u9650\u5236\u5df2\u4e34\u65f6\u4e0b\u8c03",
  "Agent Security Settings": "\u667a\u80fd\u4f53\u5b89\u5168\u8bbe\u7f6e",
  "Agent Behavior": "\u667a\u80fd\u4f53\u884c\u4e3a",
  "Agent Settings": "\u667a\u80fd\u4f53\u8bbe\u7f6e",
  "Agent Team": "\u667a\u80fd\u4f53\u534f\u4f5c\u56e2\u961f",
  "Security Preset": "\u5b89\u5168\u9884\u8bbe\u7b56\u7565",
  "Strict Mode": "\u4e25\u683c\u5b89\u5168\u6a21\u5f0f",
  "Standard Mode": "\u6807\u51c6\u5b89\u5168\u6a21\u5f0f",
  "Permissive Mode": "\u5bbd\u677e\u4fe1\u4efb\u6a21\u5f0f",
  "Agent always asks for review.": "\u667a\u80fd\u4f53\u5c06\u59cb\u7ec8\u8bf7\u6c42\u5ba1\u6838\u3002",
  "Agent cannot modify files outside of the workspace in strict mode.": "\u5728\u4e25\u683c\u6a21\u5f0f\u4e0b\uff0c\u667a\u80fd\u4f53\u65e0\u6cd5\u4fee\u6539\u5de5\u4f5c\u533a\u5916\u7684\u6587\u4ef6\u3002",
  "Agent will always ask to review in strict mode.": "\u5728\u4e25\u683c\u6a21\u5f0f\u4e0b\uff0c\u667a\u80fd\u4f53\u5c06\u59cb\u7ec8\u8bf7\u6c42\u5ba1\u6838\u3002",
  "Agents have full access to your machine and external resources.": "\u667a\u80fd\u4f53\u5bf9\u60a8\u7684\u8ba1\u7b97\u673a\u548c\u5916\u90e8\u8d44\u6e90\u62e5\u6709\u5b8c\u5168\u8bbf\u95ee\u6743\u9650\u3002",
  "Agent settings and permissions for conversations outside of projects": "\u9002\u7528\u4e8e\u975e\u9879\u76ee\u5bf9\u8bdd\u7684\u667a\u80fd\u4f53\u5168\u5c40\u8bbe\u7f6e\u4e0e\u6743\u9650",
  "A shell setup script run before every command the agent executes.": "\u5728\u667a\u80fd\u4f53\u6267\u884c\u6bcf\u6761\u547d\u4ee4\u524d\u8fd0\u884c\u7684 Shell \u521d\u59cb\u5316\u811a\u672c\u3002",
  "Agent Auto-Fix Lints": "\u667a\u80fd\u4f53\u81ea\u52a8\u4fee\u590d\u4ee3\u7801 Lint \u9519\u8bef",
  "Agent Non-Workspace File Access": "\u667a\u80fd\u4f53\u5de5\u4f5c\u533a\u5916\u6587\u4ef6\u8bbf\u95ee\u6743\u9650",
  "Agent Script Command Configuration": "\u667a\u80fd\u4f53\u811a\u672c\u4e0e\u547d\u4ee4\u914d\u7f6e",
  "Terminal Command Execution Policy": "\u7ec8\u7aef\u547d\u4ee4\u6267\u884c\u7b56\u7565",
  "Terminal Execution Policy": "\u7ec8\u7aef\u6267\u884c\u7b56\u7565",
  "Terminal Commands": "\u7ec8\u7aef\u547d\u4ee4",
  "Commands Outside Sandbox": "\u6c99\u7bb1\u5916\u6267\u884c\u547d\u4ee4",
  "Allow commands outside sandbox": "\u5141\u8bb8\u5728\u6c99\u7bb1\u5916\u90e8\u6267\u884c\u547d\u4ee4",
  "Requires confirmation for dangerous operations": "\u5371\u9669\u64cd\u4f5c\u9700\u8981\u7528\u6237\u4e8c\u6b21\u786e\u8ba4",
  "File Access Policy": "\u6587\u4ef6\u8bbf\u95ee\u7b56\u7565",
  "Network Access Policy": "\u7f51\u7edc\u8bbf\u95ee\u7b56\u7565",
  "Network Permissions": "\u7f51\u7edc\u8bbf\u95ee\u6743\u9650",
  "Local Permissions": "\u672c\u5730\u6743\u9650",
  "Actuation Permissions": "\u81ea\u4e3b\u6267\u884c\u6743\u9650",
  "Browser Actuation Rules": "\u6d4f\u89c8\u5668\u81ea\u4e3b\u64cd\u4f5c\u89c4\u5219",
  "Browser Javascript Execution Policy": "\u6d4f\u89c8\u5668 JS \u811a\u672c\u6267\u884c\u7b56\u7565",
  "Read-only mode": "\u53ea\u8bfb\u6a21\u5f0f",
  "Read and Write": "\u8bfb\u5199\u6a21\u5f0f",
  "Full Access": "\u5b8c\u5168\u8bbf\u95ee",
  "Restricted Access": "\u53d7\u9650\u8bbf\u95ee",
  "Blocked by Policy": "\u5df2\u88ab\u5b89\u5168\u7b56\u7565\u62e6\u622a",
  "Allow": "\u5141\u8bb8",
  "Deny": "\u62d2\u7edd",
  "Always Allow": "\u59cb\u7ec8\u5141\u8bb8",
  "Always Deny": "\u59cb\u7ec8\u62d2\u7edd",
  "Always Proceed": "\u59cb\u7ec8\u7ee7\u7eed",
  "Always Ask": "\u59cb\u7ec8\u8be2\u95ee",
  "Ask before running": "\u8fd0\u884c\u524d\u8be2\u95ee",
  "Ask every time": "\u6bcf\u6b21\u90fd\u8be2\u95ee",
  "Never ask": "\u4ece\u4e0d\u8be2\u95ee",
  "Confirm Command Execution": "\u786e\u8ba4\u547d\u4ee4\u6267\u884c",
  "Do you want to run this command?": "\u60a8\u786e\u5b9a\u8981\u6267\u884c\u6b64\u7ec8\u7aef\u547d\u4ee4\u5417\uff1f",
  "Dangerous Command Detected": "\u68c0\u6d4b\u5230\u9ad8\u5371\u547d\u4ee4",
  "This command may modify system files or execute external binaries.": "\u6b64\u547d\u4ee4\u53ef\u80fd\u4f1a\u4fee\u6539\u7cfb\u7edf\u6587\u4ef6\u6216\u6267\u884c\u5916\u90e8\u4e8c\u8fdb\u5236\u7a0b\u5e8f\uff0c\u8bf7\u8c28\u614e\u6838\u5bf9\u3002",
  "Appearance": "\u5916\u89c2\u6837\u5f0f",
  "Theme Mode": "\u914d\u8272\u4e3b\u9898\u6a21\u5f0f",
  "Follow System Theme": "\u8ddf\u968f\u7cfb\u7edf\u4e3b\u9898",
  "Follow System": "\u8ddf\u968f\u7cfb\u7edf",
  "Light Theme": "\u6d45\u8272\u4e3b\u9898",
  "Dark Theme": "\u6df1\u8272\u4e3b\u9898",
  "High Contrast Theme": "\u9ad8\u5bf9\u6bd4\u5ea6\u4e3b\u9898",
  "Color Theme": "\u989c\u8272\u4e3b\u9898",
  "Font Family": "\u754c\u9762\u5b57\u4f53",
  "Font Size": "\u5b57\u53f7\u5927\u5c0f",
  "Editor Font Size": "\u7f16\u8f91\u5668\u5b57\u53f7",
  "Terminal Font Size": "\u7ec8\u7aef\u5b57\u53f7",
  "Line Height": "\u884c\u9ad8",
  "Zoom Factor": "\u7f29\u653e\u6bd4\u4f8b",
  "Zoom In": "\u653e\u5927",
  "Zoom Out": "\u7f29\u5c0f",
  "Reset Zoom": "\u91cd\u7f6e\u7f29\u653e",
  "Custom CSS": "\u81ea\u5b9a\u4e49\u6837\u5f0f\u8868 (CSS)",
  "Customizations": "\u81ea\u5b9a\u4e49\u529f\u80fd",
  "Browser": "\u6d4f\u89c8\u5668\u52a9\u624b",
  "Browser Settings": "\u6d4f\u89c8\u5668\u8bbe\u7f6e",
  "App": "\u5ba2\u6237\u7aef\u8bbe\u7f6e",
  "App Settings": "\u5e94\u7528\u8bbe\u7f6e",
  "Chat Settings": "\u804a\u5929\u8bbe\u7f6e",
  "Account": "\u8d26\u6237\u8bbe\u7f6e",
  "Permissions": "\u6743\u9650\u63a7\u5236",
  "Advanced Settings": "\u9ad8\u7ea7\u8bbe\u7f6e",
  "RECOMMENDED": "\u63a8\u8350\u5feb\u6377\u952e",
  "NAVIGATION": "\u754c\u9762\u5bfc\u822a",
  "CONVERSATION": "\u5bf9\u8bdd\u4ea4\u4e92",
  "SHORTCUTS": "\u5feb\u6377\u952e",
  "Keyboard Shortcuts": "\u952e\u76d8\u5feb\u6377\u952e",
  "Keybindings": "\u6309\u952e\u7ed1\u5b9a",
  "Open Conversation Picker": "\u6253\u5f00\u5bf9\u8bdd\u9009\u62e9\u5668",
  "Open File Search": "\u6253\u5f00\u6587\u4ef6\u641c\u7d22",
  "Open Settings": "\u6253\u5f00\u8bbe\u7f6e",
  "Open Documentation": "\u6253\u5f00\u5b98\u65b9\u6587\u6863",
  "Open Logs Folder": "\u6253\u5f00\u65e5\u5fd7\u76ee\u5f55",
  "Restart Language Server": "\u91cd\u542f\u8bed\u8a00\u670d\u52a1\u7aef",
  "Command Palette": "\u547d\u4ee4\u9762\u677f",
  "Focus Input": "\u805a\u7126\u8f93\u5165\u6846",
  "Toggle Developer Tools": "\u5207\u6362\u5f00\u53d1\u8005\u5de5\u5177",
  "Toggle Full Screen": "\u5207\u6362\u5168\u5c4f",
  "Keep Computer Awake": "\u9632\u6b62\u8ba1\u7b97\u673a\u4f11\u7720",
  "Run in Background": "\u5728\u540e\u53f0\u4fdd\u6301\u8fd0\u884c",
  "Minimize to Tray": "\u6700\u5c0f\u5316\u5230\u7cfb\u7edf\u6258\u76d8",
  "Close to Tray": "\u5173\u95ed\u65f6\u6700\u5c0f\u5316\u5230\u6258\u76d8",
  "Start at Login": "\u5f00\u673a\u81ea\u542f\u52a8",
  "Provide Feedback": "\u63d0\u4ea4\u53cd\u9988",
  "Send Feedback": "\u53d1\u9001\u53cd\u9988",
  "Feedback Type": "\u53cd\u9988\u7c7b\u578b",
  "Bug Report": "\u7f3a\u9677\u62a5\u544a",
  "Feature Request": "\u529f\u80fd\u9700\u6c42",
  "Auth and Billing": "\u8d26\u6237\u4e0e\u8d26\u5355",
  "General Feedback": "\u5e38\u89c4\u53cd\u9988",
  "Description": "\u95ee\u9898\u63cf\u8ff0",
  "Steps to reproduce the issue": "\u91cd\u73b0\u6b65\u9aa4",
  "Steps to Reproduce": "\u91cd\u73b0\u6b65\u9aa4\u8bf4\u660e",
  "Expected behavior": "\u671f\u671b\u7ed3\u679c",
  "Actual behavior": "\u5b9e\u9645\u7ed3\u679c",
  "Any error messages": "\u9519\u8bef\u63d0\u793a\u4fe1\u606f",
  "Any relevant information": "\u5176\u4ed6\u76f8\u5173\u4fe1\u606f",
  "Describe the bug you encountered...": "\u8bf7\u8be6\u7ec6\u63cf\u8ff0\u60a8\u9047\u5230\u7684\u7f3a\u9677(Bug)...",
  "Describe your feature request...": "\u8bf7\u8be6\u7ec6\u63cf\u8ff0\u60a8\u671f\u5f85\u7684\u65b0\u529f\u80fd\u6216\u6539\u8fdb\u5efa\u8bae...",
  "Attach Screenshots": "\u9644\u52a0\u622a\u56fe",
  "Attach Diagnostic Logs": "\u9644\u5e26\u8bca\u65ad\u65e5\u5fd7",
  "Submit Feedback": "\u63d0\u4ea4\u53cd\u9988",
  "Thank you for your feedback!": "\u611f\u8c22\u60a8\u7684\u5b9d\u8d35\u53cd\u9988\uff01",
  "Report an Issue": "\u62a5\u544a\u95ee\u9898",
  "Community Discord": "\u52a0\u5165 Discord \u793e\u533a",
  "Terms of Service": "\u670d\u52a1\u6761\u6b3e",
  "Privacy Policy": "\u9690\u79c1\u653f\u7b56",
  "About Antigravity": "\u5173\u4e8e Antigravity",
  "Documentation": "\u5b98\u65b9\u6587\u6863",
  "Docs": "\u5b98\u65b9\u6587\u6863",
  "Help": "\u5e2e\u52a9",
  "Version": "\u5ba2\u6237\u7aef\u7248\u672c",
  "Check for Updates": "\u68c0\u67e5\u66f4\u65b0",
  "Loading Antigravity": "\u6b63\u5728\u52a0\u8f7d Antigravity",
  "Setting up...": "\u6b63\u5728\u521d\u59cb\u5316\u8bbe\u7f6e...",
  "Welcome to Antigravity": "\u6b22\u8fce\u4f7f\u7528 Antigravity",
  "Welcome to the new Antigravity!": "\u6b22\u8fce\u4f7f\u7528\u5168\u65b0\u5347\u7ea7\u7684 Antigravity\uff01",
  "Antigravity has been redesigned to put agents first with new capabilities. If you'd still like a code editor, you can download it as a separate app named Antigravity IDE.": "Antigravity \u73b0\u5df2\u5168\u9762\u5347\u7ea7\u4e3a\u4ee5\u667a\u80fd\u4f53\u4e3a\u6838\u5fc3\u7684\u5168\u65b0\u67b6\u6784\u3002\u5982\u679c\u60a8\u4ecd\u9700\u4f20\u7edf\u7684\u4ee3\u7801\u7f16\u8f91\u529f\u80fd\uff0c\u53ef\u4ee5\u5355\u72ec\u4e0b\u8f7d\u540d\u4e3a Antigravity IDE \u7684\u914d\u5957\u7f16\u8f91\u5668\u3002",
  "Download the Antigravity IDE": "\u4e0b\u8f7d Antigravity IDE \u7f16\u8f91\u5668",
  "Explore the new Antigravity": "\u7acb\u5373\u4f53\u9a8c\u5168\u65b0 Antigravity",
  "Install IDE": "\u5b89\u88c5 IDE \u63d2\u4ef6",
  "Installing IDE...": "\u6b63\u5728\u5b89\u88c5 IDE...",
  "IDE Installation Complete": "IDE \u5b89\u88c5\u5b8c\u6210",
  "IDE Installation Failed": "IDE \u5b89\u88c5\u5931\u8d25",
  "Launch IDE": "\u542f\u52a8 IDE",
  "Get Started": "\u5f00\u59cb\u4f7f\u7528",
  "Skip for now": "\u6682\u65f6\u8df3\u8fc7",
  "Next": "\u4e0b\u4e00\u6b65",
  "Back": "\u4e0a\u4e00\u6b65",
  "Finish": "\u5b8c\u6210",
  "Continue": "\u7ee7\u7eed",
  "File": "\u6587\u4ef6",
  "Edit": "\u7f16\u8f91",
  "View": "\u89c6\u56fe",
  "Window": "\u7a97\u53e3",
  "New Window": "\u65b0\u5efa\u7a97\u53e3",
  "Close Window": "\u5173\u95ed\u7a97\u53e3",
  "Minimize": "\u6700\u5c0f\u5316",
  "Maximize": "\u6700\u5927\u5316",
  "Zoom": "\u7f29\u653e",
  "Bring All to Front": "\u524d\u7f6e\u5168\u90e8\u7a97\u53e3",
  "Cut": "\u526a\u5207",
  "Copy": "\u590d\u5236",
  "Paste": "\u7c98\u8d34",
  "Paste and Match Style": "\u7c98\u8d34\u5e76\u5339\u914d\u6837\u5f0f",
  "Select All": "\u5168\u9009",
  "Undo": "\u64a4\u9500",
  "Redo": "\u91cd\u505a",
  "Speech": "\u8bed\u97f3",
  "Start Dictation": "\u5f00\u59cb\u542c\u5199",
  "Emoji & Symbols": "\u8868\u60c5\u4e0e\u7279\u6b8a\u7b26\u53f7",
  "Hide Antigravity": "\u9690\u85cf Antigravity",
  "Hide Others": "\u9690\u85cf\u5176\u4ed6\u5e94\u7528",
  "Show All": "\u663e\u793a\u5168\u90e8",
  "Quit Antigravity": "\u9000\u51fa Antigravity",
  "Quit": "\u9000\u51fa",
  "Exit": "\u9000\u51fa",
  "Restart": "\u91cd\u542f",
  "Restart Antigravity": "\u91cd\u542f Antigravity",
  "Updates": "\u8f6f\u4ef6\u66f4\u65b0",
  "Check for Updates...": "\u68c0\u67e5\u66f4\u65b0...",
  "Checking for Updates...": "\u6b63\u5728\u68c0\u67e5\u66f4\u65b0...",
  "Downloading Update...": "\u6b63\u5728\u4e0b\u8f7d\u66f4\u65b0...",
  "Update Available": "\u53d1\u73b0\u65b0\u7248\u672c",
  "Update Downloaded": "\u66f4\u65b0\u5df2\u5c31\u7eea",
  "Restart to Update": "\u91cd\u542f\u4ee5\u5b8c\u6210\u66f4\u65b0",
  "Up to date": "\u5df2\u662f\u6700\u65b0\u7248\u672c",
  "No updates available": "\u5f53\u524d\u5df2\u662f\u6700\u65b0\u7248\u672c\uff0c\u6682\u65e0\u53ef\u7528\u66f4\u65b0",
  "Notification Settings": "\u901a\u77e5\u8bbe\u7f6e",
  "Enable Desktop Notifications": "\u542f\u7528\u684c\u9762\u7cfb\u7edf\u901a\u77e5",
  "Sound Effects": "\u64cd\u4f5c\u97f3\u6548",
  "No agent running": "\u6682\u65e0\u8fd0\u884c\u4e2d\u7684\u667a\u80fd\u4f53",
  "No agents running": "\u6682\u65e0\u8fd0\u884c\u4e2d\u7684\u667a\u80fd\u4f53",
  "1 agent running": "1 \u4e2a\u667a\u80fd\u4f53\u6b63\u5728\u8fd0\u884c",
  "agents running": "\u4e2a\u667a\u80fd\u4f53\u6b63\u5728\u8fd0\u884c",
  "Review": "\u5ba1\u6838",
  "Review Changes": "\u5ba1\u6838\u66f4\u6539",
  "Review this code": "\u5ba1\u6838\u6b64\u4ee3\u7801",
  "Review my design": "\u5ba1\u6838\u6211\u7684\u8bbe\u8ba1",
  "Review Step": "\u5ba1\u6838\u6b65\u9aa4",
  "Accept": "\u63a5\u53d7",
  "Reject": "\u62d2\u7edd",
  "Accept Step": "\u63a5\u53d7\u6b65\u9aa4",
  "Reject Step": "\u62d2\u7edd\u6b65\u9aa4",
  "Accept All": "\u63a5\u53d7\u5168\u90e8",
  "Reject All": "\u62d2\u7edd\u5168\u90e8",
  "Action Required": "\u9700\u8981\u64cd\u4f5c",
  "User Approval Required": "\u9700\u8981\u7528\u6237\u786e\u8ba4\u5ba1\u6279",
  "Apply": "\u5e94\u7528",
  "Apply Changes": "\u5e94\u7528\u66f4\u6539",
  "Discard": "\u653e\u5f03",
  "Discard Changes": "\u653e\u5f03\u66f4\u6539",
  "Revert": "\u64a4\u9500",
  "Revert Changes": "\u64a4\u9500\u66f4\u6539",
  "Keep Changes": "\u4fdd\u7559\u66f4\u6539",
  "Compare Changes": "\u5bf9\u6bd4\u5dee\u5f02",
  "Modified": "\u5df2\u4fee\u6539",
  "Created": "\u5df2\u65b0\u5efa",
  "Deleted": "\u5df2\u5220\u9664",
  "Renamed": "\u5df2\u91cd\u547d\u540d",
  "Pending Review": "\u7b49\u5f85\u5ba1\u6838\u4e2d",
  "Approved": "\u5df2\u6279\u51c6",
  "Rejected": "\u5df2\u62d2\u7edd",
  "Thinking...": "\u601d\u8003\u4e2d...",
  "Working...": "\u5904\u7406\u4e2d...",
  "Planning...": "\u89c4\u5212\u4e2d...",
  "Executing...": "\u6267\u884c\u4e2d...",
  "Searching...": "\u641c\u7d22\u4e2d...",
  "Reading files...": "\u8bfb\u53d6\u6587\u4ef6\u4e2d...",
  "Writing files...": "\u5199\u5165\u6587\u4ef6\u4e2d...",
  "Running command...": "\u6267\u884c\u547d\u4ee4\u4e2d...",
  "Agent finished": "\u667a\u80fd\u4f53\u5df2\u5b8c\u6210",
  "Agent finished.": "\u667a\u80fd\u4f53\u5df2\u5b8c\u6210\u3002",
  "Agent execution finished": "\u667a\u80fd\u4f53\u6267\u884c\u5b8c\u6210",
  "Agent execution failed": "\u667a\u80fd\u4f53\u6267\u884c\u5931\u8d25",
  "Agent execution failed.": "\u667a\u80fd\u4f53\u6267\u884c\u5931\u8d25\u3002",
  "Agent paused": "\u667a\u80fd\u4f53\u5df2\u6682\u505c",
  "Agent stopped": "\u667a\u80fd\u4f53\u5df2\u505c\u6b62",
  "Agent response": "\u667a\u80fd\u4f53\u56de\u590d",
  "Stop": "\u505c\u6b62",
  "Stop generating": "\u505c\u6b62\u751f\u6210",
  "Stop Execution": "\u505c\u6b62\u6267\u884c",
  "Pause": "\u6682\u505c",
  "Resume": "\u7ee7\u7eed\u6267\u884c",
  "Regenerate": "\u91cd\u65b0\u751f\u6210",
  "Regenerate Response": "\u91cd\u65b0\u751f\u6210\u56de\u590d",
  "Retry": "\u91cd\u8bd5",
  "Try Again": "\u518d\u6b21\u5c1d\u8bd5",
  "Copied!": "\u5df2\u590d\u5236\uff01",
  "Copied to clipboard": "\u5df2\u590d\u5236\u5230\u526a\u8d34\u677f",
  "Copy code": "\u590d\u5236\u4ee3\u7801",
  "Copy message": "\u590d\u5236\u6d88\u606f",
  "Ask anything, @ to mention, / for actions": "\u95ee\u6211\u4efb\u4f55\u95ee\u9898\uff0c\u7528 @ \u63d0\u53ca\u6587\u4ef6\uff0c\u7528 / \u6267\u884c\u52a8\u4f5c",
  "Ask a question or provide instructions...": "\u8bf7\u8f93\u5165\u60a8\u7684\u95ee\u9898\u6216\u5177\u4f53\u6307\u4ee4...",
  "Type a message...": "\u8f93\u5165\u6d88\u606f...",
  "Type / for commands...": "\u8f93\u5165 / \u67e5\u770b\u53ef\u7528\u547d\u4ee4...",
  "Add context": "\u6dfb\u52a0\u4e0a\u4e0b\u6587",
  "Add to Chat": "\u6dfb\u52a0\u5230\u5bf9\u8bdd",
  "Add to Chat/Quote": "\u6dfb\u52a0\u5230\u5bf9\u8bdd/\u5f15\u7528",
  "Add files to context": "\u6dfb\u52a0\u6587\u4ef6\u5230\u4e0a\u4e0b\u6587",
  "Mention file or folder": "\u63d0\u53ca\u6587\u4ef6\u6216\u6587\u4ef6\u5939",
  "Attach File": "\u9644\u52a0\u6587\u4ef6",
  "Attach Image": "\u9644\u52a0\u56fe\u7247",
  "Drop files here to upload": "\u62d6\u62fd\u6587\u4ef6\u81f3\u6b64\u5904\u4e0a\u4f20",
  "Upload File": "\u4e0a\u4f20\u6587\u4ef6",
  "Upload Folder": "\u4e0a\u4f20\u6587\u4ef6\u5939",
  "New Task": "\u65b0\u5efa\u4efb\u52a1",
  "Open": "\u6253\u5f00",
  "Save": "\u4fdd\u5b58",
  "Close": "\u5173\u95ed",
  "Cancel": "\u53d6\u6d88",
  "Delete": "\u5220\u9664",
  "Rename": "\u91cd\u547d\u540d",
  "Customize": "\u5b9a\u5236",
  "Default": "\u9ed8\u8ba4",
  "Custom": "\u81ea\u5b9a\u4e49",
  "System": "\u8ddf\u968f\u7cfb\u7edf",
  "Turbo Mode": "\u6781\u901f\u6a21\u5f0f",
  "Turbo mode": "\u6781\u901f\u6a21\u5f0f",
  "Full Machine": "\u6574\u673a\u6388\u6743",
  "Search": "\u641c\u7d22",
  "Filter": "\u7b5b\u9009",
  "Refresh": "\u5237\u65b0",
  "Reset": "\u91cd\u7f6e",
  "OK": "\u786e\u5b9a",
  "Confirm": "\u786e\u8ba4",
  "Done": "\u5b8c\u6210",
  "Success": "\u6210\u529f",
  "Error": "\u9519\u8bef",
  "Warning": "\u8b66\u544a",
  "Info": "\u63d0\u793a",
  "Details": "\u8be6\u7ec6\u4fe1\u606f",
  "Show Details": "\u663e\u793a\u8be6\u60c5",
  "Hide Details": "\u9690\u85cf\u8be6\u60c5",
  "Learn More": "\u4e86\u89e3\u66f4\u591a",
  "Learn more": "\u4e86\u89e3\u66f4\u591a",
  "Absolute path to the Chrome/Chromium executable": "Chrome/Chromium \u53ef\u6267\u884c\u6587\u4ef6\u7684\u7edd\u5bf9\u8def\u5f84",
  "Receive product updates, tips, and promotions from Google Antigravity via email": "\u901a\u8fc7\u7535\u5b50\u90ae\u4ef6\u63a5\u6536\u6765\u81ea Google Antigravity \u7684\u4ea7\u54c1\u66f4\u65b0\u3001\u4f7f\u7528\u6280\u5de7\u4e0e\u4f18\u60e0\u4fe1\u606f",
  "copy link": "\u590d\u5236\u94fe\u63a5",
  "Copy link": "\u590d\u5236\u94fe\u63a5",
  "General": "\u5e38\u89c4",
  "Application": "\u5e94\u7528\u8bbe\u7f6e",
  "Model List": "\u6a21\u578b\u5217\u8868",
  "Browser Assistant": "\u6d4f\u89c8\u5668\u52a9\u624b",
  "Shortcuts": "\u5feb\u6377\u952e",
  "Feedback": "\u610f\u89c1\u53cd\u9988",
  "Show all": "\u663e\u793a\u5168\u90e8",
  "Execution": "\u6267\u884c\u63a7\u5236",
  "Configure agent execution, queued message delivery, and permissions.": "\u914d\u7f6e\u667a\u80fd\u4f53\u6267\u884c\u3001\u6392\u961f\u6d88\u606f\u53d1\u9001\u4e0e\u6743\u9650\u8bbe\u7f6e\u3002",
  "Queued Messages": "\u6392\u961f\u6d88\u606f",
  "Configure when follow-up messages are sent.": "\u914d\u7f6e\u540e\u7eed\u6d88\u606f\u7684\u53d1\u9001\u65f6\u673a\u3002",
  "Keyboard shortcuts": "\u952e\u76d8\u5feb\u6377\u952e",
  "Queue": "\u6392\u961f",
  "Send Immediately": "\u7acb\u5373\u53d1\u9001",
  "Choose a predefined security preset for the agent. This controls terminal auto-execution policy, and file access policy.": "\u4e3a\u667a\u80fd\u4f53\u9009\u62e9\u9884\u8bbe\u5b89\u5168\u7b56\u7565\u3002\u63a7\u5236\u7ec8\u7aef\u81ea\u52a8\u6267\u884c\u4e0e\u6587\u4ef6\u8bbf\u95ee\u6743\u9650\u3002",
  "Specifies Agent's behavior when asking for review on artifacts, which are documents it creates to enable a richer conversation experience.": "\u6307\u5b9a\u667a\u80fd\u4f53\u5728\u8bf7\u6c42\u5ba1\u6838\u4ea7\u7269\uff08\u751f\u6210\u7684\u5bcc\u6587\u6863\uff09\u65f6\u7684\u4ea4\u4e92\u7b56\u7565\u3002",
  "Always Continue": "\u59cb\u7ec8\u7ee7\u7eed",
  "Configure allowed and denied paths for file reads and writes.": "\u914d\u7f6e\u5141\u8bb8\u548c\u7981\u6b62\u8bfb\u5199\u7684\u6587\u4ef6\u8def\u5f84\u89c4\u5219\u3002",
  "Network Access Rules": "\u7f51\u7edc\u8bbf\u95ee\u89c4\u5219",
  "Configure allowed and denied URLs for reading.": "\u914d\u7f6e\u5141\u8bb8\u548c\u7981\u6b62\u8bfb\u53d6\u7684\u7f51\u7edc URL \u89c4\u5219\u3002",
  "Manage Antigravity app settings.": "\u7ba1\u7406 Antigravity \u5e94\u7528\u7a0b\u5e8f\u8bbe\u7f6e\u3002",
  "Prevent Sleep": "\u9632\u6b62\u7cfb\u7edf\u4f11\u7720",
  "Prevent the computer from sleeping while the app is running.": "\u5e94\u7528\u8fd0\u884c\u65f6\u9632\u6b62\u8ba1\u7b97\u673a\u8fdb\u5165\u7761\u7720\u72b6\u6001\u3002",
  "Keep In Menu Bar": "\u4fdd\u6301\u5728\u83dc\u5355\u680f/\u6258\u76d8",
  "Keep the app accessible from the menu bar and running in the background when all windows are closed.": "\u5173\u95ed\u6240\u6709\u7a97\u53e3\u540e\u5728\u540e\u53f0\u4fdd\u6301\u8fd0\u884c\uff0c\u5e76\u901a\u8fc7\u83dc\u5355\u680f\u6216\u6258\u76d8\u8bbf\u95ee\u3002",
  "Remote Control": "\u8fdc\u7a0b\u63a7\u5236",
  "Enable Remote Control": "\u542f\u7528\u8fdc\u7a0b\u63a7\u5236",
  "Work with local agents from another device.": "\u4ece\u5176\u4ed6\u8bbe\u5907\u8fde\u63a5\u5e76\u4f7f\u7528\u672c\u5730\u667a\u80fd\u4f53\u3002",
  "Device Name": "\u8bbe\u5907\u540d\u79f0",
  "Scan the code to open this device in Remote Control, or copy link.": "\u626b\u63cf\u4e8c\u7ef4\u7801\u4ee5\u5728\u8fdc\u7a0b\u63a7\u5236\u4e2d\u6253\u5f00\u6b64\u8bbe\u5907\uff0c\u6216\u590d\u5236\u94fe\u63a5\u3002",
  "Notifications": "\u901a\u77e5\u8bbe\u7f6e",
  "To modify notification settings, open your operating system's system preferences.": "\u5982\u9700\u4fee\u6539\u901a\u77e5\u8bbe\u7f6e\uff0c\u8bf7\u6253\u5f00\u64cd\u4f5c\u7cfb\u7edf\u7684\u7cfb\u7edf\u8bbe\u7f6e\u3002",
  "Open System Preferences": "\u6253\u5f00\u7cfb\u7edf\u504f\u597d\u8bbe\u7f6e",
  "Configure the agent's visual theme and display preferences.": "\u914d\u7f6e\u667a\u80fd\u4f53\u89c6\u89c9\u4e3b\u9898\u4e0e\u663e\u793a\u504f\u597d\u3002",
  "Verbose Agent Chat": "\u663e\u793a\u5b8c\u6574\u601d\u8003\u8fc7\u7a0b",
  "Display and preserve intermediate thinking steps.": "\u5c55\u793a\u5e76\u4fdd\u7559\u667a\u80fd\u4f53\u7684\u4e2d\u95f4\u601d\u8003\u6b65\u9aa4\u3002",
  "Conversation Width": "\u5bf9\u8bdd\u7a97\u53e3\u5bbd\u5ea6",
  "Configure the maximum width of the conversation panel.": "\u914d\u7f6e\u5bf9\u8bdd\u9762\u677f\u7684\u6700\u5927\u663e\u793a\u5bbd\u5ea6\u3002",
  "Narrow": "\u5c45\u4e2d\u7d27\u51d1",
  "Wide": "\u5168\u5bbd\u6a21\u5f0f",
  "Theme": "\u4e3b\u9898",
  "System Theme": "\u8ddf\u968f\u7cfb\u7edf\u4e3b\u9898",
  "Preset": "\u9884\u8bbe",
  "Light": "\u6d45\u8272",
  "Dark": "\u6df1\u8272",
  "Default Light": "\u9ed8\u8ba4\u6d45\u8272",
  "Default Dark": "\u9ed8\u8ba4\u6df1\u8272",
  "Background": "\u80cc\u666f\u8272",
  "Foreground": "\u524d\u666f\u8272",
  "Accent": "\u5f3a\u8c03\u8272",
  "The breakdown below shows token usage from customizations like skills, rules, and MCP. If the budget is exceeded, large customizations will be truncated automatically.": "\u4e0b\u65b9\u5c55\u793a\u4e86\u6280\u80fd\u3001\u89c4\u5219\u548c MCP \u7b49\u81ea\u5b9a\u4e49\u529f\u80fd\u7684 Token \u6d88\u8017\u660e\u7ec6\u3002\u82e5\u8d85\u51fa\u9884\u7b97\uff0c\u4f53\u79ef\u8fc7\u5927\u7684\u81ea\u5b9a\u4e49\u914d\u7f6e\u5c06\u88ab\u81ea\u52a8\u622a\u65ad\u3002",
  "There are no customizations enabled.": "\u5f53\u524d\u672a\u542f\u7528\u4efb\u4f55\u81ea\u5b9a\u4e49\u529f\u80fd\u3002",
  "Skills": "\u6280\u80fd",
  "Global": "\u5168\u5c40",
  "Add MCP": "\u6dfb\u52a0 MCP",
  "Add MCP +": "\u6dfb\u52a0 MCP +",
  "Open MCP Config": "\u6253\u5f00 MCP \u914d\u7f6e",
  "Configure default behaviors, skills, and MCP servers. Learn more.": "\u914d\u7f6e\u9ed8\u8ba4\u884c\u4e3a\u3001\u6280\u80fd\u4e0e MCP \u670d\u52a1\u3002\u4e86\u89e3\u66f4\u591a\u3002",
  "Gemini 3.5 Flash will be taken down soon": "Gemini 3.5 Flash \u5373\u5c06\u4e0b\u7ebf",
  "Update and switch to Gemini 3.7 Flash for even better performance and efficiency!": "\u8bf7\u66f4\u65b0\u5e76\u5207\u6362\u81f3 Gemini 3.7 Flash\uff0c\u4ee5\u83b7\u5f97\u66f4\u9ad8\u7684\u6027\u80fd\u4e0e\u6548\u7387\uff01",
  "Dismiss": "\u5ffd\u7565",
  "MCP Disconnected": "MCP \u5df2\u65ad\u5f00",
  "MCP Connected": "MCP \u5df2\u8fde\u63a5",
  "Model Selection": "\u6a21\u578b\u9009\u62e9",
  "Select Model": "\u9009\u62e9\u6a21\u578b",
  "Available Models": "\u53ef\u7528\u6a21\u578b",
  "Custom Model": "\u81ea\u5b9a\u4e49\u6a21\u578b",
  "API Key": "API \u5bc6\u94a5",
  "Enter API Key": "\u8f93\u5165 API \u5bc6\u94a5",
  "API Key is valid": "API \u5bc6\u94a5\u6709\u6548",
  "API Key is invalid": "API \u5bc6\u94a5\u65e0\u6548",
  "Save API Key": "\u4fdd\u5b58 API \u5bc6\u94a5",
  "Token Count": "Token \u8ba1\u6570",
  "Tokens Used": "\u5df2\u7528 Token",
  "Frequency Penalty": "\u9891\u7387\u60e9\u7f5a",
  "Presence Penalty": "\u5b58\u5728\u60e9\u7f5a",
  "System Prompt": "\u7cfb\u7edf\u63d0\u793a\u8bcd",
  "System Instructions": "\u7cfb\u7edf\u6307\u4ee4",
  "User Prompt": "\u7528\u6237\u63d0\u793a\u8bcd"
};

  // 2. Exact Phrase / Dynamic Templates
  const DYNAMIC_TEMPLATES = [
    { regex: /^Learn\s+more\s+about\s+(.+)$/i, format: (m) => `\u4e86\u89e3\u5173\u4e8e ${m[1]} \u7684\u66f4\u591a\u4fe1\u606f` },
    { regex: /^Open\s+(.+)\s+Preferences$/i, format: (m) => `\u6253\u5f00 ${m[1]} \u504f\u597d\u8bbe\u7f6e` },
    { regex: /^Open\s+(.+)\s+Settings$/i, format: (m) => `\u6253\u5f00 ${m[1]} \u8bbe\u7f6e` },
    { regex: /^Configure\s+(.+)$/i, format: (m) => `\u914d\u7f6e ${m[1]}` },
    { regex: /^Manage\s+(.+)$/i, format: (m) => `\u7ba1\u7406 ${m[1]}` },
    { regex: /^Enable\s+(.+)$/i, format: (m) => `\u542f\u7528 ${m[1]}` },
    { regex: /^Disable\s+(.+)$/i, format: (m) => `\u7981\u7528 ${m[1]}` },
    { regex: /^Choose\s+a\s+predefined\s+(.+)\s+for\s+the\s+agent\.(.*)$/i, format: (m) => `\u4e3a\u667a\u80fd\u4f53\u9009\u62e9\u9884\u8bbe\u7684 ${m[1]}\u3002${m[2]}` },
    { regex: /^Scan\s+the\s+code\s+to\s+(.+)$/i, format: (m) => `\u626b\u63cf\u4e8c\u7ef4\u7801\u4ee5 ${m[1]}` }
  ];

  // 3. Time Unit Chinese Lookup Map
  const UNIT_MAP_CN = {
    'mo': '\u4e2a\u6708\u524d',
    'month': '\u4e2a\u6708\u524d',
    'months': '\u4e2a\u6708\u524d',
    'd': '\u5929\u524d',
    'day': '\u5929\u524d',
    'days': '\u5929\u524d',
    'm': '\u5206\u949f\u524d',
    'min': '\u5206\u949f\u524d',
    'mins': '\u5206\u949f\u524d',
    'minute': '\u5206\u949f\u524d',
    'minutes': '\u5206\u949f\u524d',
    'h': '\u5c0f\u65f6\u524d',
    'hr': '\u5c0f\u65f6\u524d',
    'hrs': '\u5c0f\u65f6\u524d',
    'hour': '\u5c0f\u65f6\u524d',
    'hours': '\u5c0f\u65f6\u524d',
    's': '\u79d2\u524d',
    'sec': '\u79d2\u524d',
    'secs': '\u79d2\u524d',
    'second': '\u79d2\u524d',
    'seconds': '\u79d2\u524d',
    'y': '\u5e74\u524d',
    'yr': '\u5e74\u524d',
    'yrs': '\u5e74\u524d',
    'year': '\u5e74\u524d',
    'years': '\u5e74\u524d'
  };

  // 4. Strict Safety Bypass Elements & Ancestor Selectors
  const IGNORE_TAGS = new Set([
    'SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'CANVAS',
    'SVG', 'MATH', 'OBJECT', 'EMBED'
  ]);

  const CODE_OR_INPUT_TAGS = new Set([
    'PRE', 'CODE', 'KBD', 'SAMP', 'VAR', 'TEXTAREA'
  ]);

  const BUTTON_INPUT_TYPES = new Set([
    'button', 'submit', 'reset'
  ]);

  const SAFE_ATTRS = ['placeholder', 'title', 'aria-label'];

  const BYPASS_ANCESTOR_SELECTOR = [
    '.monaco-editor',
    '.view-lines',
    '.monaco-list-row',
    '.cm-editor',
    '.cm-content',
    '.editor-instance',
    '.monaco-tokenized-source',
    'pre',
    'code',
    'kbd',
    'samp',
    'var',
    '.code-block',
    '.hljs',
    '.syntax-highlighted',
    '.highlight',
    '.terminal',
    '.xterm',
    '.xterm-screen',
    '.xterm-viewport',
    '.terminal-wrapper',
    'textarea',
    '[contenteditable="true"]',
    '[contenteditable=""]',
    '[contenteditable]:not([contenteditable="false"])',
    '[data-no-translate]',
    '[translate="no"]',
    'svg',
    'canvas'
  ].join(', ');

  // Helper: Normalize non-breaking space
  function normalize(str) {
    if (!str) return '';
    return str.replace(/\u00a0/g, ' ');
  }

  // Helper: Format timer unit (ms vs s)
  function formatTimerUnit(unit) {
    if (!unit) return '\u79d2';
    return unit.toLowerCase().startsWith('ms') ? '\u6beb\u79d2' : '\u79d2';
  }

  // 5. Dynamic Pattern Matcher Pipeline
  function matchDynamicPatterns(trimmed) {
    let m;

    // Live Thinking Timer State
    if ((m = trimmed.match(/^(?:Thinking|Thought)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
      return `\u601d\u8003\u4e2d (${m[1]}${formatTimerUnit(m[2])})`;
    }
    if ((m = trimmed.match(/^Thinking\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$/i))) {
      return `\u601d\u8003\u4e2d... (${m[1]}${formatTimerUnit(m[2])})`;
    }
    if ((m = trimmed.match(/^(?:Thinking|Thought)\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$/i)) ||
        (m = trimmed.match(/^(?:Thinking|Thought)\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$/i))) {
      return `\u601d\u8003\u4e2d (${m[1]}${formatTimerUnit(m[2])})`;
    }

    // Live Working Timer State
    if ((m = trimmed.match(/^(?:Working|Worked)\s+for\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
      return `\u5904\u7406\u4e2d (${m[1]}${formatTimerUnit(m[2])})`;
    }
    if ((m = trimmed.match(/^Working\.\.\.\s*\(?(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)?$/i))) {
      return `\u5904\u7406\u4e2d... (${m[1]}${formatTimerUnit(m[2])})`;
    }
    if ((m = trimmed.match(/^(?:Working|Worked)\s*\((\d+(?:\.\d+)?)\s*(s|seconds?|ms)?\)$/i)) ||
        (m = trimmed.match(/^(?:Working|Worked)\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)$/i))) {
      return `\u5904\u7406\u4e2d (${m[1]}${formatTimerUnit(m[2])})`;
    }

    // Completion & Execution Duration Timers
    if ((m = trimmed.match(/^(Completed|Finished|Done)\s+in\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
      return `\u5df2\u5b8c\u6210 (\u8017\u65f6 ${m[2]}${formatTimerUnit(m[3])})`;
    }
    if ((m = trimmed.match(/^Timed\s+(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
      return `\u5df2\u8ba1\u65f6 ${m[1]}${formatTimerUnit(m[2])}`;
    }
    if ((m = trimmed.match(/^Elapsed\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
      return `\u8017\u65f6: ${m[1]}${formatTimerUnit(m[2])}`;
    }
    if ((m = trimmed.match(/^Total\s+duration:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
      return `\u603b\u8017\u65f6: ${m[1]}${formatTimerUnit(m[2])}`;
    }
    if ((m = trimmed.match(/^Execution\s+time:\s*(\d+(?:\.\d+)?)\s*(s|seconds?|ms)?$/i))) {
      return `\u6267\u884c\u8017\u65f6: ${m[1]}${formatTimerUnit(m[2])}`;
    }

    // Relative Times
    if (/^just\s+now$/i.test(trimmed)) return '\u521a\u521a';
    if (/^a\s+few\s+seconds\s+ago$/i.test(trimmed)) return '\u51e0\u79d2\u524d';
    if (/^a\s+minute\s+ago$/i.test(trimmed)) return '1\u5206\u949f\u524d';
    if (/^an\s+hour\s+ago$/i.test(trimmed)) return '1\u5c0f\u65f6\u524d';
    if (/^a\s+day\s+ago$/i.test(trimmed)) return '1\u5929\u524d';
    if (/^today$/i.test(trimmed)) return '\u4eca\u5929';
    if (/^yesterday$/i.test(trimmed)) return '\u6628\u5929';

    if (trimmed.startsWith('Today ')) return trimmed.replace('Today ', '\u4eca\u5929 ');
    if (trimmed.startsWith('Yesterday ')) return trimmed.replace('Yesterday ', '\u6628\u5929 ');

    // Compact Relative Timestamps: 10d, 5m, 1mo, 2h, 30s, 1y (with optional 'ago')
    if ((m = trimmed.match(/^(\d+)\s*(mo|[dmhsy])(?:\s+ago)?$/i))) {
      const unit = m[2].toLowerCase();
      const cn = UNIT_MAP_CN[unit];
      if (cn) return `${m[1]}${cn}`;
    }

    // Verbose Relative Timestamps: 5 minutes ago, 2 days ago, 1 month ago
    if ((m = trimmed.match(/^(\d+)\s*(months?|days?|hours?|hrs?|minutes?|mins?|seconds?|secs?|years?|yrs?)\s+ago$/i))) {
      const unit = m[2].toLowerCase();
      const cn = UNIT_MAP_CN[unit];
      if (cn) return `${m[1]}${cn}`;
    }

    // Dynamic Pane Badges & Workspace Counters
    if ((m = trimmed.match(/^(Subagents|Files Changed|Artifacts|Uploads|Background Tasks|MCP Servers|Skills)\s+(\d+)$/i))) {
      const typeMap = {
        'subagents': '\u5b50\u667a\u80fd\u4f53',
        'files changed': '\u5df2\u4fee\u6539\u6587\u4ef6',
        'artifacts': '\u4ea7\u7269',
        'uploads': '\u5df2\u4e0a\u4f20\u6587\u4ef6',
        'background tasks': '\u540e\u53f0\u4efb\u52a1',
        'mcp servers': 'MCP \u670d\u52a1',
        'skills': '\u6280\u80fd'
      };
      const label = typeMap[m[1].toLowerCase()] || m[1];
      return `${label} ${m[2]}`;
    }

    // File change counters
    if ((m = trimmed.match(/^(\d+)\s+files?\s+changed$/i))) return `${m[1]} \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539`;
    if ((m = trimmed.match(/^(\d+)\s+files?\s+modified$/i))) return `${m[1]} \u4e2a\u6587\u4ef6\u5df2\u4fee\u6539`;
    if ((m = trimmed.match(/^(\d+)\s+files?\s+added$/i))) return `${m[1]} \u4e2a\u6587\u4ef6\u5df2\u6dfb\u52a0`;
    if ((m = trimmed.match(/^(\d+)\s+files?\s+deleted$/i))) return `${m[1]} \u4e2a\u6587\u4ef6\u5df2\u5220\u9664`;
    if ((m = trimmed.match(/^(\d+)\s+files?$/i))) return `${m[1]} \u4e2a\u6587\u4ef6`;

    // Agent and Item Counters
    if ((m = trimmed.match(/^(\d+)\s+subagents?$/i))) return `${m[1]} \u4e2a\u5b50\u667a\u80fd\u4f53`;
    if ((m = trimmed.match(/^(\d+)\s+agents?\s+running$/i))) return `${m[1]} \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d`;
    if (/^No\s+agents?\s+running$/i.test(trimmed)) return '0 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d';
    if (/^1\s+agent\s+running$/i.test(trimmed)) return '1 \u4e2a\u667a\u80fd\u4f53\u8fd0\u884c\u4e2d';
    if ((m = trimmed.match(/^(\d+)\s+items?\s+selected$/i))) return `\u5df2\u9009 ${m[1]} \u9879`;
    if ((m = trimmed.match(/^(\d+)\s+selected$/i))) return `\u5df2\u9009 ${m[1]} \u9879`;
    if ((m = trimmed.match(/^(\d+)\s+tasks?$/i))) return `${m[1]} \u4e2a\u4efb\u52a1`;
    if ((m = trimmed.match(/^(\d+)\s+artifacts?$/i))) return `${m[1]} \u4e2a\u4ea7\u7269`;
    if ((m = trimmed.match(/^(\d+)\s+changes?$/i))) return `${m[1]} \u5904\u66f4\u6539`;
    if ((m = trimmed.match(/^(\d+)\s+errors?$/i))) return `${m[1]} \u4e2a\u9519\u8bef`;
    if ((m = trimmed.match(/^(\d+)\s+warnings?$/i))) return `${m[1]} \u4e2a\u8b66\u544a`;
    if ((m = trimmed.match(/^(\d+)\s+results?$/i))) return `${m[1]} \u4e2a\u7ed3\u679c`;

    // Dynamic Templates
    for (let i = 0; i < DYNAMIC_TEMPLATES.length; i++) {
      const tmpl = DYNAMIC_TEMPLATES[i];
      if ((m = trimmed.match(tmpl.regex))) {
        return tmpl.format(m);
      }
    }

    return null;
  }

  // 6. Master Text Translation Dispatcher
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

    // 2. Dynamic regex & template matchers
    const dynamicMatch = matchDynamicPatterns(trimmed);
    if (dynamicMatch !== null) {
      return normalized.replace(trimmed, dynamicMatch);
    }

    return null;
  }

  // 7. Safety Bypass Checks
  function isBypassedElement(el) {
    if (!el || el.nodeType !== 1) return false;
    if (IGNORE_TAGS.has(el.tagName)) return true;
    if (el.isContentEditable) return true;
    if (el.getAttribute && el.getAttribute('contenteditable') === 'true') return true;

    if (el.matches && el.matches(BYPASS_ANCESTOR_SELECTOR)) return true;
    if (el.closest && el.closest(BYPASS_ANCESTOR_SELECTOR)) return true;

    const className = (typeof el.className === 'string') ? el.className : (el.getAttribute ? (el.getAttribute('class') || '') : '');
    if (className) {
      const bypassClasses = ['monaco-editor', 'view-lines', 'monaco-list-row', 'terminal', 'xterm', 'code-block', 'hljs', 'cm-editor', 'cm-content'];
      for (let i = 0; i < bypassClasses.length; i++) {
        if (className.includes(bypassClasses[i])) return true;
      }
    }
    return false;
  }

  function isBypassedNode(node) {
    if (!node) return true;
    if (node.nodeType === 3) {
      const parent = node.parentElement || node.parentNode;
      if (!parent || parent.nodeType !== 1) return false;
      const parentTag = parent.tagName ? parent.tagName.toUpperCase() : '';
      if (IGNORE_TAGS.has(parentTag) || CODE_OR_INPUT_TAGS.has(parentTag)) return true;
      if (parent.isContentEditable) return true;
      if (parent.closest && parent.closest(BYPASS_ANCESTOR_SELECTOR)) return true;
      return isBypassedElement(parent);
    }
    if (node.nodeType === 1) {
      return isBypassedElement(node);
    }
    return false;
  }

  function translateAttributes(el, attrs) {
    if (!el || !el.getAttribute) return;
    for (let i = 0; i < attrs.length; i++) {
      const attr = attrs[i];
      if (el.hasAttribute && el.hasAttribute(attr)) {
        const val = el.getAttribute(attr);
        if (val && typeof val === 'string') {
          const trans = translateText(val);
          if (trans !== null && trans !== val) {
            el.setAttribute(attr, trans);
          }
        }
      }
    }
  }

  // 8. Recursive DOM and Shadow DOM Walker
  function walk(node) {
    if (!node) return;

    // Text Node (Type 3)
    if (node.nodeType === 3) {
      if (isBypassedNode(node)) return;
      const text = node.nodeValue;
      if (text && typeof text === 'string') {
        const trans = translateText(text);
        if (trans !== null && trans !== text) {
          node.nodeValue = trans;
        }
      }
      return;
    }

    // DocumentFragment / ShadowRoot (Type 11)
    if (node.nodeType === 11) {
      for (let child = node.firstChild; child; child = child.nextSibling) {
        walk(child);
      }
      return;
    }

    // Element Node (Type 1)
    if (node.nodeType === 1) {
      const tag = node.tagName ? node.tagName.toUpperCase() : '';

      // Ignore script, style, svg, canvas, etc.
      if (IGNORE_TAGS.has(tag)) return;

      // Textarea: translate safe attributes only
      if (tag === 'TEXTAREA') {
        translateAttributes(node, SAFE_ATTRS);
        return;
      }

      // Input elements
      if (tag === 'INPUT') {
        const itype = (node.getAttribute('type') || 'text').toLowerCase();
        if (BUTTON_INPUT_TYPES.has(itype)) {
          translateAttributes(node, [...SAFE_ATTRS, 'value']);
        } else {
          translateAttributes(node, SAFE_ATTRS);
        }
        return;
      }

      // Protected Containers & Code Blocks: prune subtree
      const isSelfBypassed = (
        CODE_OR_INPUT_TAGS.has(tag) ||
        (node.matches && node.matches(BYPASS_ANCESTOR_SELECTOR)) ||
        isBypassedElement(node)
      );

      if (isSelfBypassed) {
        translateAttributes(node, SAFE_ATTRS);
        return;
      }

      // Normal Element: Translate safe attributes
      translateAttributes(node, SAFE_ATTRS);

      // Traverse Open Shadow DOM
      if (node.shadowRoot) {
        observeRoot(node.shadowRoot);
        walk(node.shadowRoot);
      }

      // Traverse Child Nodes
      for (let child = node.firstChild; child; child = child.nextSibling) {
        walk(child);
      }
    }
  }

  // 9. MutationObserver Setup & Lifecycle
  let observer = null;
  const observedRoots = new WeakSet();
  const observerConfig = {
    childList: true,
    subtree: true,
    characterData: true,
    attributes: true
  };

  function observeRoot(root) {
    if (!root || !observer || observedRoots.has(root)) return;
    try {
      observedRoots.add(root);
      observer.observe(root, observerConfig);
    } catch (e) {
      // Fail-safe
    }
  }

  function startObserver() {
    if (observer) return;
    if (typeof MutationObserver === 'undefined') return;

    observer = new MutationObserver(mutations => {
      for (let i = 0; i < mutations.length; i++) {
        const m = mutations[i];
        if (m.type === 'childList') {
          for (let j = 0; j < m.addedNodes.length; j++) {
            const added = m.addedNodes[j];
            if (added.nodeType === 1 && added.shadowRoot) {
              observeRoot(added.shadowRoot);
            }
            walk(added);
          }
        } else if (m.type === 'characterData') {
          const node = m.target;
          if (!isBypassedNode(node)) {
            const trans = translateText(node.nodeValue);
            if (trans !== null && trans !== node.nodeValue) {
              node.nodeValue = trans;
            }
          }
        } else if (m.type === 'attributes') {
          const el = m.target;
          if (el.nodeType === 1 && !isBypassedElement(el)) {
            walk(el);
          }
        }
      }
    });

    // Observe documentElement to catch all roots, portals, and body changes
    if (typeof document !== 'undefined') {
      if (document.documentElement) observeRoot(document.documentElement);
      if (document.body) observeRoot(document.body);
    }
  }

  // 10. Intercept Element.prototype.attachShadow for dynamic Web Components
  if (typeof Element !== 'undefined' && Element.prototype && Element.prototype.attachShadow) {
    const origAttachShadow = Element.prototype.attachShadow;
    Element.prototype.attachShadow = function(init) {
      const shadowRoot = origAttachShadow.apply(this, arguments);
      try {
        if (shadowRoot) {
          observeRoot(shadowRoot);
          walk(shadowRoot);
        }
      } catch (e) {
        // Fail-safe
      }
      return shadowRoot;
    };
  }

  // 11. Periodic Background Micro-Sweep (Guarantees zero-reversion on React state updates)
  function startPeriodicSweep() {
    if (typeof window === 'undefined' || typeof document === 'undefined') return;
    
    const sweep = () => {
      try {
        if (document.documentElement) {
          walk(document.documentElement);
        }
      } catch (e) {}
    };

    // Fast sweep on user interactions & tab focus
    window.addEventListener('focus', sweep, { passive: true });
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible') sweep();
    }, { passive: true });
    window.addEventListener('popstate', sweep, { passive: true });
    window.addEventListener('hashchange', sweep, { passive: true });

    // Periodic heartbeat sweep every 1.5s
    setInterval(sweep, 1500);
  }

  // 12. Hook DOM Ready State
  if (typeof document !== 'undefined') {
    const init = () => {
      walk(document.documentElement || document.body);
      startObserver();
      startPeriodicSweep();
    };

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  }

  // 13. Global CommonJS Exports for testing
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      dictionary,
      DYNAMIC_TEMPLATES,
      UNIT_MAP_CN,
      normalize,
      formatTimerUnit,
      matchDynamicPatterns,
      translateText,
      isBypassedElement,
      isBypassedNode,
      walk,
      startObserver
    };
  }
})();
