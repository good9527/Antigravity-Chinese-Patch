import os
import sys
import subprocess
import json
import struct
import tempfile
import shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def run_pwsh(cmd):
    p = subprocess.run(["pwsh", "-NoProfile", "-Command", cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr

def run_bash(cmd):
    p = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout, p.stderr

def main():
    repo_root = r"C:\Users\19901\.gemini\antigravity\scratch\Antigravity-Chinese-Patch"
    results = {}
    
    # 1. PowerShell syntax validation
    ps_scripts = ["install.ps1", "patch_antigravity.ps1", "watcher/watcher.ps1"]
    ps_syntax_results = {}
    for s in ps_scripts:
        spath = os.path.join(repo_root, s)
        code, out, err = run_pwsh(f"$errors = $null; [System.Management.Automation.Language.Parser]::ParseFile('{spath}', [ref]$null, [ref]$errors); if ($errors) {{ $errors | ForEach-Object {{ $_.Message }} }} else {{ 'SYNTAX_OK' }}")
        ps_syntax_results[s] = {"exit_code": code, "output": out.strip(), "errors": err.strip()}
    results["powershell_syntax"] = ps_syntax_results

    # 2. Bash syntax validation
    sh_scripts = ["install.sh", "watcher/auto_heal.sh"]
    sh_syntax_results = {}
    for s in sh_scripts:
        spath = os.path.join(repo_root, s).replace("\\", "/")
        code, out, err = run_bash(f"bash -n '{spath}' && echo SYNTAX_OK")
        sh_syntax_results[s] = {"exit_code": code, "output": out.strip(), "errors": err.strip()}
    results["bash_syntax"] = sh_syntax_results

    # 3. Live ASAR In-Place C# Patcher Verification
    temp_dir = tempfile.mkdtemp(prefix="live_asar_audit_")
    try:
        sample_asar = os.path.join(temp_dir, "app.asar")
        sample_patched = os.path.join(temp_dir, "app.asar.patched")
        
        # Pack valid ASAR
        header_files = {
            "dist": {
                "files": {
                    "preload.js": {"size": 40, "offset": "0"},
                    "main.js": {"size": 25, "offset": "40"}
                }
            },
            "package.json": {"size": 32, "offset": "65"}
        }
        header_json = json.dumps({"files": header_files}, separators=(",", ":")).encode("utf-8")
        json_size = len(header_json)
        padding = (4 - (json_size % 4)) % 4
        payload = b"console.log('Original Host Preload Code');" + b"console.log('Main Code');" + b'{"version":"2.10.0","name":"agy"}'
        
        with open(sample_asar, "wb") as f:
            f.write(struct.pack("<IIII", 4, json_size + padding + 8, json_size + padding + 4, json_size))
            f.write(header_json)
            if padding > 0:
                f.write(b"\x00" * padding)
            f.write(payload)

        # Extract UniversalAsarEngine C# code from install.ps1 directly
        with open(os.path.join(repo_root, "install.ps1"), "r", encoding="utf-8") as f:
            install_src = f.read()
        
        csharp_start = install_src.index("$csharpPatcher = @'") + len("$csharpPatcher = @'\n")
        csharp_end = install_src.index("'@\n", csharp_start)
        csharp_code = install_src[csharp_start:csharp_end]

        csharp_test_file = os.path.join(temp_dir, "test_csharp.ps1")
        with open(csharp_test_file, "w", encoding="utf-8") as f:
            f.write(f"""
            $code = @'
{csharp_code}
'@
            Add-Type -TypeDefinition $code -Language CSharp
            $patch = "// Antigravity Chinese Localization Patch`nconsole.log('PATCHED_LIVE');"
            [UniversalAsarEngine]::InjectPreload('{sample_asar.replace('\\', '/')}', '{sample_patched.replace('\\', '/')}', $patch)
            $ver = [UniversalAsarEngine]::ReadPackageVersion('{sample_patched.replace('\\', '/')}')
            Write-Output "VER:$ver"
            """)

        code, out, err = run_pwsh(f"& '{csharp_test_file}'")
        
        # Verify patched ASAR
        with open(sample_patched, "rb") as f:
            patched_bytes = f.read()
        magic, u2, u3, jsize = struct.unpack("<IIII", patched_bytes[:16])
        p_header = json.loads(patched_bytes[16:16+jsize].decode("utf-8"))
        p_offset = int(p_header["files"]["dist"]["files"]["preload.js"]["offset"])
        p_size = int(p_header["files"]["dist"]["files"]["preload.js"]["size"])
        p_content = patched_bytes[8 + u2 + p_offset : 8 + u2 + p_offset + p_size].decode("utf-8")

        results["live_csharp_asar_injection"] = {
            "exit_code": code,
            "version_read": "2.10.0" in out,
            "patch_marker_in_preload": "// Antigravity Chinese Localization Patch" in p_content,
            "original_preload_preserved": "Original Host Preload Code" in p_content,
            "new_code_in_preload": "PATCHED_LIVE" in p_content,
            "header_valid": magic == 4
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print(json.dumps(results, indent=2, ensure_ascii=True))

if __name__ == "__main__":
    main()
