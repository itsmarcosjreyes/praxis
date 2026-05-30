# Rule 05 — Deployment Checklist (release gate)

On completion, set `status.json → checklists.deployment.state` and, when all gates pass, set
`status.json → release_gate_open: true`. Consider the `engineering:deploy-checklist` skill.

## Pre-deploy
- [ ] Testing + Security checklists `passed` in `status.json`.
- [ ] (Web) SEO + Page Speed gate `passed`.
- [ ] Version bumped; changelog updated; release tagged.
- [ ] DB migrations reviewed, reversible, and tested on a copy; backfill plan if needed.
- [ ] Feature flags configured; risky changes behind a flag.
- [ ] Env vars/secrets present in target environment.
- [ ] Rollback plan written: trigger conditions + exact steps.

## Deploy
- [ ] Deploy to staging; smoke test the critical path.
- [ ] Progressive rollout (canary / percentage) where supported.
- [ ] Mobile: build signed (Fastlane + Match); store metadata/screenshots ready; staged rollout set.

## Post-deploy
- [ ] Health checks green; error rate + latency within bounds (Datadog/observability).
- [ ] KPI instrumentation confirmed live in production.
- [ ] **Write KPI snapshot to `kpi-history.json`** with the release tag + git ref.
- [ ] Append release entry to `memory.json`.
- [ ] Update `roadmap.json` item statuses; update `status.json` (new `current_release`, reset checklists for next cycle).
- [ ] Profitability mechanisms verified active (`profitability.json`).
- [ ] Monitor for the rollback window; document any incident (`engineering:incident-response`).

## Automation target
Most of the post-deploy bookkeeping (KPI snapshot, memory entry, status reset) should be automated via a
GitHub Action on tag. Until it is, keep an `automation-opportunity` entry in `tech-debt.json`.
