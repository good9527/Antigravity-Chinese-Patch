#!/usr/bin/env bash
# install.sh
# macOS / Linux Universal Installer & Daemon Manager for Antigravity-Chinese-Patch
# Features: Zero Process Disruption + In-Place ASAR Hot Patch + Offline Cache + launchd / systemd Auto-Heal Daemon

set -e

# 1. Parse Command Line Arguments
ACTION="install"
QUIET=false
JSON_OUT=false
CUSTOM_PATH=""
DAEMON_ACTION=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --install|-i)
            ACTION="install"
            shift
            ;;
        --uninstall|-u)
            ACTION="uninstall"
            shift
            ;;
        --check|-c)
            ACTION="check"
            shift
            ;;
        --restore|-r)
            ACTION="restore"
            shift
            ;;
        --daemon)
            ACTION="daemon"
            DAEMON_ACTION="$2"
            shift 2
            ;;
        --daemon-on)
            ACTION="daemon"
            DAEMON_ACTION="enable"
            shift
            ;;
        --daemon-off)
            ACTION="daemon"
            DAEMON_ACTION="disable"
            shift
            ;;
        --daemon-status)
            ACTION="daemon"
            DAEMON_ACTION="status"
            shift
            ;;
        --quiet|-q|--silent)
            QUIET=true
            shift
            ;;
        --json)
            JSON_OUT=true
            shift
            ;;
        --path|-p)
            CUSTOM_PATH="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE_DIR="$HOME/.antigravity-chinese-patch"
CACHED_PRELOAD="$CACHE_DIR/preload.js"
CACHED_AUTOHEAL="$CACHE_DIR/auto_heal.sh"
PATCH_MARKER="// Antigravity Chinese Localization Patch"
REPO_OWNER="good9527"
REPO_NAME="Antigravity-Chinese-Patch"

log() {
    if [ "$QUIET" = false ] && [ "$JSON_OUT" = false ]; then
        echo "$@"
    fi
}

# 2. Smart Path Resolver
find_asar_path() {
    if [ -n "$CUSTOM_PATH" ]; then
        if [ -f "$CUSTOM_PATH/resources/app.asar" ]; then
            echo "$CUSTOM_PATH/resources/app.asar"
            return
        elif [ -f "$CUSTOM_PATH/Contents/Resources/app.asar" ]; then
            echo "$CUSTOM_PATH/Contents/Resources/app.asar"
            return
        elif [ -f "$CUSTOM_PATH" ]; then
            echo "$CUSTOM_PATH"
            return
        fi
    fi

    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -f "/Applications/Antigravity.app/Contents/Resources/app.asar" ]; then
            echo "/Applications/Antigravity.app/Contents/Resources/app.asar"
            return
        elif [ -f "$HOME/Applications/Antigravity.app/Contents/Resources/app.asar" ]; then
            echo "$HOME/Applications/Antigravity.app/Contents/Resources/app.asar"
            return
        fi
    else
        # Linux standard paths
        if [ -f "/opt/Antigravity/resources/app.asar" ]; then
            echo "/opt/Antigravity/resources/app.asar"
            return
        elif [ -f "/usr/lib/antigravity/resources/app.asar" ]; then
            echo "/usr/lib/antigravity/resources/app.asar"
            return
        elif [ -f "$HOME/.local/share/antigravity/resources/app.asar" ]; then
            echo "$HOME/.local/share/antigravity/resources/app.asar"
            return
        fi
    fi
    echo ""
}

ASAR_PATH="$(find_asar_path)"
RESOURCES_DIR=""
BACKUP_ASAR=""

if [ -n "$ASAR_PATH" ]; then
    RESOURCES_DIR="$(dirname "$ASAR_PATH")"
    BACKUP_ASAR="$RESOURCES_DIR/app.asar.bak"
fi

