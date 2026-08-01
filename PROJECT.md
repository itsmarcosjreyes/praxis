# Project Definition

> **This Markdown file is the human authoring surface for the project's identity.** Edit it (or drop in a
> filled-in copy), then run `./bootstrap.sh sync` — that compiles it into `.ai/state/project.json`, which is
> the machine-readable source of truth the rest of Praxis reads and validates. **Edit this file, not the
> JSON.** The pre-commit hook also regenerates the JSON from this file automatically.
>
> Keep the section headings exactly as written — the parser keys off them. Fill in the values; delete the
> `REPLACE_…`/`...` placeholders as you go.
>
> **The idea written here gets stress-tested before it gets built.** The idea-defining sections (Goal,
> Non-goals, Primary KPI, Audience, MVP, Constraints) are fingerprinted; a new or changed idea makes a
> **Crucible audit** (`rules/09-crucible.md`) REQUIRED before build work — a 5-persona council issues a
> GO / RESHAPE / KILL verdict plus a 48–72h validation test, recorded in `.ai/state/viability.json` and
> enforced by `scripts/check_viability.py`.
>
> Allowed values:
> - **Type:** `web` | `saas` | `ios` | `tvos` | `android` | `streaming` | `ai-service` | `library` | `other`
> - **MVP status:** `not-started` | `in-progress` | `shipped`
> - **Active packs:** `web-seo` | `mobile` | `ai-service` | `streaming`

## Identity
- **Name:** REPLACE_PROJECT_NAME
- **Codename:**
- **Slug:** replace-project-slug
- **Type:** web
- **Owner:** marcos@kineticmatrix.io
- **Ecosystem:** kinetic-matrix
- **Repository:**
- **Production URL:**

## Goal (one sentence)
REPLACE: [Project] helps [who] achieve [outcome] by [mechanism], measured by [primary KPI].

## Primary KPI
kpi-001

## Non-goals
- Explicitly list what this project will NOT do, to protect scope.

## Audience
- **Primary:**
- **Secondary:**
- **Jobs to be done:**
  - ...

## MVP
- **Definition:** The smallest shippable thing that delivers the one-sentence goal.
- **Status:** not-started
- **Target date:**
- **In scope:**
  - ...
- **Out of scope:**
  - ...
- **Acceptance criteria:**
  - ...

## Horizons
- **Short term:** Next 1-2 weeks / this release.
- **Mid term:** This quarter. What this unlocks or constrains.
- **Long term:** Platform vision. Why this scales.

## Constraints
- **Business:**
  - ...
- **Platform compliance:**
  - ...
- **Technical:**
  - ...
- **Budget:**

## Stack
> Defaults below. Override per project and log the override as a decision (`decisions.json`).
- **Frontend:** vercel
- **Backend:** supabase
- **Compute:** modal
- **Automation:** n8n
- **LLM routing:** openrouter
- **Cloud:** aws
- **CI/CD:** github-actions
- **Analytics:** segment+amplitude
- **Overrides:**
  - ...

## Active packs
> Opt in by listing packs here (one per bullet). Leave the placeholder to activate none.
- ...
