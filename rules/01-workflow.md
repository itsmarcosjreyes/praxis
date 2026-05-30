# Rule 01 — Lifecycle & Order of Operations

The canonical flow for any unit of work. Enforced by CLAUDE.md §2 (Pre-Flight) and §10 (Release Gates).

## A. Pre-Flight (before starting anything)
1. Read all `.ai/state/*.json`. Reconstruct the project from JSON.
2. Confirm the work serves `project.json → goal.one_sentence`. If not, stop and surface it.
3. Place the work on a horizon (`roadmap.json`) and confirm MVP scope (`project.json → mvp`).
4. Run the **Skill & Tool Audit** (`rules/07-skills-and-tools.md`). Update `skills-ledger.json`.
5. Read `tech-debt.json`; pay down or note blocking debt.
6. Identify decisions to be made → prepare to log them (`rules/02-state-management.md`).
7. Plan parallelism; spin off subagents for independent tracks.
8. Set `status.json → current_focus`, `phase`, `next_action`.

## B. Build
1. Create/update the feature doc in `docs/features/` BEFORE coding (so any agent can resume).
2. Log decisions as you make them (`decisions.json` + ADR mirror).
3. Implement, keeping KPI instrumentation in scope (a feature that should move a KPI ships with its tracking).
4. Record incurred debt immediately in `tech-debt.json`.
5. Keep `status.json` current.

## C. Verify (release gate — hard stop)
Run all applicable checklists and update `status.json → checklists.*`:
- Testing (`rules/03`), Security (`rules/04`), Deployment (`rules/05`)
- If web-accessible: SEO + Page Speed (`rules/06`)

## D. Release
1. Write a KPI snapshot to `kpi-history.json` (compute deltas vs previous release).
2. Append an evolution entry to `memory.json`.
3. Confirm `profitability.json` has at least one active mechanism (esp. before MVP ship).
4. Set `status.json → release_gate_open` only when every gate passed; then tag/release.
5. Update `roadmap.json` item statuses.

## E. Close out
- Final reconciliation of all state files.
- Report: what shipped, decisions made, debt incurred, KPI deltas, next action.

> Do not report "done" while any gate box is unchecked. Defer only with an explicit `tech-debt.json` entry.
