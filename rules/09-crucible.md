# Rule 09 — The Crucible (idea viability gate)

Praxis validates HOW you build. The Crucible validates WHETHER the thing in `PROJECT.md` deserves to be
built at all. An idea that has never been stress-tested is an unverified assumption with a roadmap attached.

**The Crucible is not optional.** It runs automatically at defined trigger points (below), its verdict is
machine-readable state (`.ai/state/viability.json`), and the release gate will not open for an MVP whose
idea was never audited. `scripts/check_viability.py` is the trigger engine — it detects when an audit is
missing, stale, or invalidated, and it is wired into pre-commit (warn), CI (fail), and the release gate
(hard block).

---

## When the Crucible runs (triggers)

Run the full council when `check_viability.py` reports **REQUIRED** or **BLOCKED**, and treat
**RECOMMENDED** as a strong prompt. The machine-detectable triggers:

| # | Trigger | Detected by | Severity |
|---|---|---|---|
| T1 | Idea authored (goal filled in) but never audited (`verdict: not-run`) | fingerprint absent | REQUIRED |
| T2 | **Idea drift** — the idea-defining sections of `PROJECT.md` (goal, non-goals, primary KPI, audience, MVP, constraints) changed since the last audit | fingerprint mismatch | REQUIRED |
| T3 | Verdict is `kill` and no override decision is logged | `kill_override.decision_link` empty | BLOCKED |
| T4 | Verdict is `reshape` but the pivot was never applied to `PROJECT.md` (or explicitly rejected via a decision) | `reshape.applied: false` | REQUIRED |
| T5 | The 48–72h validation test is `running` past its due date with no recorded result | `validation_test.due` < today | REQUIRED |
| T6 | Verdict exists but the validation test was never started | `validation_test.status: not-started` | RECOMMENDED |
| T7 | Audit staleness — MVP not yet shipped and the audit is older than `config.revalidate_after_days` (default 45) | audit date | RECOMMENDED |
| T8 | Reality disagrees — the primary KPI is off-track for `config.kpi_offtrack_streak` consecutive release snapshots (default 2) | `kpi-history.json` | RECOMMENDED |
| T9 | Phase boundary — `mvp.status` changed since the audit (especially `→ shipped`: re-audit before committing to the post-MVP phase) | `audited_mvp_status` mismatch | RECOMMENDED |

Non-machine triggers (agent judgment, log them in `triggers_log` when acted on): a credible new competitor,
a platform-policy change that touches a constraint, a load-bearing assumption observed breaking in the wild,
or the human saying "I'm not sure this is working."

> **Pre-Flight integration:** Pre-Flight step 3 (CLAUDE.md §2) runs `python3 scripts/check_viability.py`.
> REQUIRED/BLOCKED → convene the council before any build work. No exceptions without a logged decision.

---

## Step 1 — Assemble the brief (from state, not from questions)

Build the brief from what Praxis already knows. Read `project.json` (goal, audience, MVP, constraints,
stack), `profitability.json` (how it makes money), and `memory.json → summary` (context/edge). Compose one
short paragraph covering:

1. **The idea** — the one-sentence goal, expanded to 1–2 sentences.
2. **Who buys it and how it makes money** — audience + the active/planned profitability mechanisms.
3. **The builder's edge** — skills, audience, assets, distribution already in hand.
4. **Constraints** — budget, timeline, compliance, time-to-first-dollar pressure.

Only ask the human for what state cannot answer (usually the edge, sometimes pricing). One batch, 3 questions
max. If a required section of `PROJECT.md` is still placeholder, stop — the idea isn't authored enough to
audit; get it written first.

Paste the identical brief into every council member's prompt so all five judge the same thing.

## Step 2 — Convene the council (5 subagents, in parallel)

Spin up **all five personas in parallel in a single message** (one subagent each). Each returns: a one-line
stance, 3–5 sharpest points, the single most important thing the builder must hear, the load-bearing
assumptions it identified, and a 1–10 score on its own dimension (1 = walk away, 10 = no-brainer).

**1. The Contrarian (red team)**
> You are the Contrarian on an idea council. Assume this idea fails. Find the fatal flaws, the fastest way it
> dies, and the load-bearing assumptions that are probably wrong. Be ruthless and specific. No hedging, no
> "but it could work." Attack the weakest points. THE BRIEF: [brief]

**2. The Expansionist (bull)**
> You are the Expansionist on an idea council. Make the strongest possible case FOR this idea. Find the
> biggest upside, the 10x version, the adjacent opportunities and unlock points the builder isn't seeing. Be
> specific about where the real money and leverage could be. THE BRIEF: [brief]