# 3. Offline Cache Synchronizer
sync_offline_cache() {
    mkdir -p "$CACHE_DIR"
    local source_preload="$1"
    if [ -f "$source_preload" ]; then
        cp "$source_preload" "$CACHED_PRELOAD"
    fi

    # Sync watcher scripts
    if [ -f "$SCRIPT_DIR/watcher/auto_heal.sh" ]; then
        cp "$SCRIPT_DIR/watcher/auto_heal.sh" "$CACHED_AUTOHEAL"
        chmod +x "$CACHED_AUTOHEAL"
    elif [ -f "$SCRIPT_DIR/auto_heal.sh" ]; then
        cp "$SCRIPT_DIR/auto_heal.sh" "$CACHED_AUTOHEAL"
        chmod +x "$CACHED_AUTOHEAL"
    fi
}

# 4. Multi-Mirror CDN Waterfall Downloader
download_patch_cdn() {
    local dest="$1"
    local timestamp=$(date +%s%N 2>/dev/null || date +%s)
    local mirrors=(
        "https://fastly.jsdelivr.net/gh/$REPO_OWNER/$REPO_NAME@main/dist/preload.js?t=$timestamp"
        "https://testingcf.jsdelivr.net/gh/$REPO_OWNER/$REPO_NAME@main/dist/preload.js?t=$timestamp"
        "https://ghfast.top/https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/main/dist/preload.js?t=$timestamp"
        "https://cdn.jsdelivr.net/gh/$REPO_OWNER/$REPO_NAME@main/dist/preload.js?t=$timestamp"
        "https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/main/dist/preload.js?t=$timestamp"
    )

    for url in "${mirrors[@]}"; do
        log "Connecting to mirror: $url ..."
        if curl -fsSL "$url" -o "$dest" --connect-timeout 5 2>/dev/null; then
            if [ -s "$dest" ] && [ $(wc -c < "$dest") -gt 50 ]; then
                log "Successfully downloaded from mirror!"
                return 0
            fi
        fi
    done
    return 1
}

