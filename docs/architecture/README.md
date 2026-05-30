# docs/architecture/

System architecture documentation. Keep this current enough that a new agent can understand how the system
fits together without reading all the code.

## Suggested contents
- **overview.md** — context diagram, major components, data flow, external dependencies.
- **data-model.md** — entities, relationships, ownership, retention.
- **api.md** — contracts, auth model, versioning, error conventions.
- **infra.md** — environments, deploy topology (Vercel/Supabase/Modal/AWS), CI/CD pipeline, observability.
- **runbooks** — operational procedures (or use the `operations:runbook` skill).

## Practices
- Prefer diagrams (Mermaid) plus short prose over walls of text.
- Significant architectural choices get a decision entry (`decisions.json`) + ADR (`docs/decisions/`).
- Use `engineering:system-design` and `engineering:architecture` skills to draft and evaluate.
- Note what breaks at scale and the intended evolution path (ties to `roadmap.json` long-term horizon).
