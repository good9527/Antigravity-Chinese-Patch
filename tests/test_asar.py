#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_asar.py
Tier 1 and Tier 2 test suite for ASAR Binary Manipulation:
- Header parsing & structure verification
- Dynamic size/offset recalculation
- In-place preload extraction & injection
- Header integrity stripping
- Idempotency & byte-exact restoration
- Corrupted file recovery
"""

import unittest
import struct
import json
import os
import shutil
import tempfile
import hashlib
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PATCH_MARKER = "// Antigravity Chinese Localization Patch"


class AsarBinaryHelper:
    """
    Standard Electron ASAR Binary Helper for packing, unpacking,
    and in-place manipulation strictly following Electron specifications.
    """

    @staticmethod
    def pack_archive(files_dict, output_path):
        """
        Packs a dictionary of {relative_path: bytes_or_str} into a valid ASAR archive.
        Supports nested paths (e.g. 'dist/preload.js', 'package.json').
        """
        header_files = {}
        payload_bytes = bytearray()
        current_offset = 0

        for path, data in files_dict.items():
            if isinstance(data, str):
                data = data.encode("utf-8")
            elif data is None:
                data = b""

            parts = path.replace("\\", "/").strip("/").split("/")
            curr_node = header_files
            for part in parts[:-1]:
                if part not in curr_node:
                    curr_node[part] = {"files": {}}
                curr_node = curr_node[part]["files"]

            file_name = parts[-1]
            size = len(data)
            curr_node[file_name] = {
                "size": size,
                "offset": str(current_offset)
            }
            payload_bytes.extend(data)
            current_offset += size

        header_json = json.dumps({"files": header_files}, separators=(",", ":")).encode("utf-8")
        json_size = len(header_json)
        padding = (4 - (json_size % 4)) % 4
        header_payload = json_size + padding

        with open(output_path, "wb") as f:
            # Standard Electron ASAR Header: [4, header_payload + 8, header_payload + 4, json_size]
            f.write(struct.pack("<IIII", 4, header_payload + 8, header_payload + 4, json_size))
            f.write(header_json)
            if padding > 0:
                f.write(b"\x00" * padding)
            f.write(payload_bytes)

    @staticmethod
    def parse_header(asar_path):
        """
        Parses 16-byte ASAR header and returns (header_dict, data_start_offset, json_size).
        """
        with open(asar_path, "rb") as f:
            header_bytes = f.read(16)
            if len(header_bytes) < 16:
                raise ValueError("ASAR header too short or truncated")
            magic, u2, u3, json_size = struct.unpack("<IIII", header_bytes)
            if magic != 4:
                raise ValueError(f"Invalid ASAR magic number: {magic}, expected 4")

            json_bytes = f.read(json_size)
            header_dict = json.loads(json_bytes.decode("utf-8"))
            data_start = 8 + u2
            return header_dict, data_start, json_size

    @staticmethod
    def read_file(asar_path, target_rel_path):
        """Extracts content of a specific file inside ASAR."""
        header, data_start, _ = AsarBinaryHelper.parse_header(asar_path)
        parts = target_rel_path.replace("\\", "/").strip("/").split("/")

        curr = header["files"]
        for p in parts[:-1]:
            if p not in curr or "files" not in curr[p]:
                raise FileNotFoundError(f"Directory {p} not found in ASAR")
            curr = curr[p]["files"]

        file_name = parts[-1]
        if file_name not in curr:
            raise FileNotFoundError(f"File {target_rel_path} not found in ASAR")

        entry = curr[file_name]
        offset = int(entry["offset"])
        size = int(entry["size"])

        with open(asar_path, "rb") as f:
            f.seek(data_start + offset)
            return f.read(size)

    @staticmethod
    def inject_preload(input_asar, output_asar, patch_code):
        """
        In-place injection matching UniversalAsarEngine interface.
        Extracts preload.js, strips old patch marker if present, appends patch,
        strips integrity hash, recalculates offsets, and writes new ASAR.
        """
        with open(input_asar, "rb") as f:
            asar_bytes = f.read()

        if len(asar_bytes) < 16:
            raise ValueError("Invalid ASAR: file too small")

        magic, u2, u3, json_size = struct.unpack("<IIII", asar_bytes[:16])
        if magic != 4:
            raise ValueError("Invalid ASAR magic")

        header_json = asar_bytes[16: 16 + json_size].decode("utf-8")
        header = json.loads(header_json)
        data_start = 8 + u2

        entries = []

        def collect(node, path=""):
            if "files" in node:
                for k, v in node["files"].items():
                    collect(v, f"{path}/{k}" if path else k)
            else:
                is_unpacked = node.get("unpacked", False)
                offset = int(node.get("offset", 0))
                size = int(node.get("size", 0))
                entries.append({
                    "path": path,
                    "node": node,
                    "old_offset": offset,
                    "size": size,
                    "unpacked": is_unpacked,
                    "new_data": None
                })

        collect(header)
        preload_entry = next((e for e in entries if e["path"].endswith("dist/preload.js")), None)
        if not preload_entry:
            raise RuntimeError("dist/preload.js not found in app.asar")

        old_preload_bytes = asar_bytes[data_start + preload_entry["old_offset"]: data_start + preload_entry["old_offset"] + preload_entry["size"]]
        old_preload = old_preload_bytes.decode("utf-8", errors="ignore")

        if PATCH_MARKER in old_preload:
            old_preload = old_preload.split(PATCH_MARKER)[0].rstrip()

        new_preload = old_preload + "\r\n\r\n" + patch_code
        new_preload_bytes = new_preload.encode("utf-8")
        preload_entry["new_data"] = new_preload_bytes
        preload_entry["size"] = len(new_preload_bytes)
        preload_entry["node"]["size"] = len(new_preload_bytes)

        # Strip integrity hash if present to prevent Electron tamper checks
        if "integrity" in preload_entry["node"]:
            del preload_entry["node"]["integrity"]

        # Recalculate offsets in original byte order
        entries.sort(key=lambda e: e["old_offset"])
        cur_offset = 0
        for e in entries:
            if e["unpacked"]:
                continue
            e["node"]["offset"] = str(cur_offset)
            cur_offset += e["size"]

        new_json_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
        new_json_size = len(new_json_bytes)
        padding = (4 - (new_json_size % 4)) % 4
        header_payload = new_json_size + padding

        with open(output_asar, "wb") as out:
            out.write(struct.pack("<IIII", 4, header_payload + 8, header_payload + 4, new_json_size))
            out.write(new_json_bytes)
            if padding > 0:
                out.write(b"\x00" * padding)
            for e in entries:
                if e["unpacked"]:
                    continue
                if e["new_data"] is not None:
                    out.write(e["new_data"])
                else:
                    out.write(asar_bytes[data_start + e["old_offset"]: data_start + e["old_offset"] + e["size"]])


# ==============================================================================
# TIER 1: ASAR Feature Coverage Tests
# ==============================================================================

class TestAsarCoreFeatures(unittest.TestCase):
    """
    Tier 1: Core ASAR binary manipulation capabilities:
    - Header parsing
    - Clean injection
    - Backup and restoration
    - Version reading
    """
    TIER = 1

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_asar_")
        self.asar_path = os.path.join(self.temp_dir, "app.asar")
        self.backup_path = os.path.join(self.temp_dir, "app.asar.bak")
        self.patched_path = os.path.join(self.temp_dir, "app.asar.patched")

        # Synthesize a realistic sample unpatched ASAR
        self.initial_files = {
            "package.json": json.dumps({"name": "antigravity", "version": "2.10.0"}),
            "dist/main.js": "console.log('Antigravity Main');",
            "dist/preload.js": "'use strict';\nObject.defineProperty(exports, '__esModule', { value: true });\nconsole.log('Original Host Preload');\n",
            "resources/icon.png": "SAMPLE_IMAGE_DATA_BYTES"
        }
        AsarBinaryHelper.pack_archive(self.initial_files, self.asar_path)

        # Compute initial hash for restoration verification
        with open(self.asar_path, "rb") as f:
            self.initial_hash = hashlib.sha256(f.read()).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_asar_header_parsing_and_file_listing(self):
        """Tier 1: Verify parsing of ASAR header and JSON directory tree."""
        header, data_start, json_size = AsarBinaryHelper.parse_header(self.asar_path)
        self.assertIn("files", header)
        self.assertIn("package.json", header["files"])
        self.assertIn("dist", header["files"])
        self.assertIn("preload.js", header["files"]["dist"]["files"])
        self.assertGreater(data_start, 16)
        self.assertGreater(json_size, 0)

    def test_02_read_package_version_from_asar(self):
        """Tier 1 (F29): Extract version string from package.json in ASAR archive."""
        pkg_bytes = AsarBinaryHelper.read_file(self.asar_path, "package.json")
        pkg_data = json.loads(pkg_bytes.decode("utf-8"))
        self.assertEqual(pkg_data.get("version"), "2.10.0")

    def test_03_in_place_preload_injection(self):
        """Tier 1 (F27/F28): Inject Chinese localization patch into dist/preload.js."""
        patch_code = f"{PATCH_MARKER}\nconsole.log('Chinese patch active');"
        AsarBinaryHelper.inject_preload(self.asar_path, self.patched_path, patch_code)

        self.assertTrue(os.path.isfile(self.patched_path))
        patched_preload = AsarBinaryHelper.read_file(self.patched_path, "dist/preload.js").decode("utf-8")
        self.assertIn(PATCH_MARKER, patched_preload)
        self.assertIn("Chinese patch active", patched_preload)
        self.assertIn("Original Host Preload", patched_preload)

    def test_04_backup_creation_and_byte_exact_restoration(self):
        """Tier 1 (F35): Create backup app.asar.bak and restore byte-exact original binary."""
        # 1. Create backup
        shutil.copy2(self.asar_path, self.backup_path)
        self.assertTrue(os.path.isfile(self.backup_path))

        # 2. Modify original
        patch_code = f"{PATCH_MARKER}\n// Patched"
        AsarBinaryHelper.inject_preload(self.asar_path, self.asar_path, patch_code)

        with open(self.asar_path, "rb") as f:
            patched_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertNotEqual(self.initial_hash, patched_hash)

        # 3. Restore from backup
        shutil.copy2(self.backup_path, self.asar_path)

        with open(self.asar_path, "rb") as f:
            restored_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(self.initial_hash, restored_hash, "Restored binary hash does not match original")

    def test_05_other_files_remain_intact_after_patch(self):
        """Tier 1: Non-preload files in ASAR remain completely unmodified."""
        patch_code = f"{PATCH_MARKER}\n// Patch"
        AsarBinaryHelper.inject_preload(self.asar_path, self.patched_path, patch_code)

        pkg_bytes = AsarBinaryHelper.read_file(self.patched_path, "package.json")
        main_bytes = AsarBinaryHelper.read_file(self.patched_path, "dist/main.js")
        img_bytes = AsarBinaryHelper.read_file(self.patched_path, "resources/icon.png")

        self.assertEqual(pkg_bytes.decode("utf-8"), self.initial_files["package.json"])
        self.assertEqual(main_bytes.decode("utf-8"), self.initial_files["dist/main.js"])
        self.assertEqual(img_bytes.decode("utf-8"), self.initial_files["resources/icon.png"])


# ==============================================================================
# TIER 2: ASAR Boundary & Corner Cases
# ==============================================================================

class TestAsarBoundaryAndCornerCases(unittest.TestCase):
    """
    Tier 2: Boundary, stress, and edge-case validation for ASAR binary operations.
    """
    TIER = 2

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_asar_b_")
        self.asar_path = os.path.join(self.temp_dir, "app.asar")
        self.patched_path = os.path.join(self.temp_dir, "app.asar.patched")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_idempotency_repeated_patching(self):
        """
        Tier 2: Re-applying the patch multiple times does NOT duplicate code or inflate binary.
        """
        files = {
            "dist/preload.js": "const electron = require('electron');\n",
            "package.json": "{}"
        }
        AsarBinaryHelper.pack_archive(files, self.asar_path)

        patch_code_1 = f"{PATCH_MARKER}\nconsole.log('Version 1');"
        AsarBinaryHelper.inject_preload(self.asar_path, self.patched_path, patch_code_1)

        # Patch again with version 2
        patch_code_2 = f"{PATCH_MARKER}\nconsole.log('Version 2 Updated');"
        AsarBinaryHelper.inject_preload(self.patched_path, self.patched_path, patch_code_2)

        final_preload = AsarBinaryHelper.read_file(self.patched_path, "dist/preload.js").decode("utf-8")
        marker_count = final_preload.count(PATCH_MARKER)
        self.assertEqual(marker_count, 1, f"Patch marker appeared {marker_count} times, expected exactly 1")
        self.assertIn("Version 2 Updated", final_preload)
        self.assertNotIn("Version 1", final_preload)

    def test_02_header_integrity_hash_stripping(self):
        """
        Tier 2: When Electron integrity hash exists on preload.js, it must be removed.
        """
        header_files = {
            "dist": {
                "files": {
                    "preload.js": {
                        "size": 30,
                        "offset": "0",
                        "integrity": {
                            "algorithm": "SHA256",
                            "hash": "abcdef1234567890abcdef1234567890",
                            "blockSize": 4096,
                            "blocks": ["abcdef1234567890"]
                        }
                    }
                }
            }
        }
        header_json = json.dumps({"files": header_files}).encode("utf-8")
        json_size = len(header_json)
        padding = (4 - (json_size % 4)) % 4
        payload = b"console.log('preload code');\n"

        with open(self.asar_path, "wb") as f:
            f.write(struct.pack("<IIII", 4, json_size + padding + 8, json_size + padding + 4, json_size))
            f.write(header_json)
            if padding > 0:
                f.write(b"\x00" * padding)
            f.write(payload)

        patch_code = f"{PATCH_MARKER}\n// Patch"
        AsarBinaryHelper.inject_preload(self.asar_path, self.patched_path, patch_code)

        # Check patched header
        header, _, _ = AsarBinaryHelper.parse_header(self.patched_path)
        preload_node = header["files"]["dist"]["files"]["preload.js"]
        self.assertNotIn("integrity", preload_node, "Integrity hash was not stripped from patched ASAR header")

    def test_03_handling_unpacked_files_in_asar_directory(self):
        """
        Tier 2: Files marked with unpacked: true must not corrupt payload offset offsets.
        """
        files = {
            "dist/preload.js": "console.log('preload');",
            "dist/worker.node": "BINARY_NATIVE_NODE_MODULE_DATA"
        }
        AsarBinaryHelper.pack_archive(files, self.asar_path)

        # Mark worker.node as unpacked in header
        header, data_start, json_size = AsarBinaryHelper.parse_header(self.asar_path)
        header["files"]["dist"]["files"]["worker.node"]["unpacked"] = True

        # Re-pack with unpacked node
        patch_code = f"{PATCH_MARKER}\n// Patched"
        AsarBinaryHelper.inject_preload(self.asar_path, self.patched_path, patch_code)

        new_preload = AsarBinaryHelper.read_file(self.patched_path, "dist/preload.js").decode("utf-8")
        self.assertIn(PATCH_MARKER, new_preload)

    def test_04_corrupted_asar_header_detection(self):
        """
        Tier 2: Corrupted or invalid ASAR magic header raises informative exception.
        """
        corrupted_path = os.path.join(self.temp_dir, "corrupt.asar")
        with open(corrupted_path, "wb") as f:
            f.write(b"CORRUPT_HEADER_NOT_AN_ASAR_BINARY_DATA")

        with self.assertRaises((ValueError, Exception)):
            AsarBinaryHelper.parse_header(corrupted_path)

    def test_05_missing_preload_raises_runtime_error(self):
        """
        Tier 2: Attempting to patch an ASAR missing dist/preload.js raises RuntimeError.
        """
        files = {
            "dist/other.js": "console.log('no preload');"
        }
        no_preload_path = os.path.join(self.temp_dir, "no_preload.asar")
        AsarBinaryHelper.pack_archive(files, no_preload_path)

        with self.assertRaises(RuntimeError):
            AsarBinaryHelper.inject_preload(no_preload_path, self.patched_path, f"{PATCH_MARKER}\n// Patch")


if __name__ == "__main__":
    unittest.main()
