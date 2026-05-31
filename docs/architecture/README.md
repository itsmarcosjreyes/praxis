# docs/architecture/

System architecture documentation. Keep this current enough that a new agent can understand how the system
fits together without reading all the code.

## `overview.md` is REQUIRED and gate-enforced
Every project **must** maintain `overview.md` — it fully describes the system's architecture. The release
gate (`scripts/check_release_gate.py`) blocks any `v*` release until `overview.md` exists, has no template
placeholders (`REPLACE_`/`<FILL…>`/`<...>`), and has real substance (≥ ~600 non-whitespace chars). The check
is file-based on purpose: a self-reported flag could be set true while the doc stays empty; the document
itself can't be faked. Start from the committed template and fill it in.

## Contents
- **overview.md** — *(required)* context diagram, components, data model, APIs, external deps, infra,
  security posture, scaling/failure modes, key decisions. The single source of architectural truth.
- **data-model.md** — *(optional, for deeper detail)* entities, relationships, ownership, retention.
- **api.md** — *(optional)* contracts, auth model, versioning, error conventions.
- **infra.md** — *(optional)* environments, deploy topology (Vercel/Supabase/Modal/AWS), CI/CD, observability.
- **runbooks** — operational procedures (or use the `operations:runbook` skill).

## Practices
- Prefer diagrams (Mermaid) plus short prose over walls of text.
- Significant architectural choices get a decision entry (`decisions.json`) + ADR (`docs/decisions/`).
- Use `engineering:system-design` and `engineering:architecture` skills to draft and evaluate.
- Note what breaks at scale and the intended evolution path (ties to `roadmap.json` long-term horizon).
