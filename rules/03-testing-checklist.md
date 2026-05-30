# Rule 03 — Testing Checklist (release gate)

On completion, set `status.json → checklists.testing.state` to `passed` or `failed` with `last_run`.
A `failed` or `not-run` testing checklist blocks release.

## Core (every project)
- [ ] Unit tests cover new/changed logic; meaningful assertions (not just "it renders").
- [ ] Critical-path integration tests pass (auth, data write, payment, core action).
- [ ] Edge cases: empty, null, max, concurrency, offline, slow network, timezone/locale.
- [ ] Error paths tested (failures handled, surfaced, logged — not swallowed).
- [ ] No flaky tests; deterministic or quarantined with a `tech-debt.json` entry.
- [ ] Regression: previously fixed bugs have a guarding test.
- [ ] CI runs the suite on every PR (GitHub Actions); red blocks merge.
- [ ] Coverage tracked; net coverage does not drop without a logged reason.
- [ ] KPI instrumentation events fire correctly (verify the event reaches the source).

## Web / SaaS
- [ ] E2E happy path automated (Playwright/Cypress).
- [ ] Cross-browser + responsive smoke (mobile, tablet, desktop).
- [ ] Accessibility checks run (axe / Lighthouse a11y) — see `design:accessibility-review`.

## Mobile (iOS / tvOS / Android)
- [ ] Unit + UI tests (XCTest / Espresso); snapshot tests for key screens.
- [ ] Tested on min + latest OS and representative device classes.
- [ ] tvOS: focus engine / remote navigation verified.
- [ ] Cold start, background/foreground, low-memory, and rotation paths.

## Streaming / OTT
- [ ] Playback start, seek, bitrate switch, audio-track switch, subtitle render.
- [ ] DRM/FairPlay license acquisition + expiry handling.
- [ ] Ad insertion (SSAI/CSAI) and analytics beacons (Conviva/OMSDK) fire.
- [ ] Live edge behavior, recovery from network drop, Chromecast handoff.

## AI service
- [ ] Eval set passes thresholds (accuracy/quality/latency/cost) — see `packs/ai-service`.
- [ ] Prompt-injection and jailbreak red-team cases handled.
- [ ] Token/cost budget per request within bound; fallback model path tested.
