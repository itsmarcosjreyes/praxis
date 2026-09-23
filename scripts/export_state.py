#!/usr/bin/env python3
"""
export_state.py — Emit a normalized, versioned `praxis-export.json` from a project's `.ai/state/`.

WHY THIS EXISTS (the export contract):
  The per-project `.ai/state/*.json` files are the source of truth, but their internal layout can evolve
  with the Praxis schema. A dashboard (or any external consumer) must NOT couple to that internal layout.
  This script produces a STABLE, version-stamped projection — the `praxis-export` contract — so consumers
  can read 1 project or 50 without caring about Praxis internals. Praxis can rev internal schemas freely as
  long as this exporter keeps emitting the contract.

DESIGN:
  - Single source: reads only `.ai/state/*.json` (no network, stdlib only).
  - Portfolio-safe identity: every record is namespaced by `project.slug`. A globally-unique key is
    emitted as `uid = "<slug>:<entity_id>"` so 50 projects can share one table without collisions.
  - Rollups precomputed: `summary` carries the numbers a dashboard shows first (open debt by impact,
    KPI on-track counts, latest release, gate status, health) so a static client needs no aggregation.
  - Relationship graph: `links[]` flattens the cross-references already in state (memory→decision,
    debt→decision, roadmap→kpi/profitability, profitability→kpi) into edges a UI can draw directly.
  - Stable & additive: `export_contract_version` is independent of project `schema_version`. Add fields,
    don't repurpose; consumers ignore unknown fields.

USAGE:
  python3 scripts/export_state.py [--root DIR] [--out praxis-export.json] [--stdout] [--pretty]
Output: writes `praxis-export.json` at the repo root (gitignored by default), or stdout with --stdout.
"""
import argparse
import datetime
import json
import os
import sys

EXPORT_CONTRACT_VERSION = "1.3.0"
GREEN, RED, RESET = ("\033[32m", "\033[31m", "\033[0m") if sys.stdout.isatty() else ("", "", "")


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai", "state")):
            return d
        p = os.path.dirname(d)
        if p == d:
            return None
        d = p


def load(state_dir, name, default):
    path = os.path.join(state_dir, name)
    if not os.path.exists(path):
        return default
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def ns(slug, entity_id):
    """Globally-unique key for portfolio tables."""
    return f"{slug}:{entity_id}" if entity_id else slug


def build_links(slug, decisions, debt, roadmap, profitability, memory, marketing=None):
    """Flatten existing cross-references into a portable edge list for graph/relationship views."""
    edges = []

    def edge(src_type, src_id, rel, dst_type, dst_id):
        if not dst_id:
            return
        edges.append({
            "from": {"type": src_type, "id": src_id, "uid": ns(slug, src_id)},
            "rel": rel,
            "to": {"type": dst_type, "id": dst_id, "uid": ns(slug, dst_id)},
        })

    for d in decisions.get("decisions", []):
        edge("decision", d["id"], "supersedes", "decision", d.get("supersedes"))
        edge("decision", d["id"], "superseded_by", "decision", d.get("superseded_by"))
    for it in debt.get("items", []):
        edge("tech_debt", it["id"], "introduced_by", "decision", it.get("introduced_by_decision"))
        edge("tech_debt", it["id"], "resolved_by", "decision", it.get("resolved_by_decision"))
    for ph in roadmap.get("phases", []):
        for it in ph.get("items", []):
            for kid in (ph.get("kpi_targets") or []):
                edge("roadmap_item", it["id"], "targets_kpi", "kpi", kid)
            edge("roadmap_item", it["id"], "profitability", "profitability", it.get("profitability_link"))
            for dep in (it.get("depends_on") or []):
                edge("roadmap_item", it["id"], "depends_on", "roadmap_item", dep)
    for m in profitability.get("mechanisms", []):
        edge("profitability", m["id"], "measures_kpi", "kpi", m.get("kpi_link"))
    for it in (marketing or {}).get("initiatives", []):
        edge("marketing", it["id"], "targets_kpi", "kpi", it.get("kpi_link"))
    for ev in memory.get("timeline", []):
        links = ev.get("links", {}) or {}
        edge("memory", ev["id"], "about_decision", "decision", links.get("decision"))
        edge("memory", ev["id"], "about_feature", "feature", links.get("feature_doc"))
    return edges


