# ADR 0007: Adopt the Praxis brand identity v1.0

> Human-readable mirror of a `decisions.json` entry. The JSON (`dec-007`) is canonical; this is for reading.

- **Decision ID:** dec-007
- **Status:** accepted
- **Date:** 2026-09-14
- **Author:** marcos@kineticmatrix.io
- **Category:** other
- **Supersedes / Superseded by:** — / —

## Context
Praxis is shared publicly as the canonical operating standard, but the repo had substantive documentation
and no identity — nothing that made it recognizable, quotable, or attributable. Brand Guidelines v1.0 were
authored externally and define the full system: the Gate mark (the Greek capital Π — two uprights and a
lintel, the threshold theory crosses to become action, terracotta on the right leg only), the paper / ink /
terracotta / ochre palette with a disciplined ≤10% accent ratio, the Spectral + Space Grotesk + JetBrains
Mono type triad, and a classical, hype-free voice with fixed taglines ("Theory, compiled into action.",
"If it isn't written, it didn't happen.").

## Options considered
1. **No brand; plain README** — zero maintenance, but unmemorable in public, no attribution surface, and
   the voice drifts with every edit.
2. **Adopt Brand Guidelines v1.0 into the repo** — canonical guide + SVG assets versioned alongside the
   standard they identify, a branded README, and a small asset-maintenance surface.

## Decision
Option 2. Specifics:

- **`assets/brand/`** holds the canonical guide (`BRAND_GUIDE.html`), the mark and lockup SVGs
  (light/dark), and a quick-reference (`README.md`) covering palette, type, voice, and misuse rules.
- **`README.md`** carries the branded header (theme-aware lockup, etymology, badge row in brand colors),
  brand-themed Mermaid diagrams, an author section, and the branded footer. Decorative emoji were removed
  from diagrams per the voice rules ("the rigor is the personality").
- **Containment:** `assets/` is intentionally **not** in the `bootstrap.sh init` copy list. Projects built
  on Praxis carry their own brand, never this one. The baseline README that `init` copies is expected to be
  replaced by each project's own README.
- **Attribution:** the README names Marcos J. Reyes as designer/maintainer and links the Kinetic Matrix
  body of work — the repo is a public proof-of-work artifact, and the brand is part of that claim.

## Tradeoff
A small asset-maintenance surface (assets must track the guide) in exchange for a recognizable,
attributable public standard.

## Horizons
- **Short term:** branded README and assets ship with the baseline; repo metadata (description, topics)
  matches the brand voice.
- **Mid term:** the same identity carries to the Praxis page on the Kinetic Matrix website and any docs
  site.
- **Long term:** Praxis is recognizable across the portfolio and public content while child-project brands
  remain untouched.
