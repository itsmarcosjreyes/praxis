# Rule 06 — SEO & Page Speed (release gate for any web-accessible surface)

Mandatory for any project with a web surface. On completion set `status.json → checklists.seo_pagespeed.state`.
For non-web projects set it to `n/a`. Pairs with `packs/web-seo/`. Use `marketing:seo-audit` for deep audits.

## Core Web Vitals (gate — p75, field data preferred)
- [ ] **LCP ≤ 2.5s**
- [ ] **INP ≤ 200ms**
- [ ] **CLS ≤ 0.1**
- [ ] Lighthouse Performance ≥ 90 on key routes (lab check in CI).
- [ ] Track LCP/INP/CLS as KPIs in `kpis.json`; snapshot per release.

## Performance practices
- [ ] Server-render or statically generate primary content (SSR/SSG/ISR on Vercel).
- [ ] Images: modern formats (AVIF/WebP), correct sizing, `loading="lazy"`, priority hint for LCP image.
- [ ] Fonts: `font-display: swap`, preload, subset; avoid layout shift.
- [ ] JS budget enforced; code-split; defer non-critical; tree-shake; no unused deps.
- [ ] Caching/CDN headers correct; edge where it helps; compression (Brotli) on.
- [ ] Third-party scripts audited (each one justified; load deferred/async).

## SEO fundamentals (gate)
- [ ] Unique, descriptive `<title>` + meta description per route.
- [ ] One `<h1>`; logical heading hierarchy; semantic HTML.
- [ ] Canonical URLs; no duplicate-content traps.
- [ ] `robots.txt` + XML sitemap generated and submitted.
- [ ] Open Graph + Twitter cards for shareability.
- [ ] Structured data (JSON-LD) for relevant entities; validate with Rich Results test.
- [ ] Internal linking sensible; descriptive anchor text; no orphan pages.
- [ ] Mobile-friendly; responsive; tap targets ≥ 44px.
- [ ] Accessible (alt text, contrast, focus) — SEO and a11y overlap; run `design:accessibility-review`.

## Measurement
- [ ] Vercel Speed Insights / CrUX wired for field CWV.
- [ ] Lighthouse CI in GitHub Actions; regression on CWV/SEO score blocks merge.
- [ ] Search Console connected; index coverage monitored.

> Failing CWV or missing SEO fundamentals blocks release. Tie improvements to growth KPIs in `profitability.json`.
