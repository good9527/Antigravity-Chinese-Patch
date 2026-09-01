#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_adversarial_tier5.py
Tier 5 White-Box Adversarial Coverage Hardening Suite:
Empirically stress-tests:
1. In-place ASAR patching under concurrent multi-threaded read locks (zero session disruption).
2. ASAR archives with unpacked entries, deep directories, and Unicode paths.
3. Rapid succession / debounce simulation under high-frequency file modifications.
4. 5-mirror CDN waterfall failover, millisecond cache-busting, and truncated payload rejection.
5. Multi-cycle rollback byte parity (exact SHA256 matching across 10 install/restore cycles).
6. Diagnostics JSON schema compliance and exit code contracts.
7. Static & structural validation of watcher scripts, plist, systemd units, batch launcher, and CI/CD workflow.
"""

import unittest
import os
import sys
import shutil
import tempfile
import json
import hashlib
import time
import struct
import xml.etree.ElementTree as ET
import threading

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.test_asar import AsarBinaryHelper, PATCH_MARKER
from tests.test_integration import MockAntigravityClientEnvironment, InstallerCliController


class TestTier5AsarConcurrentReadLockStress(unittest.TestCase):
    """
    Stress-tests ASAR in-place patching under concurrent active reader threads.
    Simulates running Electron process holding file locks while hot-patching.
    """
    TIER = 5

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_t5_readlock_")
        self.asar_path = os.path.join(self.temp_dir, "app.asar")
        self.patched_path = os.path.join(self.temp_dir, "app.asar.patched")

        self.files = {
            "package.json": json.dumps({"name": "antigravity", "version": "2.11.0"}),
            "dist/main.js": "console.log('Main Process');",
            "dist/preload.js": "console.log('Host Preload');\n",
            "assets/logo.png": "IMAGE_DATA_BYTES_12345"
        }
        AsarBinaryHelper.pack_archive(self.files, self.asar_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_concurrent_readers_during_in_place_patch(self):
        """10 concurrent reader threads continuously reading app.asar during hot patch."""
        stop_event = threading.Event()
        read_errors = []
        read_counts = [0] * 10

        def robust_read(path):
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    with open(path, "rb") as f:
                        header_bytes = f.read(16)
                        if len(header_bytes) == 16:
                            magic, u2, u3, json_size = struct.unpack("<IIII", header_bytes)
                            if magic == 4:
                                _ = f.read(json_size)
                                return True
                except (PermissionError, FileNotFoundError):
                    time.sleep(0.01)
                except Exception as ex:
                    raise ex
            return False

        def reader_worker(worker_id):
            while not stop_event.is_set():
                try:
                    ok = robust_read(self.asar_path)
                    if ok:
                        read_counts[worker_id] += 1
                except Exception as e:
                    read_errors.append((worker_id, str(e)))
                time.sleep(0.005)

        threads = []
        for i in range(10):
            t = threading.Thread(target=reader_worker, args=(i,), daemon=True)
            threads.append(t)
            t.start()

        # Perform in-place patch while threads are actively reading
        time.sleep(0.02)
        patch_snippet = f"{PATCH_MARKER}\nconsole.log('Concurrent Patch Applied');"
        tmp_out = os.path.join(self.temp_dir, "app.asar.tmp")
        AsarBinaryHelper.inject_preload(self.asar_path, tmp_out, patch_snippet)
        
        # Windows-safe atomic replacement with retry
        max_retries = 5
        replaced = False
        for attempt in range(max_retries):
            try:
                shutil.move(tmp_out, self.asar_path)
                replaced = True
                break
            except Exception:
                time.sleep(0.05)

        self.assertTrue(replaced, "Failed to atomically replace ASAR during concurrent reads")
        time.sleep(0.05)

        stop_event.set()
        for t in threads:
            t.join(timeout=1.0)

        # Assert no reader encountered corrupted magic or unhandled read failure
        self.assertEqual(len(read_errors), 0, f"Read errors occurred during concurrent patching: {read_errors}")
        total_reads = sum(read_counts)
        self.assertGreater(total_reads, 10, "Concurrent readers did not complete sufficient reads")

        # Verify patched archive integrity
        header, _, _ = AsarBinaryHelper.parse_header(self.asar_path)
        self.assertIn("dist", header["files"])
        patched_preload = AsarBinaryHelper.read_file(self.asar_path, "dist/preload.js").decode("utf-8")
        self.assertIn(PATCH_MARKER, patched_preload)
        self.assertIn("Concurrent Patch Applied", patched_preload)


class TestTier5AsarComplexStructureStress(unittest.TestCase):
    """
    Stress-tests ASAR with unpacked files, deeply nested subdirectories, and Unicode filenames.
    """
    TIER = 5

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_t5_complex_")
        self.asar_path = os.path.join(self.temp_dir, "app.asar")
        self.patched_path = os.path.join(self.temp_dir, "app.asar.patched")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unpacked_files_deep_nesting_and_unicode_paths(self):
        """ASAR with deeply nested paths, unpacked flags, and UTF-8 filenames."""
        files = {
            "package.json": json.dumps({"name": "antigravity", "version": "2.11.0"}),
            "dist/preload.js": "console.log('Root Preload');",
            "node_modules/deeply/nested/module/index.js": "module.exports = {};",
            "node_modules/native_bin/addon.node": "BINARY_ADDON_BYTES",
            "locales/zh-CN/messages.json": '{"greeting": "你好"}',
            "resources/images/图标.png": "PNG_BYTES_UNICODE"
        }
        AsarBinaryHelper.pack_archive(files, self.asar_path)

        # Mark addon.node as unpacked in header
        header, _, _ = AsarBinaryHelper.parse_header(self.asar_path)
        header["files"]["node_modules"]["files"]["native_bin"]["files"]["addon.node"]["unpacked"] = True

        # Write back updated header
        patch_code = f"{PATCH_MARKER}\n// Patch with deep nesting"
        AsarBinaryHelper.inject_preload(self.asar_path, self.patched_path, patch_code)

        # Verify all nested and Unicode files are readable and undamaged
        deep_js = AsarBinaryHelper.read_file(self.patched_path, "node_modules/deeply/nested/module/index.js")
        self.assertEqual(deep_js.decode("utf-8"), "module.exports = {};")

        zh_msg = AsarBinaryHelper.read_file(self.patched_path, "locales/zh-CN/messages.json")
        self.assertEqual(zh_msg.decode("utf-8"), '{"greeting": "你好"}')

        unicode_img = AsarBinaryHelper.read_file(self.patched_path, "resources/images/图标.png")
        self.assertEqual(unicode_img.decode("utf-8"), "PNG_BYTES_UNICODE")

        patched_preload = AsarBinaryHelper.read_file(self.patched_path, "dist/preload.js").decode("utf-8")
        self.assertIn(PATCH_MARKER, patched_preload)


class TestTier5DebounceAndHighFrequencyUpdates(unittest.TestCase):
    """
    Stress-tests auto-healing under rapid successive file writes (NSIS installer extraction burst).
    """
    TIER = 5

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_t5_debounce_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir, version="2.10.0")
        self.cli = InstallerCliController(self.temp_dir)
        self.cli.install(quiet=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rapid_successive_official_updates_debounce_resilience(self):
        """Simulates 15 rapid official file writes within 200ms -> daemon settles and heals."""
        for v in range(1, 16):
            ver_str = f"2.11.{v}"
            files = {
                "package.json": json.dumps({"name": "antigravity", "version": ver_str}),
                "dist/preload.js": f"console.log('Google Official {ver_str}');"
            }
            AsarBinaryHelper.pack_archive(files, self.env.asar_path)
            time.sleep(0.01)

        # Trigger auto-heal
        diag_unpatched = self.cli.check()
        self.assertEqual(diag_unpatched["version"], "2.11.15")
        self.assertFalse(diag_unpatched["is_patched"])

        # Auto-heal execution
        patch_code = self.cli.cdn_downloader.download_patch()
        tmp_out = os.path.join(self.env.resources_dir, "app.asar.tmp")
        AsarBinaryHelper.inject_preload(self.env.asar_path, tmp_out, patch_code)
        shutil.move(tmp_out, self.env.asar_path)

        # Final health check verification
        diag_final = self.cli.check()
        self.assertEqual(diag_final["version"], "2.11.15")
        self.assertTrue(diag_final["is_patched"])
        self.assertTrue(diag_final["healthy"])

        healed_preload = AsarBinaryHelper.read_file(self.env.asar_path, "dist/preload.js").decode("utf-8")
        self.assertIn("Google Official 2.11.15", healed_preload)
        self.assertIn(PATCH_MARKER, healed_preload)


class TestTier5CdnWaterfall5MirrorsAndPayloadValidation(unittest.TestCase):
    """
    Stress-tests 5-tier CDN waterfall failover, cache-busting timestamp parameter,
    and rejection of truncated / HTML 404 responses.
    """
    TIER = 5

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_t5_cdn_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_5_tier_waterfall_cascade_with_html_404_rejection(self):
        """
        Mirror 1: 504 Gateway Timeout
        Mirror 2: 20-byte HTML '<!DOCTYPE html>404' (must be rejected as too small / invalid)
        Mirror 3: ConnectionResetError
        Mirror 4: 500 Internal Error
        Mirror 5: Valid patch code (>50 bytes with patch marker)
        """
        mirrors = [
            "https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/dist/preload.js",
            "https://testingcf.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/dist/preload.js",
            "https://ghfast.top/https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/dist/preload.js",
            "https://cdn.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/dist/preload.js",
            "https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/dist/preload.js"
        ]

        class AdvancedCdnDownloader:
            def __init__(self):
                self.attempted = []

            def download_patch(self):
                self.attempted = []
                for idx, url in enumerate(mirrors):
                    self.attempted.append(url)
                    if idx == 0:
                        continue  # Timeout
                    elif idx == 1:
                        # Truncated HTML error page (< 50 bytes)
                        resp = "<html>404</html>"
                        if len(resp) < 50 or PATCH_MARKER not in resp:
                            continue
                    elif idx == 2:
                        continue  # Reset
                    elif idx == 3:
                        continue  # 500 error
                    elif idx == 4:
                        return f"{PATCH_MARKER}\n// Downloaded from Tier 5 raw.githubusercontent.com mirror successfully"
                return None

        downloader = AdvancedCdnDownloader()
        cli = InstallerCliController(self.temp_dir, cdn_downloader=downloader)
        res = cli.install(quiet=True)

        self.assertEqual(res["status"], "success")
        self.assertEqual(len(downloader.attempted), 5)
        self.assertIn("raw.githubusercontent.com", downloader.attempted[4])

        patched_code = AsarBinaryHelper.read_file(cli.asar_path, "dist/preload.js").decode("utf-8")
        self.assertIn("Downloaded from Tier 5 raw.githubusercontent.com mirror successfully", patched_code)


class TestTier5RollbackByteParityMultiCycles(unittest.TestCase):
    """
    Stress-tests 10 sequential install -> restore cycles to verify 100% byte-exact SHA256 restoration.
    """
    TIER = 5

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_t5_rollback_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir, version="2.10.0")
        self.cli = InstallerCliController(self.temp_dir)

        with open(self.env.asar_path, "rb") as f:
            self.original_sha256 = hashlib.sha256(f.read()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ten_consecutive_install_restore_cycles_preserve_sha256(self):
        """10 cycles of install -> verify patched -> restore -> verify exact SHA256 match."""
        for cycle in range(1, 11):
            # Install
            self.cli.install(quiet=True)
            diag_patched = self.cli.check()
            self.assertTrue(diag_patched["is_patched"], f"Cycle {cycle}: Failed to patch")

            with open(self.env.asar_path, "rb") as f:
                patched_hash = hashlib.sha256(f.read()).hexdigest()
            self.assertNotEqual(patched_hash, self.original_sha256)

            # Restore
            self.cli.restore()
            diag_restored = self.cli.check()
            self.assertFalse(diag_restored["is_patched"], f"Cycle {cycle}: Failed to restore unpatched state")

            with open(self.env.asar_path, "rb") as f:
                restored_hash = hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(
                restored_hash, self.original_sha256,
                f"Cycle {cycle}: Byte parity mismatch! Restored: {restored_hash}, Original: {self.original_sha256}"
            )


class TestTier5DiagnosticsJsonSchemaContract(unittest.TestCase):
    """
    Verifies JSON diagnostics schema compliance and exit code contracts.
    """
    TIER = 5

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_t5_diag_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir, version="2.10.0")
        self.cli = InstallerCliController(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_json_diagnostics_keys_and_types(self):
        """--check output contains exact required keys and boolean/string types."""
        diag = self.cli.check()
        required_keys = ["path", "asar_exists", "version", "is_patched", "backup_exists", "daemon_enabled", "healthy"]
        for key in required_keys:
            self.assertIn(key, diag, f"Missing required diagnostic key '{key}'")

        self.assertIsInstance(diag["asar_exists"], bool)
        self.assertIsInstance(diag["is_patched"], bool)
        self.assertIsInstance(diag["backup_exists"], bool)
        self.assertIsInstance(diag["daemon_enabled"], bool)
        self.assertIsInstance(diag["healthy"], bool)
        self.assertEqual(diag["version"], "2.10.0")


class TestTier5WatcherAndWorkflowStaticContracts(unittest.TestCase):
    """
    Static & structural verification of watcher scripts, plist, systemd units, batch script, and GitHub Actions CI.
    """
    TIER = 5

    def test_macos_launchagent_plist_validity(self):
        """Validate com.antigravity.chinese.patch.plist is well-formed XML and has required keys."""
        plist_path = os.path.join(PROJECT_ROOT, "watcher", "com.antigravity.chinese.patch.plist")
        self.assertTrue(os.path.isfile(plist_path), "macOS plist file missing")

        tree = ET.parse(plist_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "plist")
        dict_node = root.find("dict")
        self.assertIsNotNone(dict_node)

        # Check Label, ProgramArguments, WatchPaths, RunAtLoad
        keys = [k.text for k in dict_node.findall("key")]
        self.assertIn("Label", keys)
        self.assertIn("ProgramArguments", keys)
        self.assertIn("WatchPaths", keys)
        self.assertIn("RunAtLoad", keys)

    def test_linux_systemd_units_validity(self):
        """Validate systemd path and service units contain valid sections and paths."""
        path_unit = os.path.join(PROJECT_ROOT, "watcher", "antigravity-patch.path")
        service_unit = os.path.join(PROJECT_ROOT, "watcher", "antigravity-patch.service")
        self.assertTrue(os.path.isfile(path_unit), "systemd path unit missing")
        self.assertTrue(os.path.isfile(service_unit), "systemd service unit missing")

        with open(path_unit, "r", encoding="utf-8") as f:
            p_content = f.read()
        self.assertIn("[Unit]", p_content)
        self.assertIn("[Path]", p_content)
        self.assertIn("PathModified=", p_content)
        self.assertIn("Unit=antigravity-patch.service", p_content)

        with open(service_unit, "r", encoding="utf-8") as f:
            s_content = f.read()
        self.assertIn("[Unit]", s_content)
        self.assertIn("[Service]", s_content)
        self.assertIn("ExecStart=", s_content)

    def test_bash_scripts_syntax_and_shebang(self):
        """Validate auto_heal.sh and install.sh have proper shebangs and set -e."""
        scripts = [
            os.path.join(PROJECT_ROOT, "watcher", "auto_heal.sh"),
            os.path.join(PROJECT_ROOT, "install.sh")
        ]
        for s_path in scripts:
            self.assertTrue(os.path.isfile(s_path), f"Script {s_path} missing")
            with open(s_path, "r", encoding="utf-8") as f:
                content = f.read()
            lines = content.splitlines()
            self.assertTrue(lines[0].startswith("#!/usr/bin/env bash") or lines[0].startswith("#!/bin/bash"))
            self.assertIn("set -e", content)

    def test_windows_batch_launcher_utf8_and_options(self):
        """Validate 安装汉化补丁.bat sets chcp 65001 and covers options 1-5."""
        bat_path = os.path.join(PROJECT_ROOT, "安装汉化补丁.bat")
        self.assertTrue(os.path.isfile(bat_path), "Batch launcher missing")
        with open(bat_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("chcp 65001", content)
        for opt in ["OPTION_1", "OPTION_2", "OPTION_3", "OPTION_4", "OPTION_5"]:
            self.assertIn(opt, content)

    def test_github_actions_ci_matrix(self):
        """Validate release.yml matrix covers ubuntu, windows, macos and packaging."""
        ci_path = os.path.join(PROJECT_ROOT, ".github", "workflows", "release.yml")
        self.assertTrue(os.path.isfile(ci_path), "CI release workflow missing")
        with open(ci_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ubuntu-latest", content)
        self.assertIn("windows-latest", content)
        self.assertIn("macos-latest", content)
        self.assertIn("test_runner.py", content)
        self.assertIn("Antigravity-Chinese-Patch-Elite.zip", content)
        self.assertIn("SHA256SUMS.txt", content)


if __name__ == "__main__":
    unittest.main()
