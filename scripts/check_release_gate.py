#!/usr/bin/env python3
"""
check_release_gate.py — Enforce CLAUDE.md §10 release gates from status.json.

Used by the pre-push hook (on tag pushes) and the kpi-snapshot CI workflow before snapshotting.
A release is blocked unless every required checklist has passed and the gate is explicitly open.

Rules:
  - checklists.testing.state    == "passed"
  - checklists.security.state   == "passed"
  - checklists.deployment.state == "passed"
  - checklists.seo_pagespeed.state in ("passed", "n/a")
  - release_gate_open == true

Exit code 0 = gate open, 1 = blocked.

Usage:
  python3 scripts/check_release_gate.py [--root DIR]
"""
import argparse
import json
import os
import sys

GREEN, RED, RESET = ("\033[32m", "\033[31m", "\033[0m") if sys.stdout.isatty() else ("", "", "")


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai", "state")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("PRAXIS_ROOT", "."))
    args = ap.parse_args()

    root = find_root(args.root) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Template exemption: the Praxis baseline repo is a TEMPLATE, not a product. Its releases ship the
    # tooling itself (gates closed by design for downstream projects), so product release gates don't apply.
    # A `.praxis-template` marker file at the repo root opts out of the gate. Real projects must NOT have it.
    if os.path.exists(os.path.join(root, ".praxis-template")):
        print(f"{GREEN}✓ .praxis-template present — this is the Praxis baseline; release gate skipped.{RESET}")
        return 0

    status_path = os.path.join(root, ".ai", "state", "status.json")
    if not os.path.exists(status_path):
        print(f"{RED}✗ status.json not found at {status_path}{RESET}")
        return 1

    with open(status_path) as f:
        status = json.load(f)

    failures = []
    checklists = status.get("checklists", {})

    for gate in ("testing", "security", "deployment"):
        st = checklists.get(gate, {}).get("state")
        if st != "passed":
            failures.append(f"{gate} checklist is '{st}' (must be 'passed')")

    seo = checklists.get("seo_pagespeed", {}).get("state")
    if seo not in ("passed", "n/a"):
        failures.append(f"seo_pagespeed checklist is '{seo}' (must be 'passed' or 'n/a')")

    if status.get("release_gate_open") is not True:
        failures.append("release_gate_open is not true")

    if status.get("blockers"):
        failures.append(f"{len(status['blockers'])} open blocker(s) in status.json")

    if failures:
        print(f"{RED}✗ RELEASE GATE CLOSED:{RESET}")
        for fl in failures:
            print(f"{RED}  - {fl}{RESET}")
        print(f"{RED}Resolve gates (rules/03-05, 06 for web) and set release_gate_open=true.{RESET}")
        return 1

    print(f"{GREEN}✓ RELEASE GATE OPEN — all checklists passed.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
