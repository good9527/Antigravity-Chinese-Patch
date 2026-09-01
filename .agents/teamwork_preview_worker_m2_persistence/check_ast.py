import subprocess

ps_script = """
$tokens = $null
$errs = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path "install.ps1").Path, [ref]$tokens, [ref]$errs)
foreach ($t in $tokens) {
    if ($t.Extent.StartLineNumber -ge 645 -and $t.Extent.StartLineNumber -le 665) {
        Write-Host ($t.Extent.StartLineNumber.ToString() + ":" + $t.Extent.StartColumnNumber + " [" + $t.Kind + "] => " + $t.Extent.Text)
    }
}
"""

res = subprocess.run(["powershell.exe", "-Command", ps_script], capture_output=True, text=True)
print("STDOUT:\n" + res.stdout)
print("STDERR:\n" + res.stderr)
