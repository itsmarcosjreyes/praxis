# Praxis

> *praxis* — the process by which theory becomes disciplined, repeatable action.

A standardized, AI-native operating system for building **any** project (web, SaaS, iOS/tvOS, Android,
streaming/OTT, AI service) with Claude — consistently, efficiently, and at scale. Drop it into any repo and
every agent that touches the project works to the same standard, even after context is compacted.

## The core idea
Your context window is volatile; **the JSON in `.ai/state/` is not**. Claude reconstructs the project from
those files every session. The rules enforce a disciplined lifecycle with hard release gates. The packs add
domain specifics only when you need them. You author the project's identity in friendly Markdown
(`PROJECT.md`); Praxis compiles it into the machine-readable `project.json` the rest of the system trusts.

> Golden rule: *If it isn't written to the relevant `.ai/state/*.json`, it didn't happen.*

## How Praxis works (visual)

### 1. The system at a glance
What lives in a Praxis-equipped repo and how the pieces relate. You author Markdown; Praxis compiles and
validates the machine state; rules and scripts enforce discipline; agents read state to work.

```mermaid
flowchart TB
    subgraph Author["✍️ You author (Markdown)"]
        PM["PROJECT.md<br/>project identity"]
        ARCH["docs/architecture/overview.md<br/>system design"]
        FEAT["docs/features/*.md<br/>per-feature specs"]
    end

    subgraph Instr["📜 Instructions & rules"]
        CL["CLAUDE.md<br/>master operating instructions"]
        RULES["rules/<br/>lifecycle, checklists, audits"]
        PACKS["packs/<br/>web-seo · mobile · ai-service · streaming"]
    end

    subgraph State["🗄️ .ai/state/ — source of truth (JSON)"]
        PJ["project.json"]
        DEC["decisions.json"]
        ROAD["roadmap.json"]
        KPI["kpis.json"]
        KPIH["kpi-history.json"]
        DEBT["tech-debt.json"]
        SKILL["skills-ledger.json"]
        MEM["memory.json"]
        PROF["profitability.json"]
        STAT["status.json"]
    end

    subgraph Enforce["⚙️ Enforcement (scripts + hooks + CI)"]
        SYNC["sync_project.py"]
        VAL["validate_state.py"]
        GATE["check_release_gate.py"]
        SNAP["snapshot_kpis.py"]
        FETCH["fetch_metrics.py"]
    end

    AGENT(["🤖 Claude / AI agent"])

    PM -->|"compiled by"| SYNC --> PJ
    SYNC -.->|"validated by"| VAL
    ARCH -.->|"checked by"| GATE
    CL --> AGENT
    RULES --> AGENT
    PACKS --> AGENT
    AGENT -->|"reads + writes"| State
    VAL --> State
    GATE --> STAT
    FETCH --> KPI
    SNAP --> KPIH
    AGENT -.->|"resumes from"| MEM
```

### 2. Project lifecycle — from empty repo to shipped release
The path a project takes. Pre-Flight runs before every unit of work; the release gate is a hard stop.

```mermaid
flowchart TD
    A["bootstrap.sh init"] --> B["Edit PROJECT.md<br/>(goal, MVP, stack, packs)"]
    B --> C["bootstrap.sh sync<br/>→ project.json"]
    C --> D{{"Pre-Flight Protocol<br/>(rules/01)"}}
    D --> D1["Load state · confirm one-sentence goal"]
    D --> D2["Locate horizon · MVP scope"]
    D --> D3["Skill & tool audit → skills-ledger.json"]
    D --> D4["Check tech-debt.json"]
    D --> D5["Ensure architecture/overview.md exists"]
    D1 & D2 & D3 & D4 & D5 --> E["BUILD<br/>feature docs · decisions · code · KPI instrumentation"]
    E --> F{{"Release gate<br/>(hard stop)"}}
    F -->|"any check fails"| E
    F -->|"architecture ✓ · testing ✓ · security ✓<br/>deploy ✓ · SEO ✓/n-a · gate open"| G["Tag v* release"]
    G --> H["CI: snapshot KPIs · memory entry<br/>reset status · commit back"]
    H --> I(["Shipped — KPIs tracked release-over-release"])
    I -.->|"next feature / next version"| D
```

### 3. Adding a feature — the inner loop
Every feature follows the same disciplined path, so any agent can resume it cold and state never drifts.

```mermaid
sequenceDiagram
    participant U as You
    participant C as Claude (agent)
    participant S as .ai/state/ + docs/
    participant G as Gates (hooks/CI)

    U->>C: "Add feature X"
    C->>S: Pre-Flight — read state, confirm goal & horizon
    C->>S: Skill/tool audit → skills-ledger.json
    C->>S: Create docs/features/x.feature.md (before coding)
    C->>S: Log choices → decisions.json (+ ADR)
    C->>C: Implement (may spin off parallel subagents)
    C->>S: KPI instrumentation → kpis.json
    C->>S: Record any debt → tech-debt.json
    C->>S: Update status.json (current focus, checklists)
    U->>G: git commit
    G-->>S: pre-commit: sync project.json + validate state
    G-->>U: ❌ blocks if state invalid / ✅ allows if clean
    U->>G: git tag v* && push
    G-->>U: pre-push: release gate (architecture + checklists)
```

