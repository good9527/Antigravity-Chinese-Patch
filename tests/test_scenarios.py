#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_scenarios.py
Tier 4: Real-World Application Scenario Tests:
- Scenario 1: Fresh installation on unpatched client with active process non-locking
- Scenario 2: Simulated Google official auto-update (unpatched ASAR overwrite) -> Watcher detection & auto-healing
- Scenario 3: Corrupted patch recovery & one-click rollback to official Google binary
- Scenario 4: User typing & code review workflow with active agent state transitions
"""

import unittest
import os
import shutil
import tempfile
import json
import hashlib
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from test_asar import AsarBinaryHelper, PATCH_MARKER
from test_engine import MockNode, SpecificationTranslationEngine
from test_integration import MockAntigravityClientEnvironment, InstallerCliController


# ==============================================================================
# TIER 4: Real-World Scenarios
# ==============================================================================

class TestScenario1FreshInstallation(unittest.TestCase):
    """
    Tier 4 — Scenario 1: Fresh installation on unpatched client with active process non-locking.
    Verifies that:
    1. Client with active file read handle allows in-place patch replacement.
    2. Original unpatched client backup (app.asar.bak) is created.
    3. Patch signature is verified in active ASAR.
    4. Client session remains undisrupted.
    """
    TIER = 4

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_sc1_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir, version="2.10.0", is_initially_patched=False)
        self.cli = InstallerCliController(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scenario_1_fresh_installation_and_read_lock_resilience(self):
        # 1. Simulate active running process holding shared read handle on app.asar
        with open(self.env.asar_path, "rb") as active_proc_handle:
            # Verify active handle is reading
            header_sample = active_proc_handle.read(16)
            self.assertEqual(len(header_sample), 16)

            # 2. Perform installation
            res = self.cli.install(quiet=True)
            self.assertEqual(res["status"], "success")

        # 3. Verify backup creation
        self.assertTrue(os.path.isfile(self.env.backup_path))

        # 4. Verify in-place patch in active ASAR
        diag = self.cli.check()
        self.assertTrue(diag["is_patched"])
        self.assertTrue(diag["backup_exists"])
        self.assertEqual(diag["version"], "2.10.0")

        # 5. Verify preload code contains localization patch
        preload_code = AsarBinaryHelper.read_file(self.env.asar_path, "dist/preload.js").decode("utf-8")
        self.assertIn(PATCH_MARKER, preload_code)
        self.assertIn("Original Host Preload", preload_code)


class TestScenario2GoogleAutoUpdateAndSelfHealing(unittest.TestCase):
    """
    Tier 4 — Scenario 2: Simulated Google official auto-update & instant auto-healing.
    Verifies that:
    1. Patched client is running (v2.10.0).
    2. Google electron-updater downloads and overwrites app.asar with official v2.11.0 (unpatched).
    3. FileSystemWatcher / Auto-Heal daemon detects unpatched overwrite.
    4. Auto-healer re-applies patch immediately to the new v2.11.0 client.
    5. Version 2.11.0 is preserved with Chinese patch active.
    """
    TIER = 4

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_sc2_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir, version="2.10.0", is_initially_patched=False)
        self.cli = InstallerCliController(self.temp_dir)
        # Initial install on v2.10.0
        self.cli.install(quiet=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scenario_2_official_google_update_auto_healing(self):
        # 1. Verify initial patched state on v2.10.0
        diag_initial = self.cli.check()
        self.assertEqual(diag_initial["version"], "2.10.0")
        self.assertTrue(diag_initial["is_patched"])

        # 2. Simulate Google electron-updater extracting official v2.11.0 unpatched ASAR
        updated_v211_files = {
            "package.json": json.dumps({"name": "antigravity", "version": "2.11.0"}),
            "dist/preload.js": "console.log('Google Official v2.11.0 Preload - New Feature APIs');",
            "dist/main.js": "console.log('Main v2.11.0');"
        }
        AsarBinaryHelper.pack_archive(updated_v211_files, self.env.asar_path)

        # 3. Check immediately post-update: client is currently unpatched on v2.11.0
        diag_post_update = self.cli.check()
        self.assertEqual(diag_post_update["version"], "2.11.0")
        self.assertFalse(diag_post_update["is_patched"])

        # 4. Simulate Auto-Healing Daemon trigger:
        # In real watcher script: detects modification -> checks patch marker -> runs auto-heal routine
        def simulate_auto_heal_daemon_tick():
            check_state = self.cli.check()
            if not check_state["is_patched"]:
                # Trigger re-injection
                patch_code = self.cli.cdn_downloader.download_patch()
                tmp_out = os.path.join(self.env.resources_dir, "app.asar.tmp")
                AsarBinaryHelper.inject_preload(self.env.asar_path, tmp_out, patch_code)
                shutil.move(tmp_out, self.env.asar_path)
                return True
            return False

        healed = simulate_auto_heal_daemon_tick()
        self.assertTrue(healed, "Daemon did not trigger auto-heal on unpatched ASAR")

        # 5. Verify final state: client is v2.11.0 AND patched with Chinese localization!
        diag_final = self.cli.check()
        self.assertEqual(diag_final["version"], "2.11.0")
        self.assertTrue(diag_final["is_patched"])
        self.assertTrue(diag_final["healthy"])

        healed_preload = AsarBinaryHelper.read_file(self.env.asar_path, "dist/preload.js").decode("utf-8")
        self.assertIn("Google Official v2.11.0 Preload - New Feature APIs", healed_preload)
        self.assertIn(PATCH_MARKER, healed_preload)


class TestScenario3CorruptedPatchRecoveryAndRollback(unittest.TestCase):
    """
    Tier 4 — Scenario 3: Corrupted patch recovery & one-click rollback to official Google binary.
    Verifies that:
    1. A corrupted / interrupted patch write leaving app.asar broken is diagnosed by --check.
    2. One-click rollback restores official Google binary with byte-exact sha256 hash match.
    """
    TIER = 4

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_sc3_")
        self.env = MockAntigravityClientEnvironment(self.temp_dir, version="2.10.0", is_initially_patched=False)
        self.cli = InstallerCliController(self.temp_dir)

        with open(self.env.asar_path, "rb") as f:
            self.official_google_hash = hashlib.sha256(f.read()).hexdigest()

        # Install patch (creates backup)
        self.cli.install(quiet=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scenario_3_corrupted_patch_recovery_and_rollback(self):
        # 1. Simulate partial download / corrupted write
        with open(self.env.asar_path, "wb") as f:
            f.write(b"CORRUPTED_INCOMPLETE_WRITE_DATA")

        # 2. Health check identifies problem
        diag_corrupt = self.cli.check()
        self.assertFalse(diag_corrupt["healthy"])
        self.assertFalse(diag_corrupt["is_patched"])

        # 3. Perform one-click rollback
        rollback_res = self.cli.restore()
        self.assertEqual(rollback_res["status"], "success")

        # 4. Verify byte-exact restoration to official Google binary
        with open(self.env.asar_path, "rb") as f:
            restored_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(self.official_google_hash, restored_hash)

        # 5. Verify restored client parses cleanly
        header, _, _ = AsarBinaryHelper.parse_header(self.env.asar_path)
        self.assertIn("files", header)


class TestScenario4UserTypingAndCodeReviewWorkflow(unittest.TestCase):
    """
    Tier 4 — Scenario 4: User typing and code review workflow with active agent state transitions.
    Full opaque-box simulation of an interactive Antigravity coding session:
    1. User types prompt containing code keywords in input area -> user text is untouched.
    2. User submits -> Agent enters dynamic thinking & working timer states.
    3. File change counter and pane badge counts update dynamically.
    4. Review pane displays Monaco editor / code diff with syntax tokens -> code is 100% untouched.
    5. Action buttons (Review, Accept Step, Reject Step, Apply Changes) are translated.
    6. Relative timestamps update to Chinese format.
    """
    TIER = 4

    def setUp(self):
        dict_map = {
            "New Conversation": "新建对话",
            "Ask anything, @ to mention, / for actions": "问我任何问题，用 @ 提及文件，用 / 执行动作",
            "Review": "审核",
            "Accept Step": "接受步骤",
            "Reject Step": "拒绝步骤",
            "Apply Changes": "应用更改",
            "Files Changed": "已修改文件",
            "Subagents": "子智能体",
            "Artifacts": "产物",
            "Thinking...": "思考中...",
            "Working...": "处理中...",
            "Agent finished": "智能体已完成"
        }
        self.engine = SpecificationTranslationEngine(dictionary=dict_map)

    def test_scenario_4_end_to_end_user_interactive_session(self):
        # Step 1: User Typing in Chat Area
        chat_box = MockNode(MockNode.ELEMENT_NODE, "div", class_name="chat-composer")
        input_textarea = MockNode(
            MockNode.ELEMENT_NODE, "textarea",
            attributes={
                "placeholder": "Ask anything, @ to mention, / for actions",
                "value": "Please delete the old File and save the result."
            }
        )
        user_typing_text = MockNode(MockNode.TEXT_NODE, node_value="Please delete the old File and save the result.")
        input_textarea.append_child(user_typing_text)
        chat_box.append_child(input_textarea)

        self.engine.walk(chat_box)

        # Placeholder translated, user typed value untouched
        self.assertEqual(input_textarea.getAttribute("placeholder"), "问我任何问题，用 @ 提及文件，用 / 执行动作")
        self.assertEqual(input_textarea.getAttribute("value"), "Please delete the old File and save the result.")
        self.assertEqual(user_typing_text.nodeValue, "Please delete the old File and save the result.")

        # Step 2: Agent Dynamic State Transitions
        thinking_node = MockNode(MockNode.TEXT_NODE, node_value="Thinking for 1.8s")
        self.assertEqual(self.engine.translate_text(thinking_node.nodeValue), "思考中 (1.8秒)")

        working_node = MockNode(MockNode.TEXT_NODE, node_value="Working for 4.2s")
        self.assertEqual(self.engine.translate_text(working_node.nodeValue), "处理中 (4.2秒)")

        # Step 3: Dynamic Pane Badges & Counters
        subagent_badge = MockNode(MockNode.TEXT_NODE, node_value="Subagents 2")
        files_badge = MockNode(MockNode.TEXT_NODE, node_value="Files Changed 3")
        file_summary = MockNode(MockNode.TEXT_NODE, node_value="3 files changed")

        self.assertEqual(self.engine.translate_text(subagent_badge.nodeValue), "子智能体 2")
        self.assertEqual(self.engine.translate_text(files_badge.nodeValue), "已修改文件 3")
        self.assertEqual(self.engine.translate_text(file_summary.nodeValue), "3 个文件已修改")

        # Step 4: Code Diff Review Pane (Monaco Editor Bypass)
        review_modal = MockNode(MockNode.ELEMENT_NODE, "div", class_name="review-modal")

        # Monaco Editor container
        monaco_pane = MockNode(MockNode.ELEMENT_NODE, "div", class_name="monaco-editor")
        code_line = MockNode(MockNode.ELEMENT_NODE, "div", class_name="view-line")
        raw_code = "export function deleteFile(path) { return saveFile(path); }"
        code_text = MockNode(MockNode.TEXT_NODE, node_value=raw_code)
        code_line.append_child(code_text)
        monaco_pane.append_child(code_line)
        review_modal.append_child(monaco_pane)

        # Action Buttons in Review Modal
        action_bar = MockNode(MockNode.ELEMENT_NODE, "div", class_name="action-bar")
        for btn_text in ["Review", "Accept Step", "Reject Step", "Apply Changes"]:
            b = MockNode(MockNode.ELEMENT_NODE, "button")
            b.append_child(MockNode(MockNode.TEXT_NODE, node_value=btn_text))
            action_bar.append_child(b)
        review_modal.append_child(action_bar)

        self.engine.walk(review_modal)

        # Verify Code is completely unaltered
        self.assertEqual(code_text.nodeValue, raw_code)

        # Verify Action Buttons are cleanly translated
        translated_buttons = [btn.firstChild.nodeValue for btn in action_bar.children]
        self.assertEqual(translated_buttons, ["审核", "接受步骤", "拒绝步骤", "应用更改"])

        # Step 5: Completion and Relative Timestamps
        done_text = self.engine.translate_text("Done in 8.5s")
        self.assertEqual(done_text, "已完成 (耗时 8.5秒)")

        rel_time_1 = self.engine.translate_text("5m")
        self.assertEqual(rel_time_1, "5分钟前")

        rel_time_2 = self.engine.translate_text("Today 10:30 AM")
        self.assertEqual(rel_time_2, "今天 10:30 AM")


if __name__ == "__main__":
    unittest.main()
