#!/usr/bin/env bash
# fetch_metrics.sh — Reference wrapper that produces metrics.json for the KPI snapshot.
#
# Thin, CI-friendly front end for scripts/fetch_metrics.py. It:
#   1. Reports which metric sources are configured via env (observability).
#   2. Runs the config-driven fetcher (reads .ai/state/kpis.json, queries each KPI's source).
#   3. Always exits 0 if it produced a metrics.json — a missing/flaky source must NOT block a release;
#      snapshot_kpis.py carries previous values forward for any KPI omitted here.
#
# Wire into .github/workflows/kpi-snapshot.yml BEFORE the snapshot step:
#     - name: Fetch metrics
#       run: ./scripts/fetch_metrics.sh
#       env:
#         AMPLITUDE_API_KEY:         ${{ secrets.AMPLITUDE_API_KEY }}
#         AMPLITUDE_SECRET_KEY:      ${{ secrets.AMPLITUDE_SECRET_KEY }}
#         SUPABASE_URL:              ${{ secrets.SUPABASE_URL }}
#         SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
#         CRUX_API_KEY:              ${{ secrets.CRUX_API_KEY }}
# snapshot_kpis.py then auto-detects metrics.json (see kpi-snapshot.yml).
#
# Usage: ./scripts/fetch_metrics.sh [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--out metrics.json]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
PY="$(command -v python3 || true)"
[ -z "$PY" ] && { echo "fetch_metrics: python3 not found" >&2; exit 0; }

# --- Observability: which sources are configured? ---
configured() { [ -n "${!1:-}" ] && echo "set" || echo "MISSING"; }
echo "→ fetch_metrics: source credentials" >&2
echo "    amplitude : api_key=$(configured AMPLITUDE_API_KEY) secret=$(configured AMPLITUDE_SECRET_KEY)" >&2
echo "    supabase  : url=$(configured SUPABASE_URL) service_key=$(configured SUPABASE_SERVICE_ROLE_KEY)" >&2
echo "    crux      : api_key=$(configured CRUX_API_KEY)" >&2

# --- Run the fetcher (it logs each KPI to stderr, prints the out path to stdout) ---
OUT_PATH="$("$PY" "$HERE/fetch_metrics.py" --root "$ROOT" "$@")" || {
  echo "fetch_metrics: fetcher errored; writing empty metrics.json (all KPIs carry forward)" >&2
  echo '{}' > "$ROOT/metrics.json"
  echo "$ROOT/metrics.json"
  exit 0
}

COUNT="$("$PY" - "$OUT_PATH" <<'PY'
import json, sys
print(len(json.load(open(sys.argv[1]))))
PY
)"
echo "✓ fetch_metrics: wrote $OUT_PATH ($COUNT metric value(s); unlisted KPIs carry forward)" >&2
exit 0
