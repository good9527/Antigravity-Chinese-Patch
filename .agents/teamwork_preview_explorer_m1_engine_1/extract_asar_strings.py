import struct, json, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

asar_path = os.path.join(os.path.dirname(__file__), '..', '..', 'app.asar')
with open(asar_path, 'rb') as f:
    magic, header_size, header_len, json_len = struct.unpack('<IIII', f.read(16))
    header = json.loads(f.read(json_len).decode('utf-8'))
    data_start = 8 + header_size

    def extract_file(node, path):
        parts = path.split('/')
        curr = node['files']
        for p in parts[:-1]:
            curr = curr[p]['files']
        info = curr[parts[-1]]
        f.seek(data_start + int(info['offset']))
        return f.read(info['size'])

    def list_files(d, prefix=''):
        files = []
        for k, v in d.items():
            if 'files' in v:
                files.extend(list_files(v['files'], prefix + k + '/'))
            else:
                files.append(prefix + k)
        return files

    all_files = list_files(header.get('files', {}))
    print(f'Total files in app.asar: {len(all_files)}')

    all_strings = set()
    for file_path in all_files:
        if file_path.endswith(('.js', '.json', '.html')):
            try:
                content = extract_file(header, file_path).decode('utf-8', errors='ignore')
                for match in re.finditer(r'["\']([A-Z][A-Za-z0-9\s_\-\:\.\,\?\!\'\/\(\)]{2,80})["\']', content):
                    s = match.group(1).strip()
                    if len(s) >= 3 and not s.startswith('http') and not s.startswith('/') and not s.startswith('node_modules'):
                        all_strings.add(s)
            except Exception as e:
                pass

    print(f'Extracted {len(all_strings)} string candidates from ASAR')

    # Filter by interesting categories
    keywords = [
        'Agent', 'Model', 'Quota', 'Token', 'Setting', 'Theme', 'Update', 'File', 'Workspace',
        'Server', 'Tool', 'Prompt', 'Error', 'Failed', 'Success', 'Task', 'Conversation',
        'Window', 'Terminal', 'Debug', 'DevTools', 'Log', 'Help', 'Doc', 'Permission',
        'Sandbox', 'Security', 'Allow', 'Deny', 'Accept', 'Reject', 'Apply', 'Discard',
        'Review', 'History', 'Browse', 'Upload', 'Download', 'Install', 'Extension', 'MCP',
        'Google', 'Credits', 'Billing', 'Usage', 'Rate', 'Limit', 'Search', 'Filter',
        'Export', 'Import', 'Pin', 'Delete', 'Rename', 'Restart', 'Refresh', 'Clear'
    ]

    matched_strings = [s for s in all_strings if any(kw in s for kw in keywords)]
    print(f'Found {len(matched_strings)} candidate UI strings matching keywords')
    with open('matched_asar_strings.txt', 'w', encoding='utf-8') as out:
        for s in sorted(matched_strings):
            out.write(s + '\n')
