# Changelog

All notable changes to Praxis are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

## [0.7.0] — 2026-09-14

### Added
- **Crucible rebuttal round (Step 2b)**: a bounded, Judge-triggered rebuttal pass when the five persona
  reports genuinely conflict — single pass, never iterated — before the verdict is synthesized
  (`rules/09-crucible.md`).
- **Brand identity v1.0 (dec-007 / ADR 0007)**: the Gate mark (Π, terracotta on the right leg only),
  paper/ink/terracotta palette, Spectral + Space Grotesk + JetBrains Mono, and a classical, hype-free
  voice. Canonical guide and light/dark mark + lockup SVGs live in `assets/brand/` — deliberately
  excluded from `bootstrap.sh init` so projects built on Praxis carry their own brand, never this one.

### Changed
- **README** rebuilt to the brand system: theme-aware lockup header, etymology, badge row, brand-themed
  Mermaid palette, voice-compliant diagrams, author attribution, and branded footer.
- **Repo metadata**: description now leads with the tagline; homepage and topics set.

## [0.6.0] — 2026-09-08

### Added
- **Local-first `script` metric source**: `scripts/fetch_metrics.py` gains a `script` adapter —
  `instrumentation.fetch.command` is any shell command run from the repo root whose stdout parses as the
  KPI value (`{since}`/`{until}` templated as ISO dates). Closes the instrumentation gap for projects
  without SaaS analytics: a DB query, log grep, or `curl | jq` becomes a KPI with zero credentials.
  Same safe failure mode as every adapter (error/timeout/non-numeric → skip, carry forward).
  `kpis.json` ships a working example (`kpi-004`, commit count via `git rev-list --count HEAD`).
- **Template flag in the export contract (1.2.0)**: `praxis-export.json → project.template` is `true`
  for the Praxis baseline repo (`.praxis-template` present) so portfolio consumers can render its
  KPI/verdict rollups as n/a instead of unknowns. Additive — 1.x consumers keep working;
  `.ai/schemas/praxis-export.schema.json` extended to match. First consumer: the KineticOS portfolio.

## [0.5.0] — 2026-08-24

### Added
- **Viability in the export contract (1.1.0)**: `scripts/export_state.py` now emits a top-level
  `viability` rollup (current Crucible verdict, confidence, idea fingerprint, assumptions count,
  validation-test status/due/outcome, history count) plus `summary.viability_verdict`, closing the
  follow-on named in ADR 0006's Consequences. Additive — 1.0.x consumers keep working;
  `.ai/schemas/praxis-export.schema.json` extended to match. First consumer: the KineticOS
  portfolio (`eng/portfolio/`), which aggregates every project's export (roadmap `item-100`'s
  dashboard direction).

## [0.4.0] — 2026-08-01

### Added
- **The Crucible — idea viability gate**: Praxis now gates WHETHER the idea deserves to be built, not just
  how. `rules/09-crucible.md` runs a 5-persona adversarial council (Contrarian, Expansionist, Logician,
  Researcher, Buyer) as parallel subagents; a Judge issues **GO / RESHAPE / KILL** with an assumptions
  register, MVP adjustments, and the cheapest **48–72h validation test** of the riskiest assumption — all
  persisted to `.ai/state/viability.json` (new schema; IDs `aud-NNN`, `asm-NNN`).
- **Re-audit triggers are detected, not remembered**: `scripts/check_viability.py` fingerprints (SHA-256)
  the idea-defining sections of `PROJECT.md` (goal, non-goals, primary KPI, audience, MVP, constraints) and
  raises T1–T9 findings — never audited, idea drift, KILL without override (BLOCKED), unapplied RESHAPE,
  overdue validation test (REQUIRED); test never started, audit staleness (default 45 days pre-ship),
  primary-KPI off-track streak (default 2 snapshots), MVP phase boundary (RECOMMENDED). Template-exempt via
  `.praxis-template`.
- **Enforcement wiring**: Pre-Flight step 3 (hard stop for agents, CLAUDE.md §2/§15), pre-commit
  `--warn-only` (commits stay cheap), state-validation CI fails on REQUIRED/BLOCKED, and
  `check_release_gate.py` hard-blocks `v*` releases on unresolved verdicts or an incomplete/unwaived
  validation test. New `./bootstrap.sh crucible` command. (dec-006 / ADR 0006, mem-010)

## [0.3.1] — 2026-06-03

### Fixed
- **State Validation CI failed on the baseline itself**: `state-validation.yml` runs
  `validate_state.py --strict`, which rejects `REPLACE_*` placeholders — but the Praxis template *intentionally*
  keeps them, so CI failed on every push. `validate_state.py` now honors the `.praxis-template` marker: when
  present, strict placeholder failures downgrade to warnings (JSON/schema/duplicate-ID checks still apply).
  Real projects (no marker) remain strictly enforced. (mem-008 / learn-002)

## [0.3.0] — 2026-06-02