# 5. Daemon Controller (launchd on macOS, systemd on Linux)
manage_daemon() {
    local cmd="$1"
    mkdir -p "$CACHE_DIR"
    sync_offline_cache "$CACHED_PRELOAD"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        local plist_dir="$HOME/Library/LaunchAgents"
        local plist_file="$plist_dir/com.antigravity.chinese.patch.plist"

        if [ "$cmd" = "enable" ]; then
            mkdir -p "$plist_dir"
            cat > "$plist_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.antigravity.chinese.patch</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>[ -f "$HOME/.antigravity-chinese-patch/auto_heal.sh" ] &amp;&amp; /bin/bash "$HOME/.antigravity-chinese-patch/auto_heal.sh"</string>
    </array>
    <key>WatchPaths</key>
    <array>
        <string>/Applications/Antigravity.app/Contents/Resources/app.asar</string>
        <string>/Applications/Antigravity.app/Contents/Resources</string>
        <string>$HOME/Applications/Antigravity.app/Contents/Resources/app.asar</string>
        <string>$HOME/Applications/Antigravity.app/Contents/Resources</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/antigravity_patch_autoheal.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/antigravity_patch_autoheal.err</string>
</dict>
</plist>
EOF
            launchctl unload "$plist_file" 2>/dev/null || true
            launchctl load -w "$plist_file" 2>/dev/null || true
            log "Auto-healing LaunchAgent enabled on macOS (WatchPaths active)."
            return 0
        elif [ "$cmd" = "disable" ]; then
            if [ -f "$plist_file" ]; then
                launchctl unload "$plist_file" 2>/dev/null || true
                rm -f "$plist_file"
            fi
            log "Auto-healing LaunchAgent disabled."
            return 0
        elif [ "$cmd" = "status" ]; then
            local is_loaded=false
            if launchctl list | grep -q "com.antigravity.chinese.patch" 2>/dev/null; then
                is_loaded=true
            elif [ -f "$plist_file" ]; then
                is_loaded=true
            fi
            log "Daemon Status: $(if [ "$is_loaded" = true ]; then echo "ENABLED"; else echo "DISABLED"; fi)"
            [ "$is_loaded" = true ] && return 0 || return 1
        fi
    else
        # Linux systemd user units
        local systemd_dir="$HOME/.config/systemd/user"
        local path_file="$systemd_dir/antigravity-patch.path"
        local service_file="$systemd_dir/antigravity-patch.service"

        if [ "$cmd" = "enable" ]; then
            mkdir -p "$systemd_dir"
            cat > "$path_file" << EOF
[Unit]
Description=Watch Antigravity app.asar for updates

[Path]
PathModified=$HOME/.local/share/antigravity/resources/app.asar
PathModified=/opt/Antigravity/resources/app.asar
PathModified=/usr/lib/antigravity/resources/app.asar
Unit=antigravity-patch.service

[Install]
WantedBy=paths.target
EOF
            cat > "$service_file" << EOF
[Unit]
Description=Antigravity Chinese Patch Auto-Healing Service
After=antigravity-patch.path

[Service]
Type=oneshot
ExecStart=/bin/bash %h/.antigravity-chinese-patch/auto_heal.sh
EOF
            systemctl --user daemon-reload 2>/dev/null || true
            systemctl --user enable --now antigravity-patch.path 2>/dev/null || true
            log "Auto-healing systemd unit enabled on Linux."
            return 0
        elif [ "$cmd" = "disable" ]; then
            systemctl --user disable --now antigravity-patch.path 2>/dev/null || true
            rm -f "$path_file" "$service_file"
            systemctl --user daemon-reload 2>/dev/null || true
            log "Auto-healing systemd unit disabled."
            return 0
        elif [ "$cmd" = "status" ]; then
            local is_active=false
            if systemctl --user is-active --quiet antigravity-patch.path 2>/dev/null; then
                is_active=true
            elif [ -f "$path_file" ]; then
                is_active=true
            fi
            log "Daemon Status: $(if [ "$is_active" = true ]; then echo "ENABLED"; else echo "DISABLED"; fi)"
            [ "$is_active" = true ] && return 0 || return 1
        fi
    fi
}

