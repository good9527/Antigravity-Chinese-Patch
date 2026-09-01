#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_integration.py
Tier 3: Cross-Feature Combinations, Pairwise Testing & CDN Waterfall Simulation:
- CLI Flags (--install, --check, --restore, --uninstall, --daemon, --quiet)
- Multi-mirror CDN waterfall failover and timeout resilience
- Cross-platform installer simulation
"""

import unittest
import os
import sys
import shutil
import tempfile
import json
import hashlib
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from test_asar import AsarBinaryHelper, PATCH_MARKER


# ==============================================================================
# Cross-Platform CLI Simulation Controller
# ==============================================================================

class MockAntigravityClientEnvironment:
    """Simulated Antigravity target directory environment."""

    def __init__(self, base_dir, version="2.10.0", is_initially_patched=False):
        self.base_dir = base_dir
        self.resources_dir = os.path.join(base_dir, "resources")
        self.patcher_dir = os.path.join(base_dir, "patcher")
        self.asar_path = os.path.join(self.resources_dir, "app.asar")
        self.backup_path = os.path.join(self.resources_dir, "app.asar.bak")
        self.daemon_config_path = os.path.join(self.patcher_dir, "daemon.json")
        self.version = version

        os.makedirs(self.resources_dir, exist_ok=True)
        os.makedirs(self.patcher_dir, exist_ok=True)

        preload_content = "console.log('Original Host Preload');"
        if is_initially_patched:
            preload_content += f"\n\n{PATCH_MARKER}\n// Patch code"

        files = {
            "package.json": json.dumps({"name": "antigravity", "version": version}),
            "dist/preload.js": preload_content
        }
        AsarBinaryHelper.pack_archive(files, self.asar_path)

        if is_initially_patched:
            # Create backup with unpatched preload
            unpatched_files = {
                "package.json": json.dumps({"name": "antigravity", "version": version}),
                "dist/preload.js": "console.log('Original Host Preload');"
            }
            AsarBinaryHelper.pack_archive(unpatched_files, self.backup_path)


class InstallerCliController:
    """
    Reference CLI controller implementing interface contracts from PROJECT.md:
    --install, --uninstall, --check, --restore, --daemon, --quiet
    """

    def __init__(self, target_dir, cdn_downloader=None):
        self.target_dir = target_dir
        self.resources_dir = os.path.join(target_dir, "resources")
        self.patcher_dir = os.path.join(target_dir, "patcher")
        self.asar_path = os.path.join(self.resources_dir, "app.asar")
        self.backup_path = os.path.join(self.resources_dir, "app.asar.bak")
        self.daemon_conf = os.path.join(self.patcher_dir, "daemon.json")
        self.cdn_downloader = cdn_downloader or MockCdnWaterfallDownloader()

    def install(self, quiet=False):
        """--install / -i: Installs patch in-place, configures backup, enables auto-heal daemon."""
        if not os.path.isfile(self.asar_path):
            raise FileNotFoundError(f"app.asar not found at {self.asar_path}")

        # Check if already patched
        is_patched = False
        try:
            content = AsarBinaryHelper.read_file(self.asar_path, "dist/preload.js").decode("utf-8")
            if PATCH_MARKER in content:
                is_patched = True
        except Exception:
            pass

        # Create backup if not present and currently unpatched
        if not is_patched:
            shutil.copy2(self.asar_path, self.backup_path)
        elif not os.path.isfile(self.backup_path):
            shutil.copy2(self.asar_path, self.backup_path)

        # Download patch from CDN waterfall
        patch_code = self.cdn_downloader.download_patch()
        if not patch_code:
            raise RuntimeError("Failed to download localization patch from CDN mirrors")

        # In-place patch
        tmp_asar = os.path.join(self.resources_dir, "app.asar.tmp")
        source = self.backup_path if os.path.isfile(self.backup_path) else self.asar_path
        AsarBinaryHelper.inject_preload(source, tmp_asar, patch_code)
        shutil.move(tmp_asar, self.asar_path)

        # Enable auto-heal daemon
        self.daemon(action="enable")
        return {"status": "success", "message": "Patch successfully installed"}

    def check(self):
        """
        --check / -c: Diagnoses installation path, client version, ASAR patch status,
        backup presence, daemon health. Returns dict. Exit code 0 if healthy/patched, 1 if not.
        """
        result = {
            "path": self.target_dir,
            "asar_exists": os.path.isfile(self.asar_path),
            "version": None,
            "is_patched": False,
            "backup_exists": os.path.isfile(self.backup_path),
            "daemon_enabled": False,
            "healthy": False
        }

        if result["asar_exists"]:
            try:
                pkg_bytes = AsarBinaryHelper.read_file(self.asar_path, "package.json")
                result["version"] = json.loads(pkg_bytes.decode("utf-8")).get("version")
            except Exception:
                pass

            try:
                preload_bytes = AsarBinaryHelper.read_file(self.asar_path, "dist/preload.js")
                if PATCH_MARKER in preload_bytes.decode("utf-8"):
                    result["is_patched"] = True
            except Exception:
                pass

        if os.path.isfile(self.daemon_conf):
            try:
                with open(self.daemon_conf, "r") as f:
                    conf = json.load(f)
                    result["daemon_enabled"] = conf.get("enabled", False)
            except Exception:
                pass

        # Healthy if ASAR exists, is patched, and backup exists
        result["healthy"] = result["asar_exists"] and result["is_patched"] and result["backup_exists"]
        return result

    def restore(self):
        """--restore / -r: Reverts app.asar to app.asar.bak."""
        if not os.path.isfile(self.backup_path):
            raise FileNotFoundError("Backup app.asar.bak not found")
        shutil.copy2(self.backup_path, self.asar_path)
        return {"status": "success", "message": "Restored original backup"}

    def uninstall(self):
        """--uninstall / -u: Restores clean app.asar.bak, deletes patcher configs, disables daemon."""
        res = self.restore()
        self.daemon(action="disable")
        if os.path.isdir(self.patcher_dir):
            shutil.rmtree(self.patcher_dir, ignore_errors=True)
        return {"status": "success", "message": "Successfully uninstalled patch"}

    def daemon(self, action="status"):
        """--daemon <enable|disable|status>: Manages background auto-healing watcher."""
        os.makedirs(self.patcher_dir, exist_ok=True)
        if action == "enable":
            with open(self.daemon_conf, "w") as f:
                json.dump({"enabled": True, "target_asar": self.asar_path}, f)
            return {"daemon": "enabled"}
        elif action == "disable":
            if os.path.isfile(self.daemon_conf):
                os.remove(self.daemon_conf)
            return {"daemon": "disabled"}
        elif action == "status":
            enabled = False
            if os.path.isfile(self.daemon_conf):
                with open(self.daemon_conf, "r") as f:
                    enabled = json.load(f).get("enabled", False)
            return {"daemon": "enabled" if enabled else "disabled"}
        else:
            raise ValueError(f"Unknown daemon action: {action}")


# ==============================================================================
# CDN Multi-Mirror Waterfall Simulator
# ==============================================================================

class MockCdnWaterfallDownloader:
    """Simulates multi-mirror CDN waterfall with network error & fallback capabilities."""

    def __init__(self, mirror_responses=None):
        self.mirrors = [
            "https://fastly.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/dist/preload.js",
            "https://testingcf.jsdelivr.net/gh/good9527/Antigravity-Chinese-Patch@main/dist/preload.js",
            "https://ghfast.top/https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/dist/preload.js",
            "https://raw.githubusercontent.com/good9527/Antigravity-Chinese-Patch/main/dist/preload.js"
        ]
        # mirror_responses maps url -> content or Exception
        default_content = f"{PATCH_MARKER}\n// CDN Downloaded Patch Code"
        self.mirror_responses = mirror_responses if mirror_responses is not None else {
            url: default_content for url in self.mirrors
        }
        self.attempted_urls = []

    def download_patch(self):
        self.attempted_urls = []
        for url in self.mirrors:
            self.attempted_urls.append(url)
            resp = self.mirror_responses.get(url)
            if isinstance(resp, Exception):
                continue
            if isinstance(resp, str) and len(resp) > 0:
                return resp
        return None


# ==============================================================================
# TIER 3: Cross-Feature Integration Tests
# ==============================================================================

class TestCliFlagsSuite(unittest.TestCase):
    """
    Tier 3: CLI Flags Pairwise & Integration Suite:
    Tests --install, --check, --restore, --uninstall, --daemon in quiet and normal modes.
    """
    TIER = 3

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_cli_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir, version="2.10.0", is_initially_patched=False)
        self.cli = InstallerCliController(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_cli_check_on_fresh_unpatched_environment(self):
        """Tier 3: --check on unpatched environment reports healthy=False, is_patched=False."""
        diag = self.cli.check()
        self.assertEqual(diag["version"], "2.10.0")
        self.assertFalse(diag["is_patched"])
        self.assertFalse(diag["healthy"])

    def test_02_cli_install_creates_backup_patches_asar_and_enables_daemon(self):
        """Tier 3: --install performs end-to-end installation and enables daemon."""
        install_res = self.cli.install(quiet=True)
        self.assertEqual(install_res["status"], "success")

        # Verify state via --check
        diag = self.cli.check()
        self.assertTrue(diag["asar_exists"])
        self.assertTrue(diag["is_patched"])
        self.assertTrue(diag["backup_exists"])
        self.assertTrue(diag["daemon_enabled"])
        self.assertTrue(diag["healthy"])

    def test_03_cli_restore_reverts_to_unpatched_backup(self):
        """Tier 3: --restore restores original unpatched app.asar from backup."""
        self.cli.install(quiet=True)
        self.assertTrue(self.cli.check()["is_patched"])

        restore_res = self.cli.restore()
        self.assertEqual(restore_res["status"], "success")

        diag = self.cli.check()
        self.assertFalse(diag["is_patched"])
        self.assertTrue(diag["backup_exists"])

    def test_04_cli_uninstall_restores_and_removes_daemon(self):
        """Tier 3: --uninstall restores backup and disables daemon."""
        self.cli.install(quiet=True)
        self.assertTrue(self.cli.check()["daemon_enabled"])

        uninst_res = self.cli.uninstall()
        self.assertEqual(uninst_res["status"], "success")

        diag = self.cli.check()
        self.assertFalse(diag["is_patched"])
        self.assertFalse(diag["daemon_enabled"])

    def test_05_cli_daemon_management(self):
        """Tier 3: --daemon enable/disable/status lifecycle."""
        self.cli.daemon("enable")
        self.assertEqual(self.cli.daemon("status")["daemon"], "enabled")

        self.cli.daemon("disable")
        self.assertEqual(self.cli.daemon("status")["daemon"], "disabled")


class TestMultiMirrorCdnWaterfall(unittest.TestCase):
    """
    Tier 3: Multi-mirror CDN waterfall simulation with network timeouts and fallback.
    """
    TIER = 3

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_cdn_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_primary_cdn_success(self):
        """Tier 3: Download succeeds from primary mirror (Fastly jsDelivr)."""
        downloader = MockCdnWaterfallDownloader()
        cli = InstallerCliController(self.temp_dir, cdn_downloader=downloader)
        res = cli.install(quiet=True)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(downloader.attempted_urls), 1)
        self.assertIn("fastly.jsdelivr.net", downloader.attempted_urls[0])

    def test_02_primary_cdn_timeout_falls_back_to_secondary(self):
        """Tier 3: Primary CDN fails (timeout/500), waterfall falls back to testingcf."""
        mirrors = MockCdnWaterfallDownloader().mirrors
        responses = {
            mirrors[0]: TimeoutError("Connection timed out"),
            mirrors[1]: f"{PATCH_MARKER}\n// Downloaded from testingcf",
            mirrors[2]: "fail",
            mirrors[3]: "fail"
        }
        downloader = MockCdnWaterfallDownloader(mirror_responses=responses)
        cli = InstallerCliController(self.temp_dir, cdn_downloader=downloader)
        cli.install(quiet=True)

        self.assertEqual(len(downloader.attempted_urls), 2)
        self.assertIn("testingcf.jsdelivr.net", downloader.attempted_urls[1])

        # Verify patch content
        patched_content = AsarBinaryHelper.read_file(cli.asar_path, "dist/preload.js").decode("utf-8")
        self.assertIn("Downloaded from testingcf", patched_content)

    def test_03_first_two_cdns_fail_falls_back_to_ghfast(self):
        """Tier 3: First two mirrors fail, falls back to ghfast.top acceleration proxy."""
        mirrors = MockCdnWaterfallDownloader().mirrors
        responses = {
            mirrors[0]: ConnectionResetError("Connection reset"),
            mirrors[1]: RuntimeError("HTTP 502 Bad Gateway"),
            mirrors[2]: f"{PATCH_MARKER}\n// Downloaded from ghfast.top",
            mirrors[3]: "fail"
        }
        downloader = MockCdnWaterfallDownloader(mirror_responses=responses)
        cli = InstallerCliController(self.temp_dir, cdn_downloader=downloader)
        cli.install(quiet=True)

        self.assertEqual(len(downloader.attempted_urls), 3)
        self.assertIn("ghfast.top", downloader.attempted_urls[2])

    def test_04_all_cdns_fail_raises_runtime_error_cleanly(self):
        """Tier 3: All 4 mirrors fail -> raises clean RuntimeError without corrupting ASAR."""
        mirrors = MockCdnWaterfallDownloader().mirrors
        responses = {url: TimeoutError("Network unreachable") for url in mirrors}
        downloader = MockCdnWaterfallDownloader(mirror_responses=responses)
        cli = InstallerCliController(self.temp_dir, cdn_downloader=downloader)

        with self.assertRaises(RuntimeError):
            cli.install(quiet=True)

        # Ensure local app.asar is not left corrupted or partially written
        self.assertTrue(os.path.isfile(cli.asar_path))
        diag = cli.check()
        self.assertFalse(diag["is_patched"])


if __name__ == "__main__":
    unittest.main()
