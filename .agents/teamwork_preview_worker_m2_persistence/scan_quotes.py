with open('install.ps1', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    q_count = line.count('"')
    s_count = line.count("'")
    if q_count % 2 != 0:
        print(f"Line {idx} odd double-quotes ({q_count}): {repr(line)}")
    if s_count % 2 != 0:
        print(f"Line {idx} odd single-quotes ({s_count}): {repr(line)}")
