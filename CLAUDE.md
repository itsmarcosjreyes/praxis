# CLAUDE.md — Master Operating Instructions

> This file is the entry point for any AI agent working in this repository. It is auto-loaded by the
> Claude VS Code extension. Read it fully before doing anything. Then load the state files in `.ai/state/`
> and the rules in `rules/`. **Do not write code, make decisions, or start features before completing the
> Pre-Flight Protocol below.**

---

## 0. What this is

This is a **standardized project operating system**. It guarantees that every project — web, SaaS, iOS/tvOS,
Android, streaming/OTT, or AI service — is built the same disciplined way: clear goal, documented decisions,
tracked KPIs, managed technical debt, gated releases, and a built-in path to profitability and growth.

The **source of truth is the JSON in `.ai/state/`**, not your context window. Context gets compacted; the
JSON does not. When in doubt, re-read the state files. When you change reality, update the state files.

**Golden rule:** *If it isn't written to the relevant `.ai/state/*.json`, it didn't happen.*

---

## 1. The single-sentence goal

Every project must be describable in ONE sentence. It lives in `.ai/state/project.json → goal.one_sentence`.
If you cannot state the goal in one sentence, stop and resolve that with the human before any other work.

> Format: "**[Project] helps [who] achieve [outcome] by [mechanism], measured by [primary KPI].**"

---

## 2. Pre-Flight Protocol (run before EVERY feature or project start)

Execute in order. Do not skip. This is enforced — see `rules/01-workflow.md`.

1. **Load state.** Read all files in `.ai/state/`. Reconstruct the project from JSON, not memory.
2. **Confirm the goal.** Verify the work in front of you serves `project.json → goal.one_sentence`. If it
   doesn't, surface the conflict before proceeding.
3. **Locate the horizon.** Confirm where this work sits in short/mid/long-term plans (`roadmap.json`) and
   whether it belongs in the current MVP/version scope (`project.json → mvp`).
4. **Skill & tool audit.** Run the protocol in `rules/07-skills-and-tools.md`: confirm the installed skills,
   MCP connectors, and UI references are the *best available* for this work. Check known skills, then
   `https://www.aitmpl.com/skills/`, then `https://21st.dev/home` for UI references. Add/replace/remove
   skills as warranted and log every change in `.ai/state/skills-ledger.json`.
5. **Check debt.** Read `tech-debt.json` for anything that should be paid down or automated before building
   on top of it.
6. **Decision check.** If this work involves a non-trivial choice (architecture, dependency, data model,
   vendor, pattern), it requires a decision record — see §4.
7. **Architecture doc.** Ensure `docs/architecture/overview.md` exists and reflects reality. Create it from
   the template at project start and keep it current as the design evolves — it is a hard release gate.
8. **Plan parallelism.** Decide what can be parallelized and spin off subagents (see §7).
9. **Update status.** Set `status.json → current_focus` and `phase` so any agent picking up later knows the
   live state.

---

## 3. The horizon model (short / mid / long term)

Every major decision and every roadmap item carries three horizons. This prevents local optimizations that
sabotage the platform later.

- **Short term** — this release / next 1–2 weeks. What ships now.
- **Mid term** — this quarter. What this unlocks or constrains next.
- **Long term** — the platform vision. Why this scales (or what would break at scale).

When you propose anything significant, state all three horizons. The horizon fields are required in
`decisions.json` and `roadmap.json`.

---

## 4. Decision discipline (machine-readable forever)

Every non-trivial decision is appended to `.ai/state/decisions.json` using the schema in
`.ai/schemas/decisions.schema.json`. A human-readable mirror (ADR) goes in `docs/decisions/` using
`docs/decisions/_TEMPLATE.adr.md`. The JSON is canonical; the ADR is for humans.

