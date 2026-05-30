# docs/features/

One Markdown file per feature, named `<slug>.feature.md`, created from `_TEMPLATE.feature.md`.

**Purpose:** make every feature independently resumable by any AI agent or human. A feature doc is the
narrative companion to the machine-readable state in `.ai/state/`. The JSON tracks status and IDs; the
feature doc holds the reasoning, design, and detail needed to continue the work cold.

## Rules
- Create the feature doc **before** writing code.
- Keep it current as the feature evolves; update the changelog at the bottom.
- Cross-link IDs: roadmap `item-XXX`, decisions `dec-XXX`, KPIs `kpi-XXX`, debt `debt-XXX`, profitability `prof-XXX`.
- When a feature ships, set its status here and in `roadmap.json`, and add a `memory.json` entry.

## Index
- _(list feature docs here as they're created)_
