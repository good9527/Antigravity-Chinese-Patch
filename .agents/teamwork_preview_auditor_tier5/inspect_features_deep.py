import os
import json
import re

def inspect_features_deep():
    repo_root = r"C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch"
    
    with open(os.path.join(repo_root, "dist", "preload.js"), "r", encoding="utf-8") as f:
        preload_js = f.read()
        
    # Let's decode unicode escapes in preload_js to see readable JS
    decoded_preload_js = preload_js.encode("utf-8").decode("unicode_escape")
    
    with open(os.path.join(repo_root, "install.ps1"), "r", encoding="utf-8") as f:
        install_ps1 = f.read()
        
    checks = {
        "F06_compact_time": [
            "re_compact_time" in decoded_preload_js or "reCompactTime" in decoded_preload_js or "天前" in decoded_preload_js,
            "Matches: " + str(re.findall(r"(\d+\s*\(?mo\||\d+.*天前|天前)", decoded_preload_js)[:3])
        ],
        "F07_suffixed_time": [
            "re_verbose_time" in decoded_preload_js or "reVerboseTime" in decoded_preload_js or "ago" in decoded_preload_js,
            "Matches: " + str(re.findall(r"(ago|verbose)", decoded_preload_js)[:3])
        ],
        "F10_working_timer": [
            "re_working" in decoded_preload_js or "reWorking" in decoded_preload_js or "处理中" in decoded_preload_js,
            "Matches: " + str(re.findall(r"(Working|Worked|处理中)", decoded_preload_js)[:3])
        ],
        "F11_completion_duration": [
            "re_completed" in decoded_preload_js or "reCompleted" in decoded_preload_js or "已完成" in decoded_preload_js,
            "Matches: " + str(re.findall(r"(Completed|Finished|Done|已完成)", decoded_preload_js)[:3])
        ],
        "F33_cli_flags": [
            "$Install" in install_ps1 and "$Check" in install_ps1 and "$Restore" in install_ps1 and "$Uninstall" in install_ps1,
            "Matches: " + str(re.findall(r"(\$Install|\$Check|\$Restore|\$Uninstall|\$Daemon)", install_ps1)[:5])
        ]
    }
    
    print(json.dumps(checks, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    inspect_features_deep()
