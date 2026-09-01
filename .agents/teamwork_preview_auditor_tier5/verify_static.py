import json
import os
import re
import sys

def verify_static():
    results = {}
    repo_root = r"C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch"
    
    # 1. dictionary.json
    dict_path = os.path.join(repo_root, "dist", "dictionary.json")
    with open(dict_path, "r", encoding="utf-8") as f:
        content_raw = f.read()
        
    # Check UTF-8 validity & decoding
    data = json.loads(content_raw)
    key_count = len(data)
    
    # Check duplicates by parsing raw JSON tokens
    # Using a custom decoder to catch duplicate keys
    duplicates = []
    def dict_raise_on_duplicates(ordered_pairs):
        seen = set()
        for k, v in ordered_pairs:
            if k in seen:
                duplicates.append(k)
            seen.add(k)
        return dict(ordered_pairs)
    
    json.loads(content_raw, object_pairs_hook=dict_raise_on_duplicates)
    
    # Check for typo "已修政"
    typo_found = "已修政" in content_raw
    
    results["dictionary"] = {
        "key_count": key_count,
        "duplicates": duplicates,
        "duplicate_count": len(duplicates),
        "typo_已修政_present": typo_found,
        "utf8_valid": True
    }
    
    # 2. preload.js and engine.js pure 7-bit ASCII Unicode escapes
    for fname in ["preload.js", "engine.js"]:
        fpath = os.path.join(repo_root, "dist", fname)
        with open(fpath, "rb") as f:
            raw_bytes = f.read()
        max_byte = max(raw_bytes) if raw_bytes else 0
        non_ascii_indices = [i for i, b in enumerate(raw_bytes) if b > 127]
        results[fname] = {
            "size_bytes": len(raw_bytes),
            "max_byte": max_byte,
            "is_pure_ascii": max_byte <= 127,
            "non_ascii_count": len(non_ascii_indices)
        }
        
    # 3. Check for process killing keywords in scripts
    proc_kill_patterns = [
        r"taskkill",
        r"Stop-Process",
        r"killall",
        r"pkill",
        r"kill\s+-9",
        r"kill\s+\$\(pgrep"
    ]
    script_files = ["install.ps1", "install.sh", "patch_antigravity.ps1", "watcher/watcher.ps1", "watcher/auto_heal.sh"]
    process_killing_findings = {}
    for sfile in script_files:
        sfpath = os.path.join(repo_root, sfile)
        if os.path.exists(sfpath):
            with open(sfpath, "r", encoding="utf-8", errors="ignore") as f:
                scontent = f.read()
            matches = {}
            for pat in proc_kill_patterns:
                found = re.findall(pat, scontent, re.IGNORECASE)
                if found:
                    matches[pat] = found
            process_killing_findings[sfile] = matches
        else:
            process_killing_findings[sfile] = "FILE_NOT_FOUND"
            
    results["process_killing"] = process_killing_findings
    
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    verify_static()