### Added
- **Export contract for dashboards**: `scripts/export_state.py` emits `praxis-export.json` — a stable,
  versioned projection of all project state for an admin/portfolio dashboard. Independent
  `export_contract_version`; every record namespaced `uid = "<slug>:<id>"` for portfolio-safe tables;
  precomputed `summary` rollups (open debt by impact, KPI on-track counts, gate/health, counts); and a
  flattened `links[]` relationship graph. Schema at `.ai/schemas/praxis-export.schema.json`; `bootstrap.sh
  export` command; artifact gitignored by default. The dashboard is a separate project consuming the
  contract (static read / Supabase projection / release asset). (dec-005 / ADR 0005, roadmap `item-100`)

## [0.2.1] — 2026-05-31

### Added
- **README diagrams**: five Mermaid diagrams visualizing how Praxis operates — system at a glance, project
  lifecycle, the feature inner loop, the enforcement layer, and Markdown→JSON identity authoring. They render
  natively on GitHub (no image files) and sit right after "The core idea."

## [0.2.0] — 2026-05-30

### Added
- **Architecture release gate**: `docs/architecture/overview.md` is now a required, file-based gate.
  `scripts/check_release_gate.py` blocks `v*` releases unless the architecture doc exists, has no template
  placeholders, and has real substance (≥ ~600 non-whitespace chars). The check inspects the file itself, so
  it can't be bypassed by flipping a flag. Shipped a canonical 10-section `overview.md` template (copied into
  every project by `bootstrap.sh init`); wired into CLAUDE.md Pre-Flight + release gates and `rules/01`.
  (dec-003 / ADR 0003)
- **Markdown-first project setup**: `PROJECT.md` is now the human authoring surface for project identity
  (name, goal, MVP, stack, packs). `scripts/sync_project.py` compiles it into `.ai/state/project.json` (still
  the machine source of truth). `bootstrap.sh init` copies `PROJECT.md` and runs the sync; added
  `bootstrap.sh sync`; the pre-commit hook regenerates and re-stages `project.json` so the Markdown and JSON
  never drift. `project.json` is now GENERATED — edit the Markdown, not the JSON. (dec-004 / ADR 0004)
- **Template exemption**: a `.praxis-template` marker lets the baseline repo skip the product release gate.
  `bootstrap.sh init` deliberately omits it (and `CHANGELOG.md`) so real projects always get the full gate,
  and now also copies `.gitignore` into new projects.

### Planned (tracked, not yet shipped)
- `tech-debt.json` `debt-002` — **ratio adapter for derived KPIs** (e.g. activation = numerator/denominator).
  The current fetcher returns a single scalar per source; ratio-style KPIs still need manual values or
  carry-forward. Targeted for a future release.

## [0.1.0] — 2026-05-30
Initial baseline.

### Added
- **Core operating system**: `CLAUDE.md` (master instructions, Pre-Flight Protocol, horizon model,
  release gates), `README.md`.
- **State (`.ai/state/`)**: 10 JSON source-of-truth files — project, decisions, roadmap, kpis,
  kpi-history, tech-debt, skills-ledger, memory, profitability, status — each with a JSON Schema in
  `.ai/schemas/` and append snippets in `.ai/templates/`.
- **Rules (`rules/`)**: general behavior, lifecycle, state-management, testing/security/deployment
  checklists, SEO + Core Web Vitals gate, skill-audit protocol, profitability & marketing.
- **Docs (`docs/`)**: resumable per-feature template, architecture notes, human-readable ADRs.
- **Packs (`packs/`)**: opt-in overlays — web-seo, mobile, ai-service, streaming.
- **Enforcement layer**: git hooks (`pre-commit` validate, `pre-push` gate on `v*` tags) and CI
  (`state-validation`, `lighthouse-ci`, `kpi-snapshot`).
- **Scripts (`scripts/`)**: `validate_state.py`, `check_release_gate.py`, `snapshot_kpis.py`,
  and reference metric fetcher `fetch_metrics.py` / `fetch_metrics.sh` (Amplitude, Supabase, CrUX).
- **`bootstrap.sh`**: init / validate / gate / hooks / snapshot / new-feature.

### Notes
- Decisions recorded: `dec-001` (adopt baseline), `dec-002` (enforcement layer).
- Known seam: per-KPI metric *values* require source config in `kpis.json → instrumentation.fetch`;
  unconfigured sources carry forward safely. Ratio-style KPIs may need a custom adapter (see `debt-002`).

[0.3.1]: https://github.com/itsmarcosjreyes/praxis/releases/tag/v0.3.1
[0.3.0]: https://github.com/itsmarcosjreyes/praxis/releases/tag/v0.3.0
[0.2.1]: https://github.com/itsmarcosjreyes/praxis/releases/tag/v0.2.1
[0.2.0]: https://github.com/itsmarcosjreyes/praxis/releases/tag/v0.2.0
[0.1.0]: https://github.com/itsmarcosjreyes/praxis/releases/tag/v0.1.0
