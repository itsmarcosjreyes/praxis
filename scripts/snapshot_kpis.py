#!/usr/bin/env python3
"""
snapshot_kpis.py — Append a per-release KPI snapshot to kpi-history.json and record the release.

Automates the post-deploy bookkeeping that was tracked as debt-001:
  1. Builds a snapshot for every KPI in kpis.json.
  2. Pulls each value from a --values JSON map ({"kpi-001": 42.0, ...}) when provided;
     otherwise carries forward the previous value (or null on first run).
  3. Computes delta_vs_prev and on_track (from each KPI's target + direction).
  4. Appends the snapshot to kpi-history.json (idempotent per release tag).
  5. Appends a release entry to memory.json.
  6. (--reset-status) Resets status.json checklists for the next cycle and closes the gate.

The actual metric *values* come from project-specific instrumentation (Amplitude / Supabase / CrUX).
Fetch them in a project-specific CI step and pass via --values; this script owns the bookkeeping.

Usage:
  python3 scripts/snapshot_kpis.py --release v1.2.0 [--git-ref SHA] [--values metrics.json]
                                   [--notes "..."] [--reset-status] [--root DIR]
"""
import argparse
import datetime
import json
import os
import sys

GREEN, RED, YELLOW, RESET = ("\033[32m", "\033[31m", "\033[33m", "\033[0m") if sys.stdout.isatty() else ("", "", "", "")


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai", "state")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def load(path):
    with open(path) as f:
        return json.load(f)


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def on_track(value, target, direction):
    if value is None or target is None:
        return None
    if direction == "lower-is-better":
        return value <= target
    return value >= target


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", required=True, help="Release tag, e.g. v1.2.0")
    ap.add_argument("--git-ref", default=os.environ.get("GITHUB_SHA", ""))
    ap.add_argument("--values", default="", help="JSON file mapping kpi_id -> numeric value")
    ap.add_argument("--notes", default="")
    ap.add_argument("--reset-status", action="store_true")
    ap.add_argument("--root", default=os.environ.get("PRAXIS_ROOT", "."))
    args = ap.parse_args()

    root = find_root(args.root) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state = os.path.join(root, ".ai", "state")
    kpis = load(os.path.join(state, "kpis.json"))
    history = load(os.path.join(state, "kpi-history.json"))
    today = datetime.date.today().isoformat()

    # Idempotency: refuse to duplicate a release snapshot.
    if any(s.get("release") == args.release for s in history.get("snapshots", [])):
        print(f"{YELLOW}⚠ Snapshot for {args.release} already exists — nothing to do.{RESET}")
        return 0

    values = {}
    if args.values and os.path.exists(args.values):
        values = load(args.values)

    # Previous values for delta computation.
    prev = {}
    if history.get("snapshots"):
        for v in history["snapshots"][-1].get("values", []):
            prev[v["kpi_id"]] = v.get("value")

    snap_values = []
    for k in kpis.get("kpis", []):
        kid = k["id"]
        value = values.get(kid, prev.get(kid))  # carry forward if not supplied
        pv = prev.get(kid)
        delta = (value - pv) if isinstance(value, (int, float)) and isinstance(pv, (int, float)) else None
        snap_values.append({
            "kpi_id": kid,
            "value": value,
            "delta_vs_prev": delta,
            "target": k.get("target"),
            "on_track": on_track(value, k.get("target"), k.get("direction")),
        })

    snapshot = {
        "release": args.release,
        "date": today,
        "git_ref": args.git_ref,
        "values": snap_values,
        "notes": args.notes or f"Auto-snapshot for {args.release}.",
    }
    history.setdefault("snapshots", []).append(snapshot)
    history.setdefault("meta", {})["last_updated"] = today
    save(os.path.join(state, "kpi-history.json"), history)
    print(f"{GREEN}✓ KPI snapshot appended for {args.release} ({len(snap_values)} KPIs).{RESET}")

    # Flag regressions.
    regressions = [v["kpi_id"] for v in snap_values if v["on_track"] is False]
    if regressions:
        print(f"{YELLOW}⚠ Off-track KPIs: {', '.join(regressions)}{RESET}")

    # memory.json release entry
    mem_path = os.path.join(state, "memory.json")
    memory = load(mem_path)
    timeline = memory.setdefault("timeline", [])
    existing = [int(e["id"].split("-")[1]) for e in timeline if e.get("id", "").startswith("mem-")]
    next_n = (max(existing) + 1) if existing else 1
    timeline.append({
        "id": f"mem-{next_n:03d}",
        "date": today,
        "type": "release",
        "title": f"Released {args.release}",
        "detail": f"KPI snapshot recorded. Off-track: {', '.join(regressions) if regressions else 'none'}.",
        "links": {"decision": None, "release": args.release, "feature_doc": None},
    })
    memory.setdefault("meta", {})["last_updated"] = today
    if "summary" in memory:
        memory["summary"]["where_we_are"] = f"Shipped {args.release} on {today}."
    save(mem_path, memory)
    print(f"{GREEN}✓ memory.json release entry appended (mem-{next_n:03d}).{RESET}")

    # Optional status reset for next cycle.
    if args.reset_status:
        st_path = os.path.join(state, "status.json")
        status = load(st_path)
        status["current_release"] = args.release
        status["release_gate_open"] = False
        for g in ("testing", "security", "deployment"):
            status.setdefault("checklists", {}).setdefault(g, {})["state"] = "not-run"
            status["checklists"][g]["last_run"] = None
        if "seo_pagespeed" in status.get("checklists", {}):
            cur = status["checklists"]["seo_pagespeed"].get("state")
            status["checklists"]["seo_pagespeed"]["state"] = "n/a" if cur == "n/a" else "not-run"
            status["checklists"]["seo_pagespeed"]["last_run"] = None
        status.setdefault("meta", {})["last_updated"] = today
        save(st_path, status)
        print(f"{GREEN}✓ status.json reset for next cycle (gate closed).{RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