### 4. Enforcement — why state can't silently drift
Discipline is machine-enforced at three moments: commit, tagged push, and CI.

```mermaid
flowchart LR
    subgraph Local["Local (git hooks)"]
        CM["git commit"] --> PC["pre-commit"]
        PC --> PC1["sync project.json from PROJECT.md"]
        PC --> PC2["validate_state.py<br/>schema · unique IDs"]
        PC2 -->|"invalid"| BLOCK1["❌ commit blocked"]
        PC2 -->|"valid"| OK1["✅ commit"]
        TAG["git push v* tag"] --> PP["pre-push"]
        PP --> PP1["check_release_gate.py"]
        PP1 -->|"gate closed"| BLOCK2["❌ push blocked"]
        PP1 -->|"gate open"| OK2["✅ push"]
    end

    subgraph CI["CI (GitHub Actions)"]
        SV["state-validation.yml<br/>every push/PR"]
        LH["lighthouse-ci.yml<br/>web-seo pack only"]
        KS["kpi-snapshot.yml<br/>on v* tag"]
        KS --> KS1["fetch metrics → snapshot KPIs"]
        KS1 --> KS2["memory entry · reset status · commit back"]
    end

    OK2 --> CI
    TMPL[".praxis-template marker<br/>baseline repo only"] -.->|"exempts"| PP1
```

### 5. Authoring identity — Markdown in, validated JSON out
You never hand-edit `project.json`; it's generated and kept in lockstep with `PROJECT.md`.

```mermaid
flowchart LR
    PM["PROJECT.md<br/>(human authoring surface)"] -->|"./bootstrap.sh sync<br/>or pre-commit hook"| SY["sync_project.py"]
    SY --> PJ["project.json<br/>(machine source of truth)"]
    PJ --> V["validate_state.py<br/>(schema)"]
    PJ --> AG["agents reconstruct project"]
    PJ --> CIuse["CI reads active_packs<br/>(e.g. triggers Lighthouse)"]
    SY -. "--check (drift detection)" .-> PM
```

## What's inside
- **`CLAUDE.md`** — master instructions, auto-loaded by the Claude VS Code extension. Start here.
- **`PROJECT.md`** — the human authoring surface for the project's identity (name, goal, MVP, stack, packs).
  Edit this, then `./bootstrap.sh sync` compiles it into `.ai/state/project.json`. **You edit the Markdown;
  the JSON is generated.**
- **`.ai/state/`** — 10 JSON source-of-truth files: project, decisions, roadmap, kpis, kpi-history,
  tech-debt, skills-ledger, memory, profitability, status. (`project.json` is generated from `PROJECT.md`.)
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
# Edit PROJECT.md (goal, MVP, type, stack, packs) — the human authoring surface. Do NOT edit project.json.
./bootstrap.sh sync .             # compile PROJECT.md -> .ai/state/project.json
./bootstrap.sh validate .         # check JSON + schemas
```
Then tell Claude: **"Run the Pre-Flight Protocol in CLAUDE.md."**

> Editing project identity is Markdown-first: author `PROJECT.md`, run `sync`. The pre-commit hook also
> regenerates `project.json` from `PROJECT.md` automatically, so the two never drift.

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

## Portfolio dashboard (the export contract)
Because all project state is normalized, typed JSON, you can point an admin dashboard at it without scraping.
`./bootstrap.sh export` emits **`praxis-export.json`** — a stable, versioned projection (`export_contract_version`)
with portfolio-safe `uid`s (`<slug>:<id>`), precomputed rollups, and a flattened relationship graph. A
dashboard is a **separate project** that consumes this contract — read it straight from git, upsert it into
Supabase on each release for cross-project queries, or publish it as a release asset. Praxis can evolve its
internal schemas freely as long as the exporter keeps emitting the contract. Schema:
`.ai/schemas/praxis-export.schema.json`; details in `scripts/README.md`.

```mermaid
flowchart LR
    subgraph Repos["Each Praxis project (its own repo)"]
        S1[".ai/state/*.json"] --> EX1["export_state.py"] --> J1["praxis-export.json<br/>(slug-namespaced)"]
    end
    J1 -->|"static read from git"| DASH
    J1 -->|"upsert on release"| SUP["Supabase<br/>(projection, keyed by uid)"]
    SUP --> DASH["📊 Admin dashboard<br/>(separate project)"]
    SUP -.->|"regression alert"| N8N["n8n / notify"]
```

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

