# Pack: web-seo

Opt in by adding `"web-seo"` to `project.json → active_packs`. Activates the SEO + Core Web Vitals release
gate (`rules/06-seo-pagespeed.md`) and the practices below. Default stack: Vercel + Next.js (SSR/SSG/ISR).

## What this pack adds
- SEO + page-speed becomes a **hard release gate** (not `n/a`) in `status.json → checklists.seo_pagespeed`.
- LCP, INP, CLS become tracked KPIs in `kpis.json` (snapshot per release).
- Email capture / growth loop required before MVP ship (`rules/08`).

## Setup checklist
- [ ] Rendering strategy chosen per route (SSG > ISR > SSR > CSR) and logged as a decision.
- [ ] Vercel Speed Insights + Analytics enabled; field CWV flowing.
- [ ] Lighthouse CI added to GitHub Actions; budget thresholds set; regressions block merge.
- [ ] `next-sitemap` (or equivalent) generating `sitemap.xml` + `robots.txt`.
- [ ] Metadata API used for per-route title/description/OG/Twitter/canonical.
- [ ] JSON-LD structured data for primary entities; validated.
- [ ] Image pipeline (next/image or equivalent) with AVIF/WebP + priority on LCP image.
- [ ] Font strategy: self-host/subset, `display: swap`, preload.
- [ ] Search Console + sitemap submitted.

## Recommended skills
`marketing:seo-audit`, `marketing:competitive-brief`, `design:accessibility-review`, `marketing:content-creation`.

## UI references
Pull component/layout patterns from `https://21st.dev/home`; adapt to the project design system (don't drop in raw).
Log references in `skills-ledger.json → ui_reference_sources`.
