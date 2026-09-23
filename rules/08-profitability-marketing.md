# Rule 08 — Profitability & Marketing

No project is "just technical." Profitability and growth are designed in from the start, tracked in
`profitability.json`, and tied to KPIs in `kpis.json`.

## Profitability rule (gate)
- At least **one mechanism must be `active`** in `profitability.json` before MVP ship.
- **Any web-accessible surface without an email capture or growth loop is not done.**
- Every mechanism links to a KPI (`kpi_link`) so its effect is measurable.

## Mechanism menu (pick at least one early)
- **Email capture** → nurture list (Supabase/Klaviyo). The default top-of-funnel for every project.
- **Cross-marketing to social** → auto-publish key moments/content (n8n) to drive traffic back.
- **Cross-sell across the portfolio** → shared auth, referrals, bundles with other Kinetic Matrix projects.
- **Paid tier / subscription / one-time / affiliate / sponsorship** → as the model matures.

## Marketing plan (fuels growth, tied to KPIs)
Maintain a lightweight plan that maps channels → actions → the KPI each moves. Build campaigns with
`marketing:campaign-plan`; content with `marketing:content-creation` / `marketing:email-sequence`; track with
`marketing:performance-report`. For each initiative record: channel, hypothesis, target KPI, owner, result.

Record the plan as data in **`.ai/state/marketing.json`** (schema `.ai/schemas/marketing.schema.json`).
The file is **optional**: a project with no plan simply omits it, and nothing else in Praxis requires it.
- `plan`: `status` (none/draft/active/paused/retired), a one-line `summary`, free-form `stage`, and
  `plan_doc` (a repo-relative path to the long-form plan, if you keep one).
- `initiatives[]` (`mkt-NNN`): `name`, `channel`, `hypothesis`, `kpi_link`, `owner`, `status`
  (idea/planned/active/done/dropped), `start`/`end`, `result`.
- `next_actions[]`: `what`, `due`, `channel`, `initiative`.
- `plan.external_refs[]`: optional `{label, ref}` pointers to a plan kept outside the repo (a shared doc,
  a second-brain path). Praxis never reads or resolves them; they exist so an outside tool can.

`bootstrap.sh export` carries it to consumers as `praxis-export.json → marketing` (contract 1.3.0).

Suggested loop:
1. **Acquire** — SEO (`rules/06`), social, referrals → traffic KPIs.
2. **Capture** — email capture / signup → growth KPIs (e.g. `kpi-003`).
3. **Activate** — onboarding to the core action → activation KPI (e.g. `kpi-001`).
4. **Monetize** — convert to a paid path → revenue KPI.
5. **Compound** — cross-sell + content flywheel across the portfolio.

## Cadence
- Re-confirm profitability + marketing alignment at every phase boundary (`roadmap.json`).
- Snapshot growth/revenue KPIs per release into `kpi-history.json` like any other KPI.
- Brand/voice consistency: use the `brand-voice:*` and `marketing:brand-review` skills for outward content.