Log a decision when you: pick a technology/vendor, define a data model or API contract, choose an
architectural pattern, set a security/compliance posture, or make any trade-off that a future agent could
reasonably question. Each entry captures the goal link, options considered, the choice, the tradeoff, and
all three horizons. **Never silently reverse a logged decision** — supersede it with a new entry that
references the old `id`.

---

## 5. MVP / first version focus

`project.json → mvp` defines the smallest thing that delivers the one-sentence goal and is shippable.
Anything not required for the MVP goes to `roadmap.json` under a later phase — not into the MVP. Resist
scope creep ruthlessly. When tempted to add to the MVP, log it as a roadmap item instead and move on.

---

## 6. KPIs and per-release tracking

KPIs are defined in `kpis.json` (definition, target, instrumentation, owner). Every release writes a
snapshot to `kpi-history.json` so progress and regressions are visible release-over-release. **KPI
instrumentation is part of the definition of done** — a feature that should move a KPI but ships without the
tracking is incomplete. See `rules/02-state-management.md` for the snapshot procedure.

---

## 7. Parallel agents — you are encouraged to scale out

You may and should spin off subagents to run independent work concurrently (research, multi-file scaffolding,
test generation, audits, competitive/SEO research). Prefer one message with multiple agent calls for
independent tasks. Use a verification subagent for high-stakes work. Keep one writer per file to avoid
conflicts. Treat subagents as your execution multiplier, not a last resort.

---

## 8. Profitability & growth are first-class

No project is "just" technical. Before MVP and at every phase boundary, confirm `profitability.json` has at
least one active mechanism (email capture, cross-marketing to social, cross-sell into another project, paid
tier, affiliate, etc.) and that `marketing-plan` items tie to KPIs. A web-accessible surface without an
email capture or growth loop is not done. See `rules/08-profitability-marketing.md`.

---

## 9. Web standards: SEO & page speed are non-negotiable

For any web-accessible surface, SEO and Core Web Vitals are release gates, not nice-to-haves. See
`rules/06-seo-pagespeed.md` and the `packs/web-seo/` overlay. Failing CWV or missing SEO fundamentals blocks
release.

---

## 10. Release gates (hard stops)

A change is NOT "done" until ALL of these pass and the relevant JSON is updated:

- [ ] Architecture described in `docs/architecture/overview.md` (no placeholders, real substance) — gate-enforced
- [ ] Testing checklist passed (`rules/03-testing-checklist.md`) → `status.json → checklists.testing`
- [ ] Security checklist passed (`rules/04-security-checklist.md`) → `status.json → checklists.security`
- [ ] Deployment checklist passed (`rules/05-deployment-checklist.md`) → `status.json → checklists.deployment`
- [ ] (Web) SEO + page-speed gate passed (`rules/06-seo-pagespeed.md`)
- [ ] KPI snapshot written to `kpi-history.json`
- [ ] `decisions.json` updated for any decisions made
- [ ] `tech-debt.json` updated for any debt incurred or paid
- [ ] `memory.json` evolution entry appended
- [ ] Feature doc in `docs/features/` created/updated
- [ ] `status.json` reflects the new reality

Do not report a task complete while any box is unchecked. If you must defer one, log it explicitly in
`tech-debt.json` and say so.

---

## 11. Stack defaults (override per project)

These are the **default** tools. They are not mandatory — override per project and log the override as a
decision. Defaults exist to reduce startup friction, not to dictate.

| Concern | Default |
|---|---|
| Web hosting / frontend | Vercel |
| Backend / DB / auth | Supabase |
| Heavy compute / GPU / jobs | Modal |
| Workflow automation / orchestration | n8n |
| LLM routing | OpenRouter |
| Cloud primitives | AWS |
| CI/CD | GitHub Actions |
| Mobile CI signing | Fastlane + Match |
| Vector memory | Supabase pgvector / HNSW |
| Analytics | Segment + product analytics (Amplitude) |

When a project's needs diverge, choose the better tool and record why in `decisions.json`.

---

## 12. File map

