#!/usr/bin/env python3
"""
check_release_gate.py — Enforce CLAUDE.md §10 release gates from status.json.

Used by the pre-push hook (on tag pushes) and the kpi-snapshot CI workflow before snapshotting.
A release is blocked unless every required checklist has passed and the gate is explicitly open.

Rules:
  - docs/architecture/overview.md exists, has no template placeholders, and has real substance
  - viability (Crucible) is current: no BLOCKED/REQUIRED findings from check_viability.py, and the
    48-72h validation test is completed or explicitly waived (rules/09-crucible.md)
  - checklists.testing.state    == "passed"
  - checklists.security.state   == "passed"
  - checklists.deployment.state == "passed"
  - checklists.seo_pagespeed.state in ("passed", "n/a")
  - release_gate_open == true

The architecture check is FILE-BASED on purpose: a self-reported boolean could be flipped true while the
doc stays empty. Verifying the actual file can't be gamed.

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


# Minimum body length (chars, excluding whitespace) for the architecture doc to count as "real".
ARCH_MIN_CHARS = 600
ARCH_PATH = os.path.join("docs", "architecture", "overview.md")


def check_architecture(root):
    """Every project must ship a real architecture description before release. File-based and
    deterministic — returns a failure string, or None if the doc exists and is genuinely filled in."""
    path = os.path.join(root, ARCH_PATH)
    if not os.path.exists(path):
        return f"architecture doc missing: {ARCH_PATH} (describe the system before release)"
    with open(path) as f:
        text = f.read()
    if "REPLACE_" in text or "<FILL" in text or "<...>" in text:
        return f"architecture doc still has template placeholders: {ARCH_PATH} (fill it in)"
    body = "".join(text.split())
    if len(body) < ARCH_MIN_CHARS:
        return f"architecture doc too thin: {ARCH_PATH} (~{len(body)} chars; describe components, data, infra, scaling)"
    return None


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

    # Architecture description is a hard, file-based requirement for every project.
    arch_fail = check_architecture(root)
    if arch_fail:
        failures.append(arch_fail)

    # Idea viability (the Crucible) is a hard requirement: you cannot ship an MVP whose idea was never
    # stress-tested, drifted since its audit, or was KILLed. Fingerprint-based — can't be gamed by a flag.
    try:
        from check_viability import evaluate as viability_evaluate, load_json as via_load
        for level, code, msg in viability_evaluate(root):
            if level in ("BLOCKED", "REQUIRED"):
                failures.append(f"viability [{code}]: {msg}")
        via = via_load(os.path.join(root, ".ai", "state", "viability.json")) or {}
        vt = ((via.get("current") or {}).get("validation_test") or {})
        if vt.get("status") not in ("completed", "waived"):
            failures.append(f"viability [test-incomplete]: the 48-72h validation test is '{vt.get('status')}' — complete it (or waive with a reason) before release (rules/09-crucible.md)")
    except ImportError:
        failures.append("viability: scripts/check_viability.py missing — cannot verify the Crucible gate")

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
        print(f"{RED}Resolve gates (rules/03-05, 06 for web; architecture doc per rules/01) and set release_gate_open=true.{RESET}")
        return 1

    print(f"{GREEN}✓ RELEASE GATE OPEN — architecture doc present; all checklists passed.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