def build_summary(project, status, kpis, history, debt, roadmap, profitability, decisions, memory):
    """Precomputed rollups — the numbers a dashboard shows at a glance."""
    # Tech debt by impact / status
    debt_items = debt.get("items", [])
    open_debt = [d for d in debt_items if d.get("status") in ("open", "scheduled", "in-progress")]
    debt_by_impact = {}
    for d in open_debt:
        debt_by_impact[d.get("impact", "unknown")] = debt_by_impact.get(d.get("impact", "unknown"), 0) + 1

    # KPI on-track from the latest snapshot
    snaps = history.get("snapshots", [])
    latest = snaps[-1] if snaps else None
    kpi_on_track = kpi_off_track = kpi_unknown = 0
    if latest:
        for v in latest.get("values", []):
            ot = v.get("on_track")
            if ot is True:
                kpi_on_track += 1
            elif ot is False:
                kpi_off_track += 1
            else:
                kpi_unknown += 1

    # Roadmap item status counts
    item_status = {}
    for ph in roadmap.get("phases", []):
        for it in ph.get("items", []):
            item_status[it.get("status", "unknown")] = item_status.get(it.get("status", "unknown"), 0) + 1

    checklists = status.get("checklists", {})
    return {
        "health": status.get("health"),
        "phase": status.get("phase"),
        "current_focus": status.get("current_focus"),
        "current_release": status.get("current_release"),
        "release_gate_open": status.get("release_gate_open"),
        "blockers_count": len(status.get("blockers", [])),
        "checklists": {k: v.get("state") for k, v in checklists.items()},
        "counts": {
            "decisions": len(decisions.get("decisions", [])),
            "kpis": len(kpis.get("kpis", [])),
            "releases": len(snaps),
            "tech_debt_total": len(debt_items),
            "tech_debt_open": len(open_debt),
            "roadmap_items": sum(len(p.get("items", [])) for p in roadmap.get("phases", [])),
            "profitability_active": len([m for m in profitability.get("mechanisms", []) if m.get("status") == "active"]),
            "memory_events": len(memory.get("timeline", [])),
        },
        "tech_debt_open_by_impact": debt_by_impact,
        "roadmap_items_by_status": item_status,
        "latest_release": (latest or {}).get("release"),
        "kpi_status": {"on_track": kpi_on_track, "off_track": kpi_off_track, "unknown": kpi_unknown},
        "primary_kpi_id": project.get("goal", {}).get("primary_kpi_id"),
    }


def build_viability(viability):
    """Crucible rollup (contract 1.1.0): enough for a portfolio to show the verdict and
    whether the follow-through (validation test) is owed — full council detail stays in state."""
    cur = viability.get("current", {}) or {}
    test = cur.get("validation_test", {}) or {}
    return {
        "id": cur.get("id"),
        "date": cur.get("date"),
        "verdict": cur.get("verdict"),
        "confidence": cur.get("confidence"),
        "one_line_call": cur.get("one_line_call"),
        "fingerprint": cur.get("fingerprint"),
        "audited_mvp_status": cur.get("audited_mvp_status"),
        "assumptions_count": len(cur.get("assumptions") or []),
        "validation_test": {
            "status": test.get("status"),
            "due": test.get("due"),
            "outcome": test.get("outcome"),
        },
        "history_count": len(viability.get("history") or []),
        # Contract 1.3.0: per-persona council scores, so a dashboard can draw the council without
        # reading state. Pre-rebuttal scores only when a rebuttal round ran.
        "scores": cur.get("scores") or {},
        "scores_pre_rebuttal": cur.get("scores_pre_rebuttal") if cur.get("rebuttal_round") else None,
        "rebuttal_round": bool(cur.get("rebuttal_round")),
    }


