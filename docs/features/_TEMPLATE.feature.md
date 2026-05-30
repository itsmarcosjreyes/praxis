# Feature: <NAME>

> One `.md` per feature. Written BEFORE coding and kept current. Any agent should be able to read this file
> alone and resume the feature with full context. Link IDs back to the state JSON.

## Identity
- **Feature ID:** feat-XXX
- **Roadmap item:** item-XXX (`roadmap.json`)
- **Status:** todo | in-progress | blocked | done | cut
- **Owner:** marcos@kineticmatrix.io
- **Primary KPI it moves:** kpi-XXX

## Goal (one sentence)
What this feature does and for whom, tied to the project's one-sentence goal.

## Why now (horizons)
- **Short term:** what shipping this enables this release.
- **Mid term:** what it unlocks/constrains this quarter.
- **Long term:** how it fits the platform vision.

## Scope
- **In scope:** …
- **Out of scope:** …
- **MVP cut (if applicable):** the thinnest version that delivers value.

## UX / behavior
- User flow (steps, states: empty/loading/error/success).
- Edge cases and failure handling.
- Copy/microcopy notes (use `design:ux-copy`).

## Technical design
- Architecture / components touched (link `docs/architecture/`).
- Data model / API contracts (link decisions in `decisions.json`).
- Dependencies, feature flags, migrations.
- Decisions made: dec-XXX, dec-XXX.

## Instrumentation (required if it moves a KPI)
- Events emitted, source (Segment/Amplitude/Supabase), the KPI(s) they feed.
- How to verify the event lands in production.

## Profitability hook
- Linked mechanism in `profitability.json` (prof-XXX), if any.

## Testing
- Test cases (unit/integration/E2E) and how to run them. Mirrors `rules/03`.

## Security & compliance
- Relevant items from `rules/04` (auth, RLS, PII, etc.).

## Tech debt incurred / deferred
- debt-XXX entries created for anything cut or manual.

## Open questions
- Anything needing a human decision (mirror to `status.json → open_decisions_needed`).

## Changelog
- YYYY-MM-DD — what changed and by whom (agent/human).
