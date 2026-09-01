#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/run_browser_adversarial.py
Executes the adversarial browser test harness inside real Chromium V8 engine
and validates all safety bypass & sandbox isolation assertions.
"""

import subprocess
import os
import sys
import json
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HTML_PATH = os.path.join(PROJECT_ROOT, "tests", "test_browser_adversarial.html")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def run_browser_tests():
    if not os.path.exists(CHROME_PATH):
        print(f"Error: Chrome executable not found at {CHROME_PATH}")
        return 1

    file_url = f"file:///{HTML_PATH.replace('\\', '/')}"
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--virtual-time-budget=5000",
        "--dump-dom",
        file_url
    ]

    print("Launching Chromium Headless to execute Adversarial Suite...")
    start_time = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    elapsed = time.time() - start_time

    output = proc.stdout
    
    # Extract results summary
    summary_marker_start = '<div id="results-summary"'
    summary_marker_end = '</div>'
    
    if summary_marker_start not in output:
        print("FAIL: Could not locate results summary in DOM output.")
        print("Chromium stderr:", proc.stderr)
        return 1

    sub_start = output.find(summary_marker_start)
    tag_end = output.find('>', sub_start)
    content_end = output.find(summary_marker_end, tag_end)
    summary_json_str = output[tag_end+1:content_end].strip()

    try:
        results = json.loads(summary_json_str)
    except Exception as e:
        print(f"FAIL: Failed to parse results JSON: {e}")
        print("Raw summary string:", summary_json_str)
        # Extract pre log
        pre_start = output.find('<pre id="test-log">')
        pre_end = output.find('</pre>', pre_start)
        if pre_start != -1:
            print("Test Log:\n", output[pre_start+len('<pre id="test-log">'):pre_end])
        return 1

    # Extract test log
    pre_start = output.find('<pre id="test-log">')
    pre_end = output.find('</pre>', pre_start)
    test_log = output[pre_start+len('<pre id="test-log">'):pre_end] if pre_start != -1 else ""

    print("\n" + "=" * 70)
    print("      Chromium Headless Adversarial Test Execution Log")
    print("=" * 70)
    print(test_log.strip())
    print("-" * 70)
    print(f"Total Tests : {results.get('total', 0)}")
    print(f"Passed      : {results.get('passed', 0)}")
    print(f"Failed      : {results.get('failed', 0)}")
    print(f"Execution   : {elapsed:.2f}s")
    print("=" * 70)

    if results.get('failed', 0) == 0 and results.get('total', 0) > 0:
        print("ALL BROWSER ADVERSARIAL TESTS PASSED [OK]\n")
        return 0
    else:
        print("BROWSER ADVERSARIAL TESTS FAILED [FAIL]\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_browser_tests())
