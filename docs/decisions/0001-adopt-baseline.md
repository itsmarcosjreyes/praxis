# ADR 0001: Adopt the AI Guidance baseline as the project operating system

- **Decision ID:** dec-001
- **Status:** accepted
- **Date:** REPLACE_ISO_DATE
- **Author:** marcos@kineticmatrix.io
- **Category:** process
- **Supersedes / Superseded by:** — / —

## Context
Projects built ad-hoc with AI lose continuity when context is compacted and drift in quality and process.
A standardized, JSON-backed operating system keeps the goal, decisions, KPIs, debt, and growth plan durable
and machine-readable so any agent can resume work cold.

## Options considered
1. **Ad-hoc per project** — pros: fast start; cons: inconsistent, no durable memory, agents re-derive context.
2. **Standardized JSON-backed baseline** — pros: repeatable, agent-resumable, gated quality; cons: upfront setup.

## Decision
Adopt this baseline (CLAUDE.md + `.ai/state` + `rules/` + `docs/` + `packs/`) for every project.

## Tradeoff
Adds upfront structure per project in exchange for long-term consistency, resumability, and compounding leverage.

## Horizons
- **Short term:** slightly more setup at project init.
- **Mid term:** faster agent/human onboarding; fewer regressions.
- **Long term:** portfolio-wide consistency and compounding operational leverage.

## Consequences
Every project carries the state files and gates. Maintenance of the baseline itself becomes a (worthwhile)
ongoing task. Keep the baseline versioned so improvements propagate to new projects.
