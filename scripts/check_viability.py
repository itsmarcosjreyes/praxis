#!/usr/bin/env python3
"""
check_viability.py — The Crucible trigger engine (rules/09-crucible.md).

WHY THIS EXISTS:
  Praxis validates HOW a project is built; the Crucible validates WHETHER the idea in PROJECT.md deserves to
  be built. This script is the machine layer that answers: "does the idea need to be (re-)audited right
  now?" It never runs the audit itself — the council is agent work — it detects the conditions that demand
  one and blocks/warns accordingly.

HOW STALENESS IS DETECTED (the fingerprint):
  The idea-defining sections of PROJECT.md (goal, non-goals, primary KPI, audience, MVP, constraints) are
  normalized and hashed. The Crucible stamps that fingerprint into .ai/state/viability.json when the audit is
  written. If the sections change later, the hashes diverge and the audit is stale — no self-reported flag to
  forget or fake. Cosmetic edits elsewhere in PROJECT.md (stack, horizons wording) do NOT invalidate an audit.

FINDING LEVELS:
  BLOCKED     — building on a KILL verdict with no logged override decision. Hard stop everywhere.
  REQUIRED    — an audit (or audit follow-through) is owed before build work: never audited, idea drifted,
                unapplied RESHAPE, validation test overdue. Fails CI and the release gate; Pre-Flight must
                convene the council first.
  RECOMMENDED — strong signal to re-audit: test never started, audit older than config.revalidate_after_days,
                primary KPI off-track for config.kpi_offtrack_streak consecutive snapshots, MVP phase
                boundary crossed. Warns only.
  INFO        — nothing owed (idea not authored yet, or audit current).

TEMPLATE EXEMPTION:
  The Praxis baseline repo (.praxis-template marker) has no idea to audit — all checks are skipped, same
  convention as check_release_gate.py.

Exit codes: 0 = nothing owed (or --warn-only), 1 = REQUIRED/BLOCKED findings.

Usage:
  python3 scripts/check_viability.py [--root DIR] [--warn-only] [--print-fingerprint]
    --warn-only          report findings but always exit 0 (pre-commit uses this)
    --print-fingerprint  print the current PROJECT.md idea fingerprint and exit (the Crucible stamps this
                         into viability.json when writing an audit)
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

GREEN, RED, YELLOW, CYAN, RESET = (
    ("\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[0m") if sys.stdout.isatty() else ("", "", "", "", "")
)

# The idea-defining sections of PROJECT.md. Changing any of these means the audited idea is no longer the
# idea on disk. Stack/horizons/identity are deliberately excluded — tooling changes don't invalidate a verdict.
IDEA_SECTIONS = [
    "goal (one sentence)",
    "non-goals",
    "primary kpi",
    "audience",
    "mvp",
    "constraints",
]


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai", "state")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def split_sections(text):
    """{normalized H2 title: [lines]} — same contract as sync_project.py."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    sections, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = re.sub(r"\s+", " ", m.group(1)).strip().lower()
            sections[cur] = []
        elif cur is not None:
            sections[cur].append(line)
    return sections