def build_marketing(slug, marketing):
    """Marketing plan (contract 1.3.0) from the OPTIONAL `.ai/state/marketing.json` (Rule 08).
    None when the project records no plan. external_refs pass through untouched: they are opaque
    pointers to plans kept elsewhere, never resolved here."""
    if not marketing:
        return None
    plan = marketing.get("plan", {}) or {}
    initiatives = [{**it, "uid": ns(slug, it["id"])} for it in marketing.get("initiatives", []) if "id" in it]
    actions = sorted(marketing.get("next_actions", []) or [], key=lambda a: (a.get("due") is None, a.get("due") or ""))
    return {
        "status": plan.get("status"),
        "stage": plan.get("stage"),
        "summary": plan.get("summary"),
        "plan_doc": plan.get("plan_doc"),
        "external_refs": plan.get("external_refs", []),
        "initiatives": initiatives,
        "active_initiatives": len([i for i in initiatives if i.get("status") == "active"]),
        "next_actions": actions,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("PRAXIS_ROOT", "."))
    ap.add_argument("--out", default="praxis-export.json")
    ap.add_argument("--stdout", action="store_true", help="Write to stdout instead of a file.")
    ap.add_argument("--pretty", action="store_true", help="Indent the JSON (default: compact).")
    args = ap.parse_args()

    root = find_root(args.root) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state = os.path.join(root, ".ai", "state")
    if not os.path.isdir(state):
        print(f"{RED}✗ No .ai/state under {root}{RESET}", file=sys.stderr)
        return 1

    project = load(state, "project.json", {})
    decisions = load(state, "decisions.json", {})
    roadmap = load(state, "roadmap.json", {})
    kpis = load(state, "kpis.json", {})
    history = load(state, "kpi-history.json", {})
    debt = load(state, "tech-debt.json", {})
    skills = load(state, "skills-ledger.json", {})
    memory = load(state, "memory.json", {})
    profitability = load(state, "profitability.json", {})
    status = load(state, "status.json", {})
    viability = load(state, "viability.json", {})
    marketing = load(state, "marketing.json", None)  # optional (Rule 08)

    ident = project.get("identity", {})
    slug = ident.get("slug") or "unknown-project"

    # Namespace collections by slug (adds uid; leaves original fields intact).
    def stamp(items):
        out = []
        for it in items or []:
            if isinstance(it, dict) and "id" in it:
                out.append({**it, "uid": ns(slug, it["id"])})
            else:
                out.append(it)
        return out

    export = {
        "export_contract_version": EXPORT_CONTRACT_VERSION,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "project": {
            "slug": slug,
            # Contract 1.2.0: the Praxis baseline repo itself has no product to measure — consumers
            # (dashboards, portfolios) should render its KPI/verdict rollups as n/a, not as unknowns.
            "template": os.path.exists(os.path.join(root, ".praxis-template")),
            "name": ident.get("name"),
            "codename": ident.get("codename"),
            "type": ident.get("type"),
            "owner": ident.get("owner"),
            "ecosystem": ident.get("ecosystem"),
            "repository": ident.get("repository"),
            "production_url": ident.get("production_url"),
            "schema_version": project.get("meta", {}).get("schema_version"),
            "one_sentence_goal": project.get("goal", {}).get("one_sentence"),
            "active_packs": project.get("active_packs", []),
            "stack": project.get("stack", {}),
            "mvp_status": project.get("mvp", {}).get("status"),
            "horizons": project.get("horizons", {}),
        },
        "summary": build_summary(project, status, kpis, history, debt, roadmap, profitability, decisions, memory),
        "viability": build_viability(viability),
        "marketing": build_marketing(slug, marketing),
        "decisions": stamp(decisions.get("decisions", [])),
        "kpis": stamp(kpis.get("kpis", [])),
        "kpi_history": history.get("snapshots", []),  # already keyed by release; values carry kpi_id
        "tech_debt": stamp(debt.get("items", [])),
        "roadmap": {
            "vision": roadmap.get("vision"),
            "phases": [
                {**ph, "uid": ns(slug, ph.get("id", "")),
                 "items": stamp(ph.get("items", []))}
                for ph in roadmap.get("phases", [])
            ],
        },
        "skills_ledger": stamp(skills.get("ledger", [])),
        "profitability": stamp(profitability.get("mechanisms", [])),
        "memory": {
            "summary": memory.get("summary", {}),
            "timeline": stamp(memory.get("timeline", [])),
            "learnings": stamp(memory.get("learnings", [])),
        },
        "status": {
            "phase": status.get("phase"),
            "health": status.get("health"),
            "current_focus": status.get("current_focus"),
            "current_release": status.get("current_release"),
            "release_gate_open": status.get("release_gate_open"),
            "blockers": status.get("blockers", []),
            "checklists": status.get("checklists", {}),
            "next_action": status.get("next_action"),
        },
        "links": build_links(slug, decisions, debt, roadmap, profitability, memory, marketing),
    }
    export["summary"]["viability_verdict"] = export["viability"].get("verdict")
    export["summary"]["marketing_status"] = (export["marketing"] or {}).get("status")

    indent = 2 if args.pretty else None
    rendered = json.dumps(export, indent=indent, ensure_ascii=False) + ("\n" if args.pretty else "")

    if args.stdout:
        sys.stdout.write(rendered)
        return 0

    out_path = args.out if os.path.isabs(args.out) else os.path.join(root, args.out)
    with open(out_path, "w") as f:
        f.write(rendered if args.pretty else rendered + "\n")
    s = export["summary"]
    print(f"{GREEN}✓ Exported {os.path.relpath(out_path, root)} "
          f"(slug={slug}, contract={EXPORT_CONTRACT_VERSION}): "
          f"{s['counts']['decisions']} decisions, {s['counts']['kpis']} KPIs, "
          f"{s['counts']['tech_debt_open']} open debt, {s['counts']['releases']} releases, "
          f"{len(export['links'])} links.{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
