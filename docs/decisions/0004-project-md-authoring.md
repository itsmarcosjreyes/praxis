# ADR 0004: Author project identity in PROJECT.md; generate project.json from it

- **Decision ID:** dec-004
- **Status:** accepted
- **Date:** REPLACE_ISO_DATE
- **Author:** marcos@kineticmatrix.io
- **Category:** process
- **Supersedes / Superseded by:** — / —

## Context
Setting up a project required hand-editing `.ai/state/project.json` — unfriendly and error-prone. But
`project.json` can't simply be replaced by Markdown: its schema is validated on every commit, `lighthouse-ci`
greps it for active packs, and agents reconstruct the project from it after context compaction.

## Options considered
1. **Replace `project.json` with `PROJECT.md` entirely** — pros: one human file; cons: breaks schema
   validation, CI grep, and machine reconstruction.
2. **Author in `PROJECT.md`, generate `project.json`** — pros: friendly Markdown authoring while keeping the
   machine source of truth and all enforcement; pre-commit regen prevents drift; cons: needs a parser.

## Decision
Add `PROJECT.md` (repo root) as the human authoring surface, and `scripts/sync_project.py` to compile it
into `.ai/state/project.json`. `bootstrap.sh init` copies `PROJECT.md` and runs the sync; `bootstrap.sh sync`
regenerates on demand; the pre-commit hook regenerates and re-stages `project.json` on every commit so the
Markdown and JSON never drift. `project.json` is now GENERATED and must not be hand-edited.

## Tradeoff
Introduces a Markdown→JSON parser with a fixed heading contract (a small maintenance surface) in exchange for
much friendlier authoring without losing any machine validation. The parser preserves scalar `REPLACE_`
placeholders so `validate_state.py --strict` still flags an unfilled project, and drops template filler
(`...`) from generated lists.

## Horizons
- **Short term:** projects are configured by editing Markdown, not JSON.
- **Mid term:** lower onboarding friction; fewer malformed `project.json` files.
- **Long term:** the authoring surface can grow richer without touching the machine contract.

## Consequences
`PROJECT.md` ships with the baseline and is copied into every project by `bootstrap.sh init`. On the baseline
template repo (`.praxis-template` present), sync keeps `meta` dates as `REPLACE_ISO_DATE` to preserve the
template convention; real projects get today's date. `sync_project.py --check` provides drift detection for
CI if desired.
