# ADR 0006: Gate the idea itself — the Crucible viability audit

> Human-readable mirror of a `decisions.json` entry. The JSON (`dec-006`) is canonical; this is for reading.

- **Decision ID:** dec-006
- **Status:** accepted
- **Date:** 2026-08-01
- **Author:** marcos@kineticmatrix.io
- **Category:** process
- **Supersedes / Superseded by:** — / —

## Context
Praxis machine-enforces HOW a project is built — state integrity, architecture docs, checklists, KPI
snapshots, release gates. Nothing challenged WHETHER the thing in `PROJECT.md` deserved to be built. An idea
typed into the goal section flowed straight into MVP scoping and build work with zero adversarial
validation, and nothing detected when reality (off-track KPIs, a pivot, a changed constraint) invalidated an
earlier judgment. The most expensive failure mode Praxis could produce was a perfectly disciplined build of
the wrong thing.

## Options considered
1. **Personal Claude skill, invoked manually (`/roast` style)** — zero repo footprint and reusable outside
   Praxis, but unenforceable (depends on the human remembering), the verdict lives in chat and dies with
   context compaction, there is no re-audit detection, and it doesn't travel with the repo to other agents.
2. **Advisory rule file only** — simple, but contradicts the core Praxis lesson: every other discipline here
   is machine-enforced precisely because instructions alone drift.
3. **Repo-native protocol + durable state + fingerprint-based trigger engine wired into hooks/CI/gates** —
   more moving parts and a token/time cost on every material idea change, but the audit *always* runs, the
   verdict is durable machine-readable state, and the need to re-audit is *detected* rather than remembered.

## Decision
Option 3. `rules/09-crucible.md` defines the protocol: a brief assembled from existing state, a 5-persona
adversarial council (Contrarian, Expansionist, Logician, Researcher, Buyer) run as parallel subagents, and a
Judge issuing **GO / RESHAPE / KILL** plus an assumptions register, MVP adjustments, and the cheapest
**48–72h validation test** of the riskiest assumption. Results persist in `.ai/state/viability.json`
(schema-validated). `scripts/check_viability.py` is the trigger engine: it fingerprints (SHA-256) the
idea-defining sections of `PROJECT.md` (goal, non-goals, primary KPI, audience, MVP, constraints) and raises
findings for the T1–T9 triggers — never-audited, idea drift, unresolved KILL/RESHAPE, overdue tests,
staleness, KPI off-track streaks, phase boundaries.

Enforcement tiers: Pre-Flight step 3 (hard stop for agents), pre-commit `--warn-only` (commits stay cheap),
state-validation CI (fails on REQUIRED/BLOCKED), and `check_release_gate.py` (hard block, including
validation test completed/waived, for `v*` tags).

## Tradeoff
A full council run on every material idea edit adds latency and cost at exactly the moment the builder wants
to move fast. Accepted: a wrong idea is the most expensive artifact Praxis can produce, and the 48–72h test
exists specifically to make being wrong cheap. Warn-only commits mean a solo human can locally stack commits
on an unaudited idea — CI and the release gate backstop that window.

## Horizons
- **Short term:** every new or changed idea gets an adversarial verdict and a runnable 48–72h test before
  build work starts.
- **Mid term:** assumption registers plus KPI-linked triggers catch drifting ideas mid-build instead of at
  the post-mortem; verdict history becomes reviewable via the export contract.
- **Long term:** the Crucible is the intake valve for the whole kinetic-matrix portfolio — no project enters
  the ecosystem without a machine-recorded viability verdict, and `viability.json` feeds the dashboard like
  every other state file.

## Consequences
`viability.json` joins the state files (ID conventions `aud-NNN`, `asm-NNN`); `bootstrap.sh crucible` added;
pre-commit/CI/release-gate updated; Pre-Flight renumbered (viability check is step 3). Follow-on: surface
`viability` in `export_state.py`'s contract in a future export_contract_version bump.
