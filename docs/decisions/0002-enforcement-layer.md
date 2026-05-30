# ADR 0002: Enforce state integrity & release gates with git hooks + CI; automate KPI snapshots

- **Decision ID:** dec-002
- **Status:** accepted
- **Date:** REPLACE_ISO_DATE
- **Author:** marcos@kineticmatrix.io
- **Category:** process
- **Supersedes / Superseded by:** — / —

## Context
The baseline made the JSON in `.ai/state/` the source of truth, but updating it and passing the release
gates was enforced only by instruction in `CLAUDE.md`. Instruction-only discipline is non-deterministic and
drifts — especially under context compaction. To hold the model honest, integrity and gates must be
machine-enforced.

## Options considered
1. **Instruction-only** — pros: zero setup; cons: non-deterministic, drifts, relies on memory.
2. **Git hooks + CI + automated snapshots** — pros: deterministic, drift blocked at commit/merge/release,
   bookkeeping automated; cons: adds a git + python dependency and minor CI time.

## Decision
Add an enforcement layer:
- **`scripts/`** — `validate_state.py` (schema + unique-ID + placeholder checks), `check_release_gate.py`
  (gate from `status.json`), `snapshot_kpis.py` (per-release snapshot + memory entry + status reset).
- **`.githooks/`** — `pre-commit` runs validation on every commit; `pre-push` enforces the release gate only
  when pushing a `v*` tag (WIP pushes are unaffected). Activated via `core.hooksPath`.
- **`.github/workflows/`** — `state-validation.yml` (every push/PR), `lighthouse-ci.yml` (CWV+SEO gate,
  self-skips unless the `web-seo` pack is active), `kpi-snapshot.yml` (on `v*` tag: enforce gate → snapshot
  → memory → reset status → commit back).
- **`lighthouserc.json`** — CWV assertions mirroring `rules/06`.

## Tradeoff
A python + git dependency and small CI cost, in exchange for deterministic, self-enforcing state and
zero-effort release bookkeeping.

## Horizons
- **Short term:** invalid-state commits blocked; tagged releases require passed gates.
- **Mid term:** KPI snapshot / memory / status-reset happen automatically on release.
- **Long term:** state integrity scales across the whole portfolio without depending on anyone remembering.

## Consequences
Resolves `debt-001`. One remaining per-project seam: metric *values* must be fetched by a
project-specific step that writes `metrics.json` before the snapshot (documented in `scripts/README.md`);
until then, values carry forward so releases are never blocked on metric retrieval. The template repo itself
should run `validate_state.py` without `--strict` because it intentionally keeps `REPLACE_*` placeholders.
