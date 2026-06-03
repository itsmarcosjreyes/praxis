# ADR 0005: Add a stable, versioned export contract (praxis-export.json) for dashboards

- **Decision ID:** dec-005
- **Status:** accepted
- **Date:** REPLACE_ISO_DATE
- **Author:** marcos@kineticmatrix.io
- **Category:** architecture
- **Supersedes / Superseded by:** — / —

## Context
Per-project state is already normalized, typed JSON — ideal for a dashboard — but it lives per-repo, uses
project-local IDs (`dec-001` exists in every project), and its internal layout evolves with the Praxis
schema. A dashboard reading those internals directly would collide on shared IDs across projects and break
whenever an internal schema changes.

## Options considered
1. **Dashboard reads `.ai/state/*.json` directly** — pros: no new code; cons: couples the UI to internal
   schema, ID collisions across projects, breaks on every schema evolution.
2. **Stable, versioned export contract** — pros: decouples consumers, `uid` namespacing, precomputed rollups
   and a relationship graph, internal schema can evolve freely; cons: one more generated artifact + schema.

## Decision
Add `scripts/export_state.py`, which emits `praxis-export.json`:
- **`export_contract_version`** independent of project `schema_version` (additive changes only; consumers
  ignore unknown fields).
- **Portfolio-safe identity**: every record carries `uid = "<slug>:<id>"`.
- **Precomputed `summary`**: open debt by impact, KPI on-track counts, latest release, gate/health, counts.
- **`links[]` relationship graph**: flattens existing cross-references (memory→decision, debt→decision,
  roadmap→kpi/profitability, profitability→kpi, decision supersede chains) into `{from, rel, to}` edges.

Schema at `.ai/schemas/praxis-export.schema.json`; `./bootstrap.sh export` command; artifact gitignored by
default (derived, like `metrics.json`). The dashboard is a **separate project** consuming this contract —
static read from git, a Supabase projection upserted on release, or a published release asset.

## Tradeoff
One generated artifact and a contract schema to maintain, in exchange for a dashboard layer that never
breaks when internal state schemas evolve, and that scales across the whole portfolio.

## Horizons
- **Short term:** `bootstrap.sh export` produces a dashboard-ready file per project.
- **Mid term:** a Supabase projection enables cross-project portfolio queries and regression alerts (n8n).
- **Long term:** portfolio-wide operational intelligence without coupling to Praxis internals.

## Consequences
The dashboard build itself is tracked as roadmap `item-100` (phase-1) and is out of scope for the baseline
repo. When the export contract changes shape, bump `export_contract_version` and note it in the CHANGELOG so
consumers can adapt.
