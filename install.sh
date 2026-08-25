#!/usr/bin/env bash
# macOS / Linux Universal One-Click Installer for Antigravity-Chinese-Patch
# Usage: curl -fsSL https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/install.sh | bash

set -e

echo "=========================================================="
echo "   Antigravity Chinese Patch macOS/Linux Installer        "
echo "=========================================================="
echo ""

# 1. Locate app.asar
ASAR_PATH=""
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -f "/Applications/Antigravity.app/Contents/Resources/app.asar" ]; then
        ASAR_PATH="/Applications/Antigravity.app/Contents/Resources/app.asar"
    elif [ -f "$HOME/Applications/Antigravity.app/Contents/Resources/app.asar" ]; then
        ASAR_PATH="$HOME/Applications/Antigravity.app/Contents/Resources/app.asar"
    fi
else
    # Linux
    if [ -f "/opt/Antigravity/resources/app.asar" ]; then
        ASAR_PATH="/opt/Antigravity/resources/app.asar"
    elif [ -f "/usr/lib/antigravity/resources/app.asar" ]; then
        ASAR_PATH="/usr/lib/antigravity/resources/app.asar"
    elif [ -f "$HOME/.local/share/antigravity/resources/app.asar" ]; then
        ASAR_PATH="$HOME/.local/share/antigravity/resources/app.asar"
    fi
fi

if [ -z "$ASAR_PATH" ]; then
    echo "Antigravity installation not found automatically."
    read -p "Please enter the full path to app.asar: " ASAR_PATH
fi

if [ ! -f "$ASAR_PATH" ]; then
    echo "Error: app.asar not found at '$ASAR_PATH'."
    exit 1
fi

RESOURCES_DIR=$(dirname "$ASAR_PATH")
BACKUP_ASAR="$RESOURCES_DIR/app.asar.bak"

echo "Found Antigravity ASAR at: $ASAR_PATH"

# 2. Terminate running process
echo "Closing running Antigravity instances..."
killall -9 Antigravity 2>/dev/null || true
pkill -f "Antigravity" 2>/dev/null || true

# 3. Create Backup
if [ ! -f "$BACKUP_ASAR" ]; then
    echo "Creating original backup to app.asar.bak..."
    cp "$ASAR_PATH" "$BACKUP_ASAR"
else
    echo "Existing backup found at app.asar.bak."
fi

# 4. Download latest preload.js via CDN mirrors
TEMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'antigravity_patch')
DOWNLOADED_PRELOAD="$TEMP_DIR/preload.js"

MIRRORS=(
    "https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/dist/preload.js"
    "https://testingcf.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/dist/preload.js"
    "https://ghfast.top/https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/dist/preload.js"
    "https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/dist/preload.js"
)

DOWNLOAD_OK=false
for url in "${MIRRORS[@]}"; do
    echo "Downloading patch from: $url ..."
    if curl -fsSL "$url" -o "$DOWNLOADED_PRELOAD" --connect-timeout 5; then
        if [ -s "$DOWNLOADED_PRELOAD" ]; then
            DOWNLOAD_OK=true
            echo "Download successful!"
            break
        fi
    fi
done

if [ "$DOWNLOAD_OK" = false ]; then
    echo "Error: Failed to download localization patch from CDN mirrors."
    rm -rf "$TEMP_DIR"
    exit 1
fi

# 5. In-place Native Python ASAR Injection
python3 -c "
import json, struct, os, sys

def patch_asar(input_path, output_path, preload_patch_file):
    with open(preload_patch_file, 'r', encoding='utf-8') as pf:
        patch_full = pf.read()
    marker = '// Antigravity Chinese Localization Patch'
    if marker in patch_full:
        patch_code = patch_full[patch_full.index(marker):]
    else:
        patch_code = patch_full

    with open(input_path, 'rb') as f:
        magic, payload_size, json_payload_size, json_size = struct.unpack('<IIII', f.read(16))
        header_json = f.read(json_size).decode('utf-8')
        header = json.loads(header_json)
        data_start = 16 + json_size

        entries = []
        def collect(node, path=''):
            if 'files' in node:
                for k, v in node['files'].items():
                    collect(v, f'{path}/{k}' if path else k)
            else:
                is_unpacked = node.get('unpacked', False)
                offset = int(node.get('offset', 0))
                size = int(node.get('size', 0))
                entries.append({'path': path, 'node': node, 'offset': offset, 'size': size, 'unpacked': is_unpacked})

        collect(header)
        preload_entry = next((e for e in entries if e['path'].endswith('dist/preload.js')), None)
        if not preload_entry:
            raise RuntimeError('dist/preload.js not found in app.asar')

        f.seek(data_start + preload_entry['offset'])
        old_preload = f.read(preload_entry['size']).decode('utf-8', errors='ignore')
        if marker in old_preload:
            old_preload = old_preload.split(marker)[0].rstrip()

        new_preload = (old_preload + '\n\n' + patch_code).encode('utf-8')
        preload_entry['new_data'] = new_preload
        preload_entry['node']['size'] = len(new_preload)

        entries.sort(key=lambda e: e['offset'])
        cur_offset = 0
        for e in entries:
            if e['unpacked']: continue
            e['node']['offset'] = str(cur_offset)
            cur_offset += len(e.get('new_data', b'')) if 'new_data' in e else e['size']

        new_json_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
        new_json_size = len(new_json_bytes)

        with open(output_path, 'wb') as out:
            out.write(struct.pack('<IIII', 4, new_json_size + 8, new_json_size + 4, new_json_size))
            out.write(new_json_bytes)
            for e in entries:
                if e['unpacked']: continue
                if 'new_data' in e:
                    out.write(e['new_data'])
                else:
                    f.seek(data_start + e['offset'])
                    out.write(f.read(e['size']))

source_asar = '$BACKUP_ASAR' if os.path.exists('$BACKUP_ASAR') else '$ASAR_PATH'
patched_temp = '$TEMP_DIR/app.asar.patched'
patch_asar(source_asar, patched_temp, '$DOWNLOADED_PRELOAD')
os.replace(patched_temp, '$ASAR_PATH')
print('Native Python ASAR in-place injection successful!')
"

rm -rf "$TEMP_DIR"

echo ""
echo "=========================================================="
echo "   Patch successfully applied! Enjoy Antigravity!         "
echo "=========================================================="