def compute_fingerprint(md_text):
    """Stable hash of the idea-defining sections, insensitive to whitespace/blockquote noise."""
    sec = split_sections(md_text)
    parts = []
    for name in IDEA_SECTIONS:
        lines = [ln.strip() for ln in sec.get(name, []) if ln.strip() and not ln.strip().startswith(">")]
        parts.append(name + "::" + " ".join(lines).lower())
    blob = "\n".join(re.sub(r"\s+", " ", p) for p in parts)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def goal_is_authored(md_text):
    sec = split_sections(md_text)
    lines = [ln.strip() for ln in sec.get("goal (one sentence)", []) if ln.strip() and not ln.strip().startswith(">")]
    goal = " ".join(lines)
    return bool(goal) and "REPLACE" not in goal


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def parse_date(s):
    if not s:
        return None
    try:
        return datetime.date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def evaluate(root, today=None):
    """Return a list of findings: (level, code, message). Levels: BLOCKED > REQUIRED > RECOMMENDED > INFO."""
    today = today or datetime.date.today()
    findings = []

    md_path = os.path.join(root, "PROJECT.md")
    if not os.path.exists(md_path):
        return [("INFO", "no-project-md", "No PROJECT.md — nothing to audit.")]
    with open(md_path) as f:
        md_text = f.read()

    if not goal_is_authored(md_text):
        return [("INFO", "idea-not-authored", "PROJECT.md goal is still a placeholder — author the idea, then the Crucible runs (rules/09-crucible.md).")]

    via = load_json(os.path.join(root, ".ai", "state", "viability.json"))
    if not via:
        return [("REQUIRED", "no-viability-state", "Idea is authored but .ai/state/viability.json is missing/invalid — run the Crucible (rules/09-crucible.md).")]

    cur = via.get("current", {}) or {}
    cfg = via.get("config", {}) or {}
    verdict = cur.get("verdict", "not-run")

    # T1 — authored but never audited
    if verdict == "not-run":
        return [("REQUIRED", "never-audited", "Idea is authored but has NEVER been stress-tested — convene the Crucible council before any build work (rules/09-crucible.md).")]

    # T2 — idea drift (fingerprint mismatch)
    fp_now = compute_fingerprint(md_text)
    fp_audited = cur.get("fingerprint", "")
    if fp_now != fp_audited:
        findings.append(("REQUIRED", "idea-drift",
                         f"PROJECT.md's idea-defining sections changed since the last audit (fingerprint {fp_audited or '<none>'} → {fp_now}) — re-run the Crucible."))

    # T3 — KILL without override
    if verdict == "kill":
        override = (cur.get("kill_override") or {}).get("decision_link")
        if not override:
            findings.append(("BLOCKED", "killed",
                             "Verdict is KILL with no override decision logged — do not build. To proceed anyway, log a human-approved decision and link it in viability.json → kill_override.decision_link."))
        else:
            findings.append(("INFO", "kill-overridden", f"KILL verdict overridden by {override} — proceeding is a logged human decision."))

    # T4 — RESHAPE not applied
    if verdict == "reshape":
        rs = cur.get("reshape") or {}
        if not rs.get("applied") and not rs.get("rejected_decision_link"):
            findings.append(("REQUIRED", "reshape-unapplied",
                             "Verdict is RESHAPE but the pivot was never applied to PROJECT.md (or rejected via a logged decision) — resolve before building."))

    # T5/T6 — validation test discipline
    vt = cur.get("validation_test") or {}
    vt_status = vt.get("status", "not-defined")
    if vt_status == "running":
        due = parse_date(vt.get("due"))
        if due and due < today:
            findings.append(("REQUIRED", "test-overdue",
                             f"The 48-72h validation test is past due ({due.isoformat()}) with no recorded result — record the outcome and re-judge (rules/09-crucible.md §5)."))
    elif vt_status in ("not-defined", "not-started") and verdict in ("go", "reshape"):
        findings.append(("RECOMMENDED", "test-not-started",
                         "The verdict's 48-72h validation test was never started — it is the cheapest way to find out the idea is wrong. Start it or waive it with a reason."))

    # Project context for T7-T9
    proj = load_json(os.path.join(root, ".ai", "state", "project.json")) or {}
    mvp_status = ((proj.get("mvp") or {}).get("status")) or "not-started"

    # T7 — staleness pre-ship
    max_age = int(cfg.get("revalidate_after_days", 45))
    audit_date = parse_date(cur.get("date"))
    if audit_date and mvp_status != "shipped":
        age = (today - audit_date).days
        if age > max_age:
            findings.append(("RECOMMENDED", "audit-stale",
                             f"Audit is {age} days old (limit {max_age}, MVP not shipped) — re-check the assumptions register; re-run the Crucible if any look shaky."))

    # T8 — primary KPI off-track streak
    streak_needed = int(cfg.get("kpi_offtrack_streak", 2))
    primary_kpi = ((proj.get("goal") or {}).get("primary_kpi_id"))
    hist = load_json(os.path.join(root, ".ai", "state", "kpi-history.json")) or {}
    snaps = hist.get("snapshots", []) or []
    if primary_kpi and len(snaps) >= streak_needed:
        streak = 0
        for snap in reversed(snaps):
            vals = {v.get("kpi_id"): v for v in snap.get("values", [])}
            v = vals.get(primary_kpi)
            if v is not None and v.get("on_track") is False:
                streak += 1
            else:
                break
        if streak >= streak_needed:
            findings.append(("RECOMMENDED", "kpi-offtrack",
                             f"Primary KPI '{primary_kpi}' has been off-track for {streak} consecutive release snapshots — reality is disagreeing with the idea; re-run the Crucible."))

    # T9 — phase boundary
    audited_mvp = cur.get("audited_mvp_status", "")
    if audited_mvp and audited_mvp != mvp_status:
        findings.append(("RECOMMENDED", "phase-boundary",
                         f"MVP status moved '{audited_mvp}' → '{mvp_status}' since the audit — re-audit at the phase boundary before committing to the next phase."))

    if not findings:
        findings.append(("INFO", "current", f"Viability audit is current (verdict: {verdict.upper()}, fingerprint {fp_audited})."))
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("PRAXIS_ROOT", "."))
    ap.add_argument("--warn-only", action="store_true", help="Report findings but always exit 0 (pre-commit).")
    ap.add_argument("--print-fingerprint", action="store_true", help="Print the current PROJECT.md idea fingerprint and exit.")
    args = ap.parse_args()

    root = find_root(args.root) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args.print_fingerprint:
        md_path = os.path.join(root, "PROJECT.md")
        if not os.path.exists(md_path):
            print(f"{RED}✗ No PROJECT.md at {md_path}{RESET}")
            return 1
        with open(md_path) as f:
            print(compute_fingerprint(f.read()))
        return 0

    # Template exemption — the baseline has no idea to audit (same convention as check_release_gate.py).
    if os.path.exists(os.path.join(root, ".praxis-template")):
        print(f"{GREEN}✓ .praxis-template present — Praxis baseline; viability check skipped.{RESET}")
        return 0

    findings = evaluate(root)
    color = {"BLOCKED": RED, "REQUIRED": RED, "RECOMMENDED": YELLOW, "INFO": GREEN}
    mark = {"BLOCKED": "✗", "REQUIRED": "✗", "RECOMMENDED": "⚠", "INFO": "✓"}
    for level, code, msg in findings:
        print(f"{color[level]}{mark[level]} [{level}:{code}] {msg}{RESET}")

    hard = [f for f in findings if f[0] in ("BLOCKED", "REQUIRED")]
    if hard:
        print(f"\n{CYAN}→ The Crucible protocol lives in rules/09-crucible.md. Stamp the new fingerprint with: python3 scripts/check_viability.py --print-fingerprint{RESET}")
        if args.warn_only:
            print(f"{YELLOW}(warn-only mode: not blocking){RESET}")
            return 0
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