# 6. Action: Check Diagnostics
invoke_check() {
    local asar_exists=false
    local is_patched=false
    local bak_exists=false
    local daemon_enabled=false
    local version="Unknown"

    if [ -n "$ASAR_PATH" ] && [ -f "$ASAR_PATH" ]; then
        asar_exists=true
        if grep -q "$PATCH_MARKER" "$ASAR_PATH" 2>/dev/null; then
            is_patched=true
        fi
        version=$(python3 -c "
import json, struct, sys
try:
    with open('$ASAR_PATH', 'rb') as f:
        magic, u2, u3, json_size = struct.unpack('<IIII', f.read(16))
        header = json.loads(f.read(json_size).decode('utf-8'))
        pkg_node = header['files']['package.json']
        f.seek(8 + u2 + int(pkg_node['offset']))
        pkg = json.loads(f.read(int(pkg_node['size'])).decode('utf-8'))
        print(pkg.get('version', 'Unknown'))
except:
    print('Unknown')
" 2>/dev/null || echo "Unknown")
    fi

    if [ -n "$BACKUP_ASAR" ] && [ -f "$BACKUP_ASAR" ]; then
        bak_exists=true
    fi

    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [ -f "$HOME/Library/LaunchAgents/com.antigravity.chinese.patch.plist" ]; then
            daemon_enabled=true
        fi
    else
        if [ -f "$HOME/.config/systemd/user/antigravity-patch.path" ]; then
            daemon_enabled=true
        fi
    fi

    local healthy=false
    if [ "$asar_exists" = true ] && [ "$is_patched" = true ] && [ "$bak_exists" = true ]; then
        healthy=true
    fi

    if [ "$JSON_OUT" = true ]; then
        python3 -c "
import json
out = {
    'path': '$ASAR_PATH',
    'asar_exists': $asar_exists,
    'version': '$version',
    'is_patched': $is_patched,
    'backup_exists': $bak_exists,
    'daemon_enabled': $daemon_enabled,
    'healthy': $healthy
}
print(json.dumps(out))
"
        [ "$healthy" = true ] && exit 0 || exit 1
    fi

    echo "=========================================================="
    echo "     Antigravity Chinese Patch Health Diagnostics         "
    echo "=========================================================="
    echo "  Installation Directory : $(if [ -n "$ASAR_PATH" ]; then echo "$(dirname "$RESOURCES_DIR")"; else echo "NOT FOUND"; fi)"
    echo "  Client Version         : $version"
    echo "  Active ASAR Status     : $(if [ "$is_patched" = true ]; then echo "PATCHED [OK]"; else echo "UNPATCHED / MISSING"; fi)"
    echo "  Original Clean Backup  : $(if [ "$bak_exists" = true ]; then echo "PRESENT [OK]"; else echo "NOT FOUND"; fi)"
    echo "  Auto-Healing Daemon    : $(if [ "$daemon_enabled" = true ]; then echo "ENABLED [OK]"; else echo "DISABLED"; fi)"
    echo "=========================================================="
    echo "  Verdict: $(if [ "$healthy" = true ]; then echo "HEALTHY (100% Operational)"; else echo "ATTENTION REQUIRED"; fi)"
    echo "=========================================================="

    [ "$healthy" = true ] && exit 0 || exit 1
}

# 7. Action: Restore Backup
invoke_restore() {
    if [ -z "$ASAR_PATH" ] || [ -z "$BACKUP_ASAR" ] || [ ! -f "$BACKUP_ASAR" ]; then
        echo "Error: Backup app.asar.bak not found. Cannot restore."
        exit 1
    fi
    log "Restoring original pristine client binary from backup..."
    cp "$BACKUP_ASAR" "$ASAR_PATH"
    log "Successfully restored original client!"
}

# 8. Action: Uninstall
invoke_uninstall() {
    invoke_restore
    manage_daemon "disable"
    rm -rf "$CACHE_DIR"
    log "Antigravity Chinese Patch completely uninstalled."
}

# 9. Action: Install (In-Place ASAR Hot Patch, Zero Disruption)
invoke_install() {
    log "=========================================================="
    log "   Antigravity Chinese Patch macOS/Linux Universal Tool   "
    log "   (Zero Disruption Hot Patch + Auto-Healing Daemon)      "
    log "=========================================================="
    log ""

    if [ -z "$ASAR_PATH" ]; then
        if [ "$QUIET" = false ]; then
            echo "Antigravity installation not found automatically."
            read -p "Please enter the full path to app.asar: " ASAR_PATH
            RESOURCES_DIR="$(dirname "$ASAR_PATH")"
            BACKUP_ASAR="$RESOURCES_DIR/app.asar.bak"
        fi
    fi

    if [ -z "$ASAR_PATH" ] || [ ! -f "$ASAR_PATH" ]; then
        echo "Error: app.asar not found at '$ASAR_PATH'."
        exit 1
    fi

    log "Target Antigravity ASAR: $ASAR_PATH"

    # Step 1: Backup
    local is_patched=false
    if grep -q "$PATCH_MARKER" "$ASAR_PATH" 2>/dev/null; then
        is_patched=true
    fi

    if [ "$is_patched" = false ]; then
        log "Creating pristine backup to app.asar.bak..."
        cp "$ASAR_PATH" "$BACKUP_ASAR"
    else
        if [ ! -f "$BACKUP_ASAR" ]; then
            log "Creating backup of current client..."
            cp "$ASAR_PATH" "$BACKUP_ASAR"
        else
            log "Backup app.asar.bak verified."
        fi
    fi

    # Step 2: Obtain patch code (Local -> Cache -> CDN Waterfall)
    local patch_file=""
    if [ -f "$SCRIPT_DIR/dist/preload.js" ]; then
        patch_file="$SCRIPT_DIR/dist/preload.js"
        sync_offline_cache "$patch_file"
    elif [ -f "$CACHED_PRELOAD" ]; then
        patch_file="$CACHED_PRELOAD"
    else
        local temp_dir=$(mktemp -d 2>/dev/null || mktemp -d -t 'antigravity_patch')
        local dl_preload="$temp_dir/preload.js"
        log "Downloading patch from CDN mirrors..."
        if download_patch_cdn "$dl_preload"; then
            patch_file="$dl_preload"
            sync_offline_cache "$dl_preload"
        fi
        rm -rf "$temp_dir"
    fi

    if [ -z "$patch_file" ] || [ ! -f "$patch_file" ]; then
        echo "Error: Failed to obtain localization patch file."
        exit 1
    fi

    # Step 3: Native In-Place Python ASAR Injection (Zero Process Killing)
    log "Applying zero-disruption in-place ASAR injection..."
    python3 - "$ASAR_PATH" "$BACKUP_ASAR" "$patch_file" << 'EOF'
import sys, os, json, struct, time

asar_path = sys.argv[1]
backup_path = sys.argv[2]
patch_path = sys.argv[3]
marker = "// Antigravity Chinese Localization Patch"

with open(patch_path, 'r', encoding='utf-8') as pf:
    patch_full = pf.read()

if marker in patch_full:
    patch_code = patch_full[patch_full.index(marker):]
else:
    patch_code = patch_full

source_asar = backup_path if os.path.exists(backup_path) else asar_path

max_retries = 5
patched = False

for attempt in range(max_retries):
    try:
        with open(source_asar, 'rb') as f:
            magic, u2, u3, json_size = struct.unpack('<IIII', f.read(16))
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
                    entries.append({'path': path, 'node': node, 'offset': offset, 'size': size, 'unpacked': is_unpacked})

            collect(header)
            preload_entry = next((e for e in entries if e['path'].endswith('dist/preload.js') or e['path'].endswith('dist\\preload.js')), None)
            if not preload_entry:
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
                if e['unpacked']: continue
                e['node']['offset'] = str(cur_offset)
                cur_offset += len(e.get('new_data', b'')) if 'new_data' in e else e['size']

            new_json_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
            new_json_size = len(new_json_bytes)
            padding = (4 - (new_json_size % 4)) % 4
            header_payload = new_json_size + padding

            tmp_asar = asar_path + '.patched.tmp'
            with open(tmp_asar, 'wb') as out:
                out.write(struct.pack('<IIII', 4, header_payload + 8, header_payload + 4, new_json_size))
                out.write(new_json_bytes)
                if padding > 0:
                    out.write(b'\x00' * padding)
                for e in entries:
                    if e['unpacked']: continue
                    if 'new_data' in e:
                        out.write(e['new_data'])
                    else:
                        f.seek(data_start + e['offset'])
                        out.write(f.read(e['size']))

        os.replace(tmp_asar, asar_path)
        patched = True
        break
    except Exception as ex:
        if attempt == max_retries - 1:
            print(f"Error during patching: {ex}", file=sys.stderr)
            sys.exit(1)
        time.sleep(0.5)

if not patched:
    sys.exit(1)
EOF

    log "In-place ASAR hot patch applied successfully!"

    # Step 4: Enable auto-healing daemon
    manage_daemon "enable"

    log ""
    log "=========================================================="
    log "   [+] Patch successfully applied! Enjoy Antigravity!     "
    log "   [*] Auto-healing daemon enabled for background updates."
    log "=========================================================="
}

# 10. Main Router
case "$ACTION" in
    check)
        invoke_check
        ;;
    restore)
        invoke_restore
        ;;
    uninstall)
        invoke_uninstall
        ;;
    daemon)
        manage_daemon "$DAEMON_ACTION"
        ;;
    install|*)
        invoke_install
        ;;
esac
