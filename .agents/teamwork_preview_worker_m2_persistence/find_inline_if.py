import glob, re

for pattern in ["*.ps1", "watcher/*.ps1"]:
    for path in glob.glob(pattern):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for idx, line in enumerate(lines, 1):
            if re.search(r'-ForegroundColor\s+\(if\b', line):
                print(f"{path}:{idx}: {line.strip()}")
            elif re.search(r'\bexit\s+\(if\b', line):
                print(f"{path}:{idx}: {line.strip()}")
            elif re.search(r'\breturn\s+\(if\b', line):
                print(f"{path}:{idx}: {line.strip()}")
