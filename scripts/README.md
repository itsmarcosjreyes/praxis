# scripts/ — enforcement & automation

Dependency-light Python (stdlib + optional `jsonschema`). These power the git hooks and CI workflows so the
state files can't silently drift and release bookkeeping happens automatically.

| Script | Does | Run by |
|---|---|---|
| `sync_project.py` | Compiles `PROJECT.md` (human authoring surface) into `.ai/state/project.json` (machine source of truth); `--check` detects drift | `pre-commit` hook, `bootstrap.sh sync` |
| `validate_state.py` | Validates every `.ai/state/*.json` against its schema; checks unique IDs; flags `REPLACE_*` placeholders (`--strict` to fail on them) | `pre-commit` hook, `state-validation.yml` |
| `check_release_gate.py` | Fails unless `docs/architecture/overview.md` is filled in (file-based), testing/security/deployment checklists are `passed` (SEO `passed`/`n/a`), and `release_gate_open: true` | `pre-push` hook (on `v*` tags), `kpi-snapshot.yml` |
| `snapshot_kpis.py` | Appends a per-release KPI snapshot (deltas + on_track), adds a `memory.json` release entry, optionally resets `status.json` | `kpi-snapshot.yml` |
| `fetch_metrics.py` | Reads `kpis.json`, queries each KPI's source (Amplitude/Supabase/CrUX), writes `metrics.json` | `kpi-snapshot.yml` (via `fetch_metrics.sh`) |
| `fetch_metrics.sh` | CI wrapper for the fetcher: reports configured sources, runs it, never blocks a release | `kpi-snapshot.yml` |

## Local use
```bash
python3 scripts/validate_state.py            # warn on placeholders
python3 scripts/validate_state.py --strict   # fail on placeholders (CI mode)
python3 scripts/check_release_gate.py        # is the release gate open?
python3 scripts/snapshot_kpis.py --release v1.2.0 --reset-status
python3 scripts/snapshot_kpis.py --release v1.2.0 --values metrics.json   # with real metric values
```

## Git hooks
Hooks live in `.githooks/` and are activated with `git config core.hooksPath .githooks`
(`bootstrap.sh init` does this automatically). Override a single run with `--no-verify` (discouraged).

- **pre-commit** → `validate_state.py` (every commit; blocks invalid state).
- **pre-push** → `check_release_gate.py` (only when pushing a `v*` tag; blocks unsanctioned releases).

## CI workflows (`.github/workflows/`)
- **state-validation.yml** — validates state on every push/PR (strict).
- **lighthouse-ci.yml** — Core Web Vitals + SEO gate; self-skips unless `web-seo` pack is active.
- **kpi-snapshot.yml** — on `v*` tag: enforce gate → snapshot KPIs → memory entry → reset status → commit back.

## The metric-fetch seam (now wired)
`snapshot_kpis.py` owns the *bookkeeping*; the *values* come from `fetch_metrics.py`, which reads
`kpis.json` and dispatches each KPI to an adapter by its `instrumentation.source`. This keeps the fetcher
in lockstep with the KPI definitions — there is no second list to maintain.

```bash
# Defaults to a 7-day window; override with --since/--until.
AMPLITUDE_API_KEY=... AMPLITUDE_SECRET_KEY=... SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... \
  ./scripts/fetch_metrics.sh                       # writes metrics.json
python3 scripts/snapshot_kpis.py --release v1.2.0 --values metrics.json --reset-status
```

**Supported sources** (add an adapter function to support more):

| source | query | required env |
|---|---|---|
| `amplitude` / `amplitude-eu` | event segmentation (`uniques`/`totals`) over the window | `AMPLITUDE_API_KEY`, `AMPLITUDE_SECRET_KEY` (`AMPLITUDE_BASE` for EU) |
| `supabase` | PostgREST exact row count on a table+filter | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` |
| `crux` | Chrome UX Report field **p75** for a Core Web Vital | `CRUX_API_KEY` |

Per-KPI query config lives in `kpis.json → instrumentation.fetch` (see `.ai/templates/entries.md`).

**Failure mode is safe by design:** if a source is unconfigured, errors, or returns nothing, that KPI is
*omitted* from `metrics.json` (never zeroed) and `snapshot_kpis.py` carries the previous value forward. A
flaky metric source therefore never blocks a release or corrupts history. Every skip is logged to stderr.

**Customize the queries:** the adapters implement sensible defaults (event counts, row counts, p75). Your
exact KPI formula may need a tweak — edit the adapter or the `fetch` block. The CrUX adapter auto-converts
ms→seconds when the KPI `unit` is `seconds` (LCP target is `2.5`).
