import os
import json
import re
import sys

def verify_anti_cheating():
    repo_root = r"C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch"
    findings = {
        "facade_detections": [],
        "hardcoded_shortcuts": [],
        "prepopulated_artifacts": [],
        "feature_inventory_verification": {}
    }
    
    # 1. Check for prepopulated artifacts in workspace (excluding node_modules or system files)
    flagged_artifacts = []
    for root, dirs, files in os.walk(repo_root):
        if "node_modules" in root or ".git" in root or "app.asar.unpacked" in root or ".agents" in root:
            continue
        for f in files:
            if f.endswith(".log") or "result" in f.lower() or "attestation" in f.lower():
                flagged_artifacts.append(os.path.relpath(os.path.join(root, f), repo_root))
    findings["prepopulated_artifacts"] = flagged_artifacts

    # 2. Check for dummy / facade functions: `def ...: return True` or `return <const>` in implementation files
    impl_files = [
        "dist/preload.js", "dist/engine.js", "install.ps1", "install.sh", "patch_antigravity.ps1",
        "watcher/watcher.ps1", "watcher/auto_heal.sh"
    ]
    for rel_path in impl_files:
        fpath = os.path.join(repo_root, rel_path)
        if not os.path.exists(fpath):
            findings["facade_detections"].append(f"Missing file: {rel_path}")
            continue
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Check for NotImplementedError, mock passes, or trivial bodies
        if "NotImplementedError" in content or "TODO: implement" in content or "mock" in content.lower():
            # In test files it might be okay, but in impl files it's suspicious
            findings["facade_detections"].append(f"{rel_path} contains potential mock/todo marker")

    # 3. Verify all 36 features F01 - F36 against source code
    # Load dist/preload.js, dist/dictionary.json, install.ps1, install.sh, patch_antigravity.ps1, watcher files
    with open(os.path.join(repo_root, "dist", "dictionary.json"), "r", encoding="utf-8") as f:
        dict_data = json.load(f)
    with open(os.path.join(repo_root, "dist", "preload.js"), "r", encoding="utf-8") as f:
        preload_js = f.read()
    with open(os.path.join(repo_root, "install.ps1"), "r", encoding="utf-8") as f:
        install_ps1 = f.read()
    with open(os.path.join(repo_root, "install.sh"), "r", encoding="utf-8") as f:
        install_sh = f.read()
    with open(os.path.join(repo_root, "patch_antigravity.ps1"), "r", encoding="utf-8") as f:
        patch_ps1 = f.read()
    with open(os.path.join(repo_root, "watcher", "watcher.ps1"), "r", encoding="utf-8") as f:
        watcher_ps1 = f.read()
    with open(os.path.join(repo_root, "watcher", "auto_heal.sh"), "r", encoding="utf-8") as f:
        auto_heal_sh = f.read()
    with open(os.path.join(repo_root, ".github", "workflows", "release.yml"), "r", encoding="utf-8") as f:
        ci_yml = f.read()

    features = {
        "F01": ("Primary Navigation Items", "New Conversation" in dict_data and "Settings" in dict_data),
        "F02": ("Conversation Management", "Untitled Conversation" in dict_data and "Collapse All" in dict_data),
        "F03": ("Auxiliary Panes Headers", "Subagents" in dict_data and "Files Changed" in dict_data and "Artifacts" in dict_data),
        "F04": ("Dynamic Counter Badges", "rePanes" in preload_js or "re_panes" in preload_js or "Subagents" in preload_js),
        "F05": ("File Change Counter", "files?\\s+changed" in preload_js or "reFilesChanged" in preload_js or "个文件已修改" in preload_js),
        "F06": ("Relative Timestamps (Compact)", "reCompactTime" in preload_js or "天前" in preload_js),
        "F07": ("Relative Timestamps (Suffixed)", "reVerboseTime" in preload_js or "minutes?\\s+ago" in preload_js),
        "F08": ("Date Header Prefixes", "Today " in preload_js and "Yesterday " in preload_js),
        "F09": ("Live Thinking Timer State", "Thinking" in preload_js and "formatTimerUnit" in preload_js),
        "F10": ("Live Working Timer State", "Working" in preload_js and "reWorking" in preload_js),
        "F11": ("Execution Completion Duration", "reCompleted" in preload_js and "已完成" in preload_js),
        "F12": ("Static Agent Status Messages", "Thinking..." in dict_data and "Agent finished" in dict_data),
        "F13": ("Review & Action Buttons", "Review" in dict_data and "Accept Step" in dict_data and "Reject Step" in dict_data),
        "F14": ("Settings Modal Navigation", "Account" in dict_data and "Permissions" in dict_data and "Appearance" in dict_data),
        "F15": ("Model Quota & Subscriptions", "Your Plan: Google AI Ultra" in dict_data and "Credits Balance" in dict_data),
        "F16": ("Security & Execution Policies", "Sandbox policy" in dict_data or "Terminal execution" in dict_data or "Terminal Command Execution Policy" in dict_data),
        "F17": ("Appearance & Theme Controls", "Theme Mode" in dict_data and "Font Size" in dict_data),
        "F18": ("Feedback & Diagnostic Modal", "Bug Report" in dict_data and "Feature Request" in dict_data),
        "F19": ("Input Placeholders & Tooltips", "SAFE_ATTRS" in preload_js and "placeholder" in preload_js and "title" in preload_js),
        "F20": ("Application Menus", "File" in dict_data and "View" in dict_data and "Window" in dict_data and "Help" in dict_data),
        "F21": ("System Tray & Agent Count", "reAgentsRunning" in preload_js or "re_agents_running" in preload_js or "agents?\\s+running" in preload_js),
        "F22": ("Splash & Onboarding Overlays", "Loading Antigravity" in dict_data or "Loading Antigravity..." in dict_data or "Setting up Antigravity..." in dict_data),
        "F23": ("Non-Breaking Space Normalizer", "\\u00a0" in preload_js and "normalize" in preload_js),
        "F24": ("Substring Replacement Pipeline", "substringReplacements" in preload_js and "Minimize" in preload_js),
        "F25": ("Monaco Editor & Code Bypass", "monaco-editor" in preload_js and "isBypassedElement" in preload_js),
        "F26": ("User Input Value Protection", "BUTTON_INPUT_TYPES" in preload_js and "textarea" in preload_js),
        "F27": ("In-Place ASAR Injection (.NET)", "UniversalAsarEngine" in install_ps1 and "InjectPreload" in install_ps1),
        "F28": ("In-Place ASAR Injection (Python)", "struct.unpack('<IIII'" in install_sh and "Inject" in install_sh or "python3" in install_sh),
        "F29": ("ASAR Version Extractor", "ReadPackageVersion" in install_ps1 and "package.json" in install_sh),
        "F30": ("Real-Time Auto-Healing Daemon", "FileSystemWatcher" in watcher_ps1 and "auto_heal.sh" in auto_heal_sh),
        "F31": ("Safe Updater Hooking", "pendingUpdateDir" in watcher_ps1 or "WatchPaths" in auto_heal_sh or "antigravity-patch.path" in auto_heal_sh or "antigravity-updater" in watcher_ps1),
        "F32": ("Interactive Elite Console", "Show-Menu" in patch_ps1 and "Apply-Patch" in patch_ps1),
        "F33": ("Non-Interactive CLI Flags", "--install" in install_ps1 and "--check" in install_ps1 and "--restore" in install_ps1),
        "F34": ("CDN Multi-Mirror Waterfall", "Get-CdnFile" in install_ps1 and "fastly.jsdelivr.net" in install_ps1),
        "F35": ("One-Click Backup & Rollback", "Invoke-RestoreBackup" in install_ps1 and "app.asar.bak" in install_ps1),
        "F36": ("Multi-OS CI & Test Suite", "test-matrix" in ci_yml and "package-release" in ci_yml and "test_runner.py" in ci_yml)
    }

    all_passed = True
    for fid, (name, passed) in features.items():
        findings["feature_inventory_verification"][fid] = {
            "name": name,
            "status": "PASS" if passed else "FAIL"
        }
        if not passed:
            all_passed = False

    findings["feature_inventory_all_pass"] = all_passed
    print(json.dumps(findings, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify_anti_cheating()
