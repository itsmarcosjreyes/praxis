# AI Guidance Baseline

A standardized, AI-native operating system for building **any** project (web, SaaS, iOS/tvOS, Android,
streaming/OTT, AI service) with Claude — consistently, efficiently, and at scale. Drop it into any repo and
every agent that touches the project works to the same standard, even after context is compacted.

## The core idea
Your context window is volatile; **the JSON in `.ai/state/` is not**. Claude reconstructs the project from
those files every session. The rules enforce a disciplined lifecycle with hard release gates. The packs add
domain specifics only when you need them.

> Golden rule: *If it isn't written to the relevant `.ai/state/*.json`, it didn't happen.*

## What's inside
- **`CLAUDE.md`** — master instructions, auto-loaded by the Claude VS Code extension. Start here.
- **`.ai/state/`** — 10 JSON source-of-truth files: project, decisions, roadmap, kpis, kpi-history,
  tech-debt, skills-ledger, memory, profitability, status.
- **`.ai/schemas/`** — JSON Schemas validating every state file.
- **`rules/`** — 9 operating rules: general behavior, lifecycle, state management, testing / security /
  deployment / SEO checklists, skill-audit protocol, profitability & marketing.
- **`docs/`** — feature docs (resumable per feature), architecture, and human-readable ADRs.
- **`packs/`** — opt-in overlays: `web-seo`, `mobile`, `ai-service`, `streaming`.
- **`bootstrap.sh`** — install into a new repo, validate state, scaffold features.

## Quick start
```bash
# From this baseline directory:
./bootstrap.sh init /path/to/new-project "My Project"
cd /path/to/new-project
# Open in VS Code — CLAUDE.md loads automatically.
# Edit .ai/state/project.json (goal.one_sentence, mvp, type), then add packs to active_packs.
./bootstrap.sh validate .         # check JSON + schemas
```
Then tell Claude: **"Run the Pre-Flight Protocol in CLAUDE.md."**

## The non-negotiables this enforces
1. A goal stated in **one sentence**.
2. **Short / mid / long-term** horizons on every major decision.
3. A clear **MVP** definition; scope creep goes to the roadmap, not the MVP.
4. **Every decision** logged in machine-readable JSON (survives compaction).
5. A **growth roadmap** in JSON.
6. **KPIs** defined, instrumented, and **snapshotted per release** for progress tracking.
7. A **skill/tool audit** before every project and feature (incl. aitmpl.com skills and 21st.dev UI refs),
   with an add/remove/replace **ledger**.
8. A **technical-debt** register that flags manual work to automate.
9. **`docs/features/`** breakdowns so AI can resume any feature.
10. **Testing / security / deployment** (and **SEO + page-speed** for web) as **hard release gates**, with
    status written back to JSON.
11. Permission to **spin off parallel agents** for throughput.
12. A **project memory** file so any agent onboards fast.
13. A built-in **path to profitability** (email capture, cross-marketing, cross-sell) tied to KPIs.
14. A **marketing plan** that fuels growth and ties back to KPIs.

## Maintaining the baseline
Version it. When you improve a rule or schema here, new projects get it on their next `init`. Existing
projects can re-copy individual files. Treat this repo as the canonical template for the whole portfolio.

### Iterating on Praxis as you use it
Praxis is designed to improve through contact with real projects. A tight loop:

1. **Hit friction in a project** → note what the baseline didn't cover or got wrong.
2. **Fix it here**, in the canonical repo (a rule, schema, script, or pack).
3. **Bump the version** and tag it (`git tag vX.Y.Z`), so projects can pin to a known-good baseline.
4. **Propagate**: new projects pick it up via `bootstrap.sh init`; existing ones re-copy the changed files.

Keep changes disciplined — the tool that enforces discipline should be built with it:
`scripts/validate_state.py` runs on every commit, and the CHANGELOG/tags are the baseline's own KPI history.