```
CLAUDE.md                     ← you are here (master instructions)
PROJECT.md                    ← human authoring surface for project identity → generates project.json
.ai/
  state/                      ← SOURCE OF TRUTH (JSON, survives context compaction)
    project.json              ← identity, one-sentence goal, MVP, horizons (GENERATED from PROJECT.md)
    decisions.json            ← machine-readable decision log
    roadmap.json              ← growth plan by phase + horizons
    kpis.json                 ← KPI definitions + targets
    kpi-history.json          ← per-release KPI snapshots
    tech-debt.json            ← debt + manual-work-to-automate backlog
    skills-ledger.json        ← skills/tools added, removed, evaluated
    memory.json               ← evolution log (onboard any agent fast)
    profitability.json        ← monetization + growth loops
    status.json               ← live status, checklist states, current focus
  schemas/                    ← JSON Schemas that validate every state file
  templates/                  ← blank entry templates
rules/                        ← the operating rules (read all)
docs/
  features/                   ← one .md per feature (AI can resume any feature)
  architecture/               ← system architecture notes
  decisions/                  ← human-readable ADRs (mirror of decisions.json)
packs/                        ← opt-in overlays: web-seo, mobile, ai-service, streaming
scripts/                      ← enforcement & automation (validate_state, check_release_gate, snapshot_kpis, export_state)
.githooks/                    ← pre-commit (validate state), pre-push (gate on v* tags)
.github/workflows/            ← CI: state-validation, lighthouse-ci, kpi-snapshot
lighthouserc.json             ← Core Web Vitals assertions (mirrors rules/06)
bootstrap.sh                  ← copy this baseline into any new repo + install hooks
```

> **Project identity is authored in `PROJECT.md`, not `project.json`.** `PROJECT.md` is the Markdown a human
> edits (or drops in); `scripts/sync_project.py` compiles it into `.ai/state/project.json` (the machine
> source of truth everything else reads). Run `./bootstrap.sh sync` after editing, or just commit — the
> pre-commit hook regenerates and re-stages `project.json` automatically. Never hand-edit `project.json`.

---

## 14. Enforcement (the gates are machine-enforced, not just instructions)

State integrity and the release gates are enforced by tooling, so they cannot silently drift:

- **pre-commit hook** regenerates `project.json` from `PROJECT.md` (via `scripts/sync_project.py`) and
  re-stages it, then runs `scripts/validate_state.py` — invalid JSON, schema violations, or duplicate IDs
  block the commit.
- **pre-push hook** runs `scripts/check_release_gate.py` when pushing a `v*` tag — a release is blocked
  unless `docs/architecture/overview.md` is filled in (file-based check), testing/security/deployment (and
  SEO for web) checklists are `passed`, and `release_gate_open: true`.
- **CI** mirrors this on every push/PR (`state-validation.yml`), enforces Core Web Vitals on web projects
  (`lighthouse-ci.yml`), and on a `v*` tag automatically writes the KPI snapshot, appends a `memory.json`
  entry, resets `status.json`, and commits it back (`kpi-snapshot.yml`).

Activate hooks in a project with `./bootstrap.sh hooks .` (init does this automatically). Override a single
run with `--no-verify` only in emergencies. See `scripts/README.md` for the full map and the per-project
metric-fetch seam (`metrics.json`).

---

## 13. Operating principles (how to think here)

- Optimize for **leverage and throughput**, not cleverness. Prefer maintainable-pragmatic over academically perfect.
- For every recommendation, answer: *why does this scale? what's the operational burden? what breaks at scale? what's the hidden tradeoff?*
- Challenge weak assumptions. Do not blindly agree. Intellectual friction is wanted.
- Automate anything done manually more than twice; log the manual step in `tech-debt.json` until automated.
- Deterministic, observable systems. If it can't be measured or logged, it can't be operated.
- Keep state current as you go — small, frequent JSON updates beat one big update at the end.
