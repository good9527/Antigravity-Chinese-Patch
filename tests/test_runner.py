#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Test Suite Runner & Orchestrator for Antigravity Chinese Patch
Supports tier-based execution (--tier 1|2|3|4|all), verbose reporting,
diagnostic logs, failure analysis, and summary statistics.
"""

import sys
import os
import unittest
import time
import argparse
import traceback

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root and tests/ directory are in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
TESTS_DIR = os.path.dirname(__file__)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)


class Color:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    @classmethod
    def disable(cls):
        cls.HEADER = ""
        cls.BLUE = ""
        cls.CYAN = ""
        cls.GREEN = ""
        cls.YELLOW = ""
        cls.RED = ""
        cls.BOLD = ""
        cls.UNDERLINE = ""
        cls.RESET = ""


class DetailedTestResult(unittest.TestResult):
    """Custom TestResult capturing timing, diagnostics, and tier classification."""

    def __init__(self, stream=None, descriptions=None, verbosity=1):
        super().__init__(stream, descriptions, verbosity)
        self.verbosity = verbosity
        self.test_timings = {}
        self._test_start_time = 0
        self.successes = []
        self.tier_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, "other": 0}
        self.tier_passed = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, "other": 0}

    def _get_tier(self, test):
        tier = getattr(test, "_test_tier", None)
        if tier is None:
            cls_tier = getattr(test.__class__, "TIER", None)
            tier = cls_tier if cls_tier is not None else "other"
        return tier

    def startTest(self, test):
        super().startTest(test)
        self._test_start_time = time.time()
        tier = self._get_tier(test)
        if tier in self.tier_counts:
            self.tier_counts[tier] += 1
        else:
            self.tier_counts["other"] += 1

        if self.verbosity >= 2:
            test_id = test.id().split(".")[-1]
            cls_name = test.__class__.__name__
            sys.stdout.write(f"  [Tier {tier}] {cls_name}.{test_id} ... ")
            sys.stdout.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        elapsed = time.time() - self._test_start_time
        self.test_timings[test.id()] = elapsed
        self.successes.append(test)
        tier = self._get_tier(test)
        if tier in self.tier_passed:
            self.tier_passed[tier] += 1
        else:
            self.tier_passed["other"] += 1

        if self.verbosity >= 2:
            sys.stdout.write(f"{Color.GREEN}PASS{Color.RESET} ({elapsed*1000:.1f}ms)\n")
        elif self.verbosity == 1:
            sys.stdout.write(f"{Color.GREEN}.{Color.RESET}")
            sys.stdout.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        elapsed = time.time() - self._test_start_time
        self.test_timings[test.id()] = elapsed
        tier = self._get_tier(test)
        if self.verbosity >= 2:
            sys.stdout.write(f"{Color.RED}FAIL{Color.RESET} ({elapsed*1000:.1f}ms)\n")
        elif self.verbosity == 1:
            sys.stdout.write(f"{Color.RED}F{Color.RESET}")
            sys.stdout.flush()

    def addError(self, test, err):
        super().addError(test, err)
        elapsed = time.time() - self._test_start_time
        self.test_timings[test.id()] = elapsed
        tier = self._get_tier(test)
        if self.verbosity >= 2:
            sys.stdout.write(f"{Color.YELLOW}ERROR{Color.RESET} ({elapsed*1000:.1f}ms)\n")
        elif self.verbosity == 1:
            sys.stdout.write(f"{Color.YELLOW}E{Color.RESET}")
            sys.stdout.flush()

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        elapsed = time.time() - self._test_start_time
        self.test_timings[test.id()] = elapsed
        tier = self._get_tier(test)
        if self.verbosity >= 2:
            sys.stdout.write(f"{Color.CYAN}SKIP ({reason}){Color.RESET}\n")
        elif self.verbosity == 1:
            sys.stdout.write(f"{Color.CYAN}S{Color.RESET}")
            sys.stdout.flush()


def load_suite(tier=None):
    """Load tests filtered by tier or all."""
    import test_engine
    import test_asar
    import test_integration
    import test_scenarios
    import test_tier5_adversarial

    modules = [test_engine, test_asar, test_integration, test_scenarios, test_tier5_adversarial]
    loader = unittest.TestLoader()
    full_suite = unittest.TestSuite()

    for mod in modules:
        suite = loader.loadTestsFromModule(mod)
        full_suite.addTests(suite)

    if tier is None or tier == "all":
        return full_suite

    tier_int = int(tier)
    filtered_suite = unittest.TestSuite()

    def filter_tests(test_item):
        if isinstance(test_item, unittest.TestSuite):
            for sub_test in test_item:
                filter_tests(sub_test)
        elif isinstance(test_item, unittest.TestCase):
            test_tier = getattr(test_item, "_test_tier", None)
            if test_tier is None:
                test_tier = getattr(test_item.__class__, "TIER", None)
            if test_tier == tier_int:
                filtered_suite.addTest(test_item)

    filter_tests(full_suite)
    return filtered_suite


def run_tests(tier="all", verbosity=2, no_color=False):
    """Execute test suite and render comprehensive diagnostic report."""
    if no_color or not sys.stdout.isatty():
        # Keep ANSI colors if forced, or disable if unsupported
        if os.name == "nt" and "WT_SESSION" not in os.environ and "TERM" not in os.environ:
            # Enable ANSI escape sequences on Windows console
            os.system("")

    print(f"{Color.BOLD}{Color.CYAN}======================================================================{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}      Antigravity Chinese Patch — Comprehensive E2E Test Suite        {Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}======================================================================{Color.RESET}")
    print(f"  Project Root : {PROJECT_ROOT}")
    print(f"  Target Tier  : {tier.upper() if isinstance(tier, str) else f'Tier {tier}'}")
    print(f"  Python Vers. : {sys.version.split()[0]}")
    print(f"{Color.BOLD}{Color.CYAN}----------------------------------------------------------------------{Color.RESET}")

    suite = load_suite(tier)
    start_wall_time = time.time()
    result = DetailedTestResult(verbosity=verbosity)

    if verbosity == 1:
        print("Running tests: ", end="")

    suite.run(result)

    if verbosity == 1:
        print()

    total_duration = time.time() - start_wall_time

    # Render Failure / Error Diagnostics
    if result.failures:
        print(f"\n{Color.BOLD}{Color.RED}======================================================================{Color.RESET}")
        print(f"{Color.BOLD}{Color.RED}                         FAILURES DIAGNOSTICS                         {Color.RESET}")
        print(f"{Color.BOLD}{Color.RED}======================================================================{Color.RESET}")
        for idx, (test, err) in enumerate(result.failures, 1):
            tier = result._get_tier(test)
            print(f"\n{Color.BOLD}{Color.RED}[{idx}] FAIL (Tier {tier}): {test.id()}{Color.RESET}")
            print(f"{Color.YELLOW}{'-'*70}{Color.RESET}")
            print(err)

    if result.errors:
        print(f"\n{Color.BOLD}{Color.YELLOW}======================================================================{Color.RESET}")
        print(f"{Color.BOLD}{Color.YELLOW}                          ERRORS DIAGNOSTICS                          {Color.RESET}")
        print(f"{Color.BOLD}{Color.YELLOW}======================================================================{Color.RESET}")
        for idx, (test, err) in enumerate(result.errors, 1):
            tier = result._get_tier(test)
            print(f"\n{Color.BOLD}{Color.YELLOW}[{idx}] ERROR (Tier {tier}): {test.id()}{Color.RESET}")
            print(f"{Color.YELLOW}{'-'*70}{Color.RESET}")
            print(err)

    # Render Summary
    print(f"\n{Color.BOLD}{Color.CYAN}======================================================================{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}                          TEST SUITE SUMMARY                          {Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}======================================================================{Color.RESET}")
    print(f"  Total Tests Run : {result.testsRun}")
    print(f"  Passed          : {Color.GREEN}{len(result.successes)}{Color.RESET}")
    print(f"  Failures        : {Color.RED if result.failures else Color.GREEN}{len(result.failures)}{Color.RESET}")
    print(f"  Errors          : {Color.YELLOW if result.errors else Color.GREEN}{len(result.errors)}{Color.RESET}")
    print(f"  Skipped         : {Color.CYAN}{len(result.skipped)}{Color.RESET}")
    print(f"  Total Duration  : {total_duration:.3f}s")
    print(f"{Color.CYAN}----------------------------------------------------------------------{Color.RESET}")
    print("  Tier Breakdown:")
    for t in [1, 2, 3, 4, 5]:
        total_t = result.tier_counts.get(t, 0)
        passed_t = result.tier_passed.get(t, 0)
        status_color = Color.GREEN if (total_t > 0 and passed_t == total_t) else (Color.RED if total_t > 0 else Color.RESET)
        print(f"    - Tier {t}: {status_color}{passed_t}/{total_t} Passed{Color.RESET}")

    is_successful = len(result.failures) == 0 and len(result.errors) == 0
    print(f"{Color.BOLD}{Color.CYAN}======================================================================{Color.RESET}")
    if is_successful:
        print(f"  {Color.BOLD}{Color.GREEN}OVERALL STATUS: ALL ASSIGNED TESTS PASSED [OK]{Color.RESET}")
    else:
        print(f"  {Color.BOLD}{Color.RED}OVERALL STATUS: TESTS FAILED - BUGS DETECTED [FAIL]{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}======================================================================{Color.RESET}\n")

    return 0 if is_successful else 1


def main():
    parser = argparse.ArgumentParser(description="Antigravity Chinese Patch E2E Test Suite Runner")
    parser.add_argument(
        "--tier",
        type=str,
        default="all",
        choices=["1", "2", "3", "4", "5", "all"],
        help="Execute specific test tier (1: Feature Coverage, 2: Boundary/Corner, 3: Integration, 4: Scenarios, 5: Adversarial, all: All)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", default=True, help="Enable verbose test output")
    parser.add_argument("-q", "--quiet", action="store_true", help="Minimal one-character progress output")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")

    args = parser.parse_args()
    verbosity = 1 if args.quiet else (2 if args.verbose else 1)
    exit_code = run_tests(tier=args.tier, verbosity=verbosity, no_color=args.no_color)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
