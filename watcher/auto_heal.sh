#!/usr/bin/env bash
# auto_heal.sh - macOS / Linux background auto-healing script for Antigravity-Chinese-Patch
# Zero session disruption (no killall/pkill), 100% offline using local cache

set -e

PATCH_DIR="$HOME/.antigravity-chinese-patch"
LOG_FILE="/tmp/antigravity_patch_autoheal.log"
MARKER="// Antigravity Chinese Localization Patch"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] [AutoHeal] $*"
    echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
    echo "$msg"
}

# 1. Locate app.asar across standard platforms and paths
ASAR_PATH=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -f "/Applications/Antigravity.app/Contents/Resources/app.asar" ]; then
        ASAR_PATH="/Applications/Antigravity.app/Contents/Resources/app.asar"
    elif [ -f "$HOME/Applications/Antigravity.app/Contents/Resources/app.asar" ]; then
        ASAR_PATH="$HOME/Applications/Antigravity.app/Contents/Resources/app.asar"
    fi
else
    # Linux standard paths
    if [ -f "/opt/Antigravity/resources/app.asar" ]; then
        ASAR_PATH="/opt/Antigravity/resources/app.asar"
    elif [ -f "/usr/lib/antigravity/resources/app.asar" ]; then
        ASAR_PATH="/usr/lib/antigravity/resources/app.asar"
    elif [ -f "$HOME/.local/share/antigravity/resources/app.asar" ]; then
        ASAR_PATH="$HOME/.local/share/antigravity/resources/app.asar"
    fi
fi

if [ -z "$ASAR_PATH" ] || [ ! -f "$ASAR_PATH" ]; then
    log "Antigravity app.asar not found. Exiting."
    exit 0
fi

# 2. Check if already patched
if grep -q "$MARKER" "$ASAR_PATH" 2>/dev/null; then
    log "app.asar is already patched. Nothing to do."
    exit 0
fi

log "Unpatched official Google update detected at $ASAR_PATH! Re-applying Chinese patch..."

# 3. Locate cached patch code
PRELOAD_PATCH="$PATCH_DIR/preload.js"
if [ ! -f "$PRELOAD_PATCH" ]; then
    # Fallback to local script relative dist/preload.js if running from git clone
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$SCRIPT_DIR/../dist/preload.js" ]; then
        PRELOAD_PATCH="$SCRIPT_DIR/../dist/preload.js"
    fi
fi

if [ ! -f "$PRELOAD_PATCH" ]; then
    log "Error: Cached patch file not found ($PRELOAD_PATCH)."
    exit 1
fi

# 4. In-Place Python 3 ASAR Injection (Zero Process Disruption, Atomic Swap, Retry Loop)
python3 - "$ASAR_PATH" "$PRELOAD_PATCH" << 'EOF'
import sys, os, json, struct, time

asar_path = sys.argv[1]
patch_path = sys.argv[2]
marker = "// Antigravity Chinese Localization Patch"

try:
    with open(patch_path, 'r', encoding='utf-8') as pf:
        patch_full = pf.read()

    if marker in patch_full:
        patch_code = patch_full[patch_full.index(marker):]
    else:
        patch_code = patch_full
except Exception as e:
    print(f"Error reading patch code: {e}", file=sys.stderr)
    sys.exit(1)

max_retries = 5
success = False

for attempt in range(max_retries):
    try:
        with open(asar_path, 'rb') as f:
            header_bytes = f.read(16)
            if len(header_bytes) < 16:
                raise ValueError("ASAR header truncated")
            magic, u2, u3, json_size = struct.unpack('<IIII', header_bytes)
            if magic != 4:
                raise ValueError(f"Invalid ASAR magic: {magic}")

            header_json = f.read(json_size).decode('utf-8')
            header = json.loads(header_json)
            data_start = 8 + u2

            entries = []
            def collect(node, path=''):
                if 'files' in node:
                    for k, v in node['files'].items():
                        collect(v, f'{path}/{k}' if path else k)
                else:
                    is_unpacked = node.get('unpacked', False)
                    offset = int(node.get('offset', 0))
                    size = int(node.get('size', 0))
                    entries.append({
                        'path': path,
                        'node': node,
                        'offset': offset,
                        'size': size,
                        'unpacked': is_unpacked
                    })

            collect(header)
            preload_entry = next((e for e in entries if e['path'].endswith('dist/preload.js') or e['path'].endswith('dist\\preload.js')), None)
            if not preload_entry:
                print("Error: dist/preload.js not found in ASAR", file=sys.stderr)
                sys.exit(1)

            f.seek(data_start + preload_entry['offset'])
            old_preload = f.read(preload_entry['size']).decode('utf-8', errors='ignore')
            if marker in old_preload:
                old_preload = old_preload.split(marker)[0].rstrip()

            new_preload = (old_preload + '\n\n' + patch_code).encode('utf-8')
            preload_entry['new_data'] = new_preload
            preload_entry['node']['size'] = len(new_preload)

            if 'integrity' in preload_entry['node']:
                del preload_entry['node']['integrity']

            entries.sort(key=lambda e: e['offset'])
            cur_offset = 0
            for e in entries:
                if e['unpacked']:
                    continue
                e['node']['offset'] = str(cur_offset)
                cur_offset += len(e.get('new_data', b'')) if 'new_data' in e else e['size']

            new_json_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
            new_json_size = len(new_json_bytes)
            padding = (4 - (new_json_size % 4)) % 4
            header_payload = new_json_size + padding

            tmp_out = asar_path + '.autoheal.tmp'
            with open(tmp_out, 'wb') as out:
                out.write(struct.pack('<IIII', 4, header_payload + 8, header_payload + 4, new_json_size))
                out.write(new_json_bytes)
                if padding > 0:
                    out.write(b'\x00' * padding)
                for e in entries:
                    if e['unpacked']:
                        continue
                    if 'new_data' in e:
                        out.write(e['new_data'])
                    else:
                        f.seek(data_start + e['offset'])
                        out.write(f.read(e['size']))

        os.replace(tmp_out, asar_path)
        success = True
        break
    except Exception as ex:
        if attempt == max_retries - 1:
            print(f"Auto-heal patch injection failed: {ex}", file=sys.stderr)
            sys.exit(1)
        time.sleep(0.5)

if success:
    print("Auto-heal in-place injection successful.")
EOF

log "Auto-healing routine finished successfully."
