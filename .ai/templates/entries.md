# Append-ready entry snippets

Copy these when adding items to the state files. Replace IDs (use `meta.next_id`, then bump it) and dates
(ISO 8601). Validate after editing (`./bootstrap.sh validate .`).

## decisions.json → decisions[]
```json
{
  "id": "dec-00X", "title": "", "status": "accepted", "date": "YYYY-MM-DD",
  "author": "marcos@kineticmatrix.io", "category": "architecture", "goal_link": "",
  "context": "", "options_considered": [{ "option": "", "pros": [], "cons": [] }],
  "decision": "", "tradeoff": "",
  "horizons": { "short_term": "", "mid_term": "", "long_term": "" },
  "reversible": true, "supersedes": null, "superseded_by": null, "adr_doc": "docs/decisions/000X-slug.md"
}
```

## roadmap.json → phases[].items[]
```json
{ "id": "item-00X", "title": "", "feature_doc": "docs/features/slug.feature.md", "priority": "P1",
  "status": "todo", "estimate": "", "depends_on": [], "unlocks": [], "profitability_link": null }
```

## kpis.json → kpis[]
```json
{ "id": "kpi-00X", "name": "", "category": "product", "definition": "", "formula": "", "unit": "",
  "target": 0, "direction": "higher-is-better",
  "instrumentation": { "source": "amplitude", "event": "", "implemented": false, "fetch": { "metric": "uniques" } },
  "owner": "marcos@kineticmatrix.io", "review_cadence": "per-release", "is_primary": false }
```
`instrumentation.source` drives `scripts/fetch_metrics.py`. Supported: `amplitude`, `amplitude-eu`,
`supabase`, `crux`. The optional `fetch` block carries source-specific query config:
- **amplitude:** `{ "metric": "uniques" | "totals" }` (uses `event`).
- **supabase:** `{ "table": "subscribers", "filter": "created_at=gte.{since}" }` (PostgREST; `{since}`/`{until}` templated).
- **crux:** `{ "url": "https://your-origin/", "form_factor": "PHONE", "percentile_metric": "largest_contentful_paint" }` (returns field p75).
Any KPI whose source is unset/unsupported is skipped and carried forward at snapshot time.

## kpi-history.json → snapshots[]
```json
{ "release": "vX.Y.Z", "date": "YYYY-MM-DD", "git_ref": "",
  "values": [{ "kpi_id": "kpi-001", "value": 0, "delta_vs_prev": 0, "target": 0, "on_track": true }],
  "notes": "" }
```

## tech-debt.json → items[]
```json
{ "id": "debt-00X", "title": "", "type": "automation-opportunity", "category": "", "description": "",
  "manual_today": true, "automatable": true, "proposed_automation": "", "impact": "medium", "effort": "low",
  "interest_rate": "", "introduced": "YYYY-MM-DD", "introduced_by_decision": null, "blocks": [],
  "status": "open", "owner": "marcos@kineticmatrix.io" }
```

## skills-ledger.json → ledger[]
```json
{ "id": "skl-00X", "action": "added", "name": "", "kind": "skill", "source": "aitmpl.com",
  "date": "YYYY-MM-DD", "reason": "", "replaced": null, "replaced_by": null, "decision_link": null }
```

## memory.json → timeline[]
```json
{ "id": "mem-00X", "date": "YYYY-MM-DD", "type": "release", "title": "",
  "detail": "", "links": { "decision": null, "release": null, "feature_doc": null } }
```

## profitability.json → mechanisms[]
```json
{ "id": "prof-00X", "type": "email-capture", "description": "", "status": "planned",
  "kpi_link": null, "tooling": "", "owner": "marcos@kineticmatrix.io", "estimated_value": "" }
```
