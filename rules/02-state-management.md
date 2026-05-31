# Rule 02 — State Management (when & how to write each JSON)

The state files are the project's long-term memory. This rule defines exactly when to touch each one. All
files validate against their schema in `.ai/schemas/`. Always set `meta.last_updated` (ISO 8601) and bump
`meta.next_id` when you add an item.

| File | Write WHEN | Key discipline |
|---|---|---|
| `PROJECT.md` → `project.json` | Identity, goal, MVP scope, stack, or horizons change | **Edit `PROJECT.md` (Markdown), then `./bootstrap.sh sync` — never hand-edit `project.json`, it's generated.** Goal must stay one sentence; log stack overrides as decisions |
| `decisions.json` | Any non-trivial choice is made or reversed | Append-only; supersede, never edit history; mirror to `docs/decisions/` |
| `roadmap.json` | Scope changes; items move status; phases planned | Every item has a horizon + priority; MVP-only in phase-0 |
| `kpis.json` | A KPI is defined/changed/retired | Instrumentation + owner required |
| `kpi-history.json` | Every release | Append one snapshot; compute `delta_vs_prev` and `on_track` |
| `tech-debt.json` | Debt incurred or paid; manual step found | Flag `automatable` + `proposed_automation` |
| `skills-ledger.json` | Skill/connector/UI-ref added, removed, replaced, evaluated | Log on every pre-flight audit, even "kept" |
| `memory.json` | Milestones, pivots, releases, incidents, learnings | Keep `summary` current; this is the onboarding file |
| `profitability.json` | A monetization/growth mechanism changes status | ≥1 active mechanism before MVP ship |
| `status.json` | Start AND end of every work session; gate state changes | The live truth; agents read this first for "where are we" |

## ID conventions
`dec-NNN`, `item-NNN`, `kpi-NNN`, `debt-NNN`, `skl-NNN`, `mem-NNN`, `prof-NNN`. Zero-padded, monotonic, never reused.

## KPI snapshot procedure (per release)
1. For each KPI in `kpis.json`, read current value from its instrumentation source.
2. Append a snapshot object to `kpi-history.json → snapshots` with `release`, `date`, `git_ref`.
3. For each value compute `delta_vs_prev` (vs last snapshot) and `on_track` (vs `target` + `direction`).
4. Note regressions in `memory.json` and, if actionable, `tech-debt.json`.

## Integrity rules
- Replace literal `REPLACE_*` placeholders on project init. For identity fields, edit `PROJECT.md` and run
  `./bootstrap.sh sync` — do not edit `project.json` directly (it is regenerated and your edits are lost).
- Never delete decision or memory history — supersede instead.
- After any batch of edits, validate JSON (see `bootstrap.sh validate` / the verify step).
- Prefer minimal diffs; one logical change per write where practical.
