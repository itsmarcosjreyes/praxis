# Rule 07 — Skill & Tool Audit Protocol

Run this **before every project start and before every new feature** (Pre-Flight step 4). The goal: always
build with the *best available* skills, MCP connectors, and UI references — and keep a permanent record of
what changed. Every run writes to `skills-ledger.json` (even when nothing changes — log `kept`/`evaluated`).

## Step 1 — Inventory what's installed
- List installed skills (global + project) and MCP connectors actually relevant to the task at hand.
- Record the current relevant set in `skills-ledger.json → active_skills` / `active_connectors`.

## Step 2 — Scan for better options
Check, in order:
1. **Known skills/connectors** you're already aware of in this environment.
2. **`https://www.aitmpl.com/skills/`** — scan for skills that better fit the upcoming work.
3. **`https://21st.dev/home`** — for any UI/component work, pull UI references/patterns from here and record the source in `skills-ledger.json → ui_reference_sources`.

## Step 3 — Decide and act
For each candidate, judge fit against the task: capability match, maintenance, overlap with existing tools, operational burden.
- **Add** a skill/connector if it clearly beats what's installed → log `action: added`.
- **Replace** an inferior skill with a newer/better one → log `action: replaced` with `replaced` + `replaced_by`.
- **Remove** a skill that's outdated, redundant, or weaker than an alternative → log `action: removed` with reason.
- **Keep** when current tooling is still best → log `action: kept`.
If a change is material (affects architecture or workflow), also log a `decisions.json` entry and link it via `decision_link`.

## Step 4 — Record
Append one ledger entry per skill/connector/UI-ref touched. Update `active_*` arrays. Set `meta.last_updated`.

## Guardrails
- Don't churn: only replace when the gain is real. Note the rationale.
- Prefer fewer, sharper tools over many overlapping ones (lower operational burden).
- Don't remove a skill another active workflow depends on without checking usage.
- Treat UI references as inspiration to adapt to the project's design system — not drop-in dependencies.

## Default tool posture
Stack defaults live in `project.json → stack` (Vercel, Supabase, Modal, n8n, OpenRouter, AWS, GitHub Actions).
Diverge when a project needs it and log the override as a decision.
