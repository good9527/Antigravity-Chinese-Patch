import subprocess

with open('install.ps1', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.index("Function Invoke-InstallPatch {")
end_idx = text.index("# 11. Parameter Routing Dispatcher")
func_text = text[start_idx:end_idx]

ps_script = f"""
$tokens = $null
$errs = $null
[System.Management.Automation.Language.Parser]::ParseInput(@'
{func_text}
'@, [ref]$tokens, [ref]$errs)
foreach ($e in $errs) {{
    Write-Host ("ERROR in Invoke-InstallPatch: " + $e.Message + " at Line " + $e.Extent.StartLineNumber + ":" + $e.Extent.StartColumnNumber)
}}
"""

res = subprocess.run(["powershell.exe", "-Command", ps_script], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("STDOUT:\n" + res.stdout)
print("STDERR:\n" + res.stderr)