**3. The Logician (first principles)**
> You are the Logician on an idea council. NO outside research, NO web. Reason purely from first principles:
> does the core mechanism make sense, do the incentives line up, does the math work even in theory? Include
> the unit economics implied by the brief's price and audience. Strip it to fundamentals and say whether it
> holds. THE BRIEF: [brief]

**4. The Researcher (evidence)**
> You are the Researcher on an idea council. Use web search. Bring real-world evidence: existing competitors,
> market size or demand signals, what comparable products charge, whether the real world validates or
> contradicts this. Also check the brief's constraints against platform/compliance reality. Cite what you
> find. THE BRIEF: [brief]

**5. The Buyer (voice of customer)**
> You are the Buyer on an idea council. Role-play the exact primary audience in the brief, first person.
> Would you actually pay for this? What's your real objection? What makes you pick a competitor or do
> nothing? What price feels right, and what makes you say yes today? Honest and slightly skeptical, not a
> cheerleader. THE BRIEF: [brief]

Every persona stays in character. None hedges or softens. The value is in the friction.

## Step 3 — The Judge delivers the verdict

The orchestrating agent acts as Judge. Read all five reports, name the real tension between them, and
resolve it — do not average scores. Fold in the economics lens: rough price, realistic time-to-first-dollar,
and whether the builder can ship fast given their stated edge. Then make an actual call. "It depends" is not
a verdict.

- **GO** — build the MVP as scoped (possibly with adjustments below).
- **RESHAPE** — the idea survives only with a specific pivot. Name the pivot precisely.
- **KILL** — walk away. Say why in one line.

The Judge must also produce:

- **Assumptions register** — the 3–7 load-bearing assumptions, each marked `untested | holding | broken`.
  These are what future re-audits check first.
- **MVP adjustments** — concrete edits to `PROJECT.md → MVP` (scope cuts, acceptance-criteria changes,
  target-date reality check). Scope cuts here are the cheapest ones you will ever make.
- **The 48–72h validation test** — the single cheapest, fastest test of the riskiest assumption BEFORE
  building: hypothesis, method, measurable success criteria, window (48–72h). This is the most important
  output of the entire audit.

## Step 4 — Write it to state (or it didn't happen)

1. Snapshot the previous `current` audit (if any) into `viability.json → history[]`.
2. Write the new audit into `viability.json → current`: verdict, confidence, scores, council one-liners,
   assumptions, MVP adjustments, the validation test (status `not-started`), and the **fingerprint** printed
   by `python3 scripts/check_viability.py --print-fingerprint`.
3. Set `audited_mvp_status` to the current `project.json → mvp.status`.
4. Append the firing trigger to `viability.json → triggers_log`.
5. If RESHAPE: propose the `PROJECT.md` edits to the human. When accepted, apply them, run
   `./bootstrap.sh sync`, **re-run the fingerprint**, update it, and set `reshape.applied: true`. If the
   human rejects the pivot, log the rejection as a decision (`dec-XXX`) and link it.
6. If KILL: stop build work. Proceeding requires a human-approved override decision logged in
   `decisions.json` and linked in `kill_override.decision_link`.
7. If the verdict changes project direction, log it as a decision with all three horizons; append a
   `memory.json` timeline entry (`type: pivot` or `milestone`).
8. Validate: `./bootstrap.sh validate .`

## Step 5 — Run the test, then close the loop

Start the validation test promptly: set `status: running`, `started`, and `due` (started + window). When the
window ends, record `result`, set `outcome` (`validated | invalidated | inconclusive`) and
`action_taken`, set `status: completed`. **An invalidated test is a T2-class event**: reconvene the Judge
(full council optional) and re-issue the verdict — often this is where GO becomes RESHAPE cheaply, 48 hours
in instead of 4 weeks in. `waived` is allowed only with a logged reason (e.g., the test is the MVP itself).

---

## Rules

- The council is adversarial on purpose. If all five scores land within ±1, the audit probably failed —
  interrogate the personas' independence before trusting it.
- The Judge picks GO, RESHAPE, or KILL and owns it. Confidence: low/medium/high.
- The cheapest 48–72h test is the highest-value artifact. A verdict without a runnable test is incomplete.
- Never soften a verdict because work is already underway. Sunk cost is the Contrarian's favorite meal.
- Keep the chat output skimmable (verdict block + scores line); the depth lives in `viability.json`.
