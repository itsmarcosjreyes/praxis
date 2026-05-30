# Changelog

All notable changes to Praxis are recorded here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/); versions follow [SemVer](https://semver.org/).

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
  unconfigured sources carry forward safely. Ratio-style KPIs may need a custom adapter (see roadmap).

[0.1.0]: https://github.com/itsmarcosjreyes/praxis/releases/tag/v0.1.0
