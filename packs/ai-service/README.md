# Pack: ai-service

Opt in by adding `"ai-service"` to `project.json → active_packs`. For LLM/agent/RAG/vector-memory services.
Default stack: OpenRouter (routing), Supabase pgvector/HNSW (memory), Modal (heavy/GPU jobs), n8n (orchestration).

## What this pack adds
- An **eval gate**: quality/accuracy/latency/cost thresholds must pass before release (part of testing gate).
- Prompt-injection / jailbreak red-teaming becomes part of the security gate.
- Cost-per-request and quality scores become tracked KPIs.

## Architecture defaults
- Route through OpenRouter with a primary + fallback model; budget caps per request.
- Retrieval: canonicalize at ingestion; chunk + embed; HNSW index; cite sources.
- Determinism/observability: log prompts (PII-scrubbed), tokens, latency, cost, model, eval scores.
- Orchestration via n8n / workflow chains; idempotent steps; retries with backoff.

## Setup checklist
- [ ] Eval set defined with thresholds (accuracy/quality/latency/cost); runs in CI.
- [ ] Fallback model path + timeout/retry policy tested.
- [ ] Per-user + global spend caps enforced; alerting on overspend.
- [ ] Prompt-injection mitigations; untrusted content isolated from tool/agent authority.
- [ ] Output filtering for sensitive-data leakage; secrets unreachable by the model.
- [ ] Vector store: ingestion canonicalization, dedup, re-index strategy, freshness.
- [ ] Full observability: traces, token/cost logs, eval dashboards.

## KPIs to add
- Eval pass rate / quality score, p95 latency, cost per request, cache hit rate, hallucination/error rate.

## Recommended skills
`engineering:system-design`, `engineering:architecture`, `engineering:testing-strategy`, `skill-creator`.
