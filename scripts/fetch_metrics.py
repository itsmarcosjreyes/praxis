#!/usr/bin/env python3
"""
fetch_metrics.py — Reference metric fetcher. Reads kpis.json, queries each KPI's source, and writes
metrics.json ({ "kpi-001": 45.0, ... }) for snapshot_kpis.py to consume.

DESIGN (why it's built this way):
  - kpis.json is the SINGLE SOURCE OF TRUTH. We iterate the KPIs defined there and dispatch each to an
    adapter by its `instrumentation.source`. No KPI list is duplicated here, so the fetcher can't drift
    from the definitions.
  - Adapters are pure functions: (kpi, window) -> float | None. Add a source by adding one function.
  - FAILURE MODE IS SAFE BY DESIGN: if a source is unconfigured, errors, or returns nothing, the KPI is
    OMITTED from metrics.json (not zeroed). snapshot_kpis.py then carries the previous value forward, so a
    flaky metric source never blocks or corrupts a release. Every skip/error is logged to stderr.
  - Secrets come from env only. Deterministic, observable, dependency-light (stdlib + curl-free urllib).

PER-KPI CONFIG (optional, additive to the existing instrumentation block in kpis.json):
  "instrumentation": {
    "source": "amplitude" | "supabase" | "crux" | "script" | "manual",
    "event": "core_action_completed",     # amplitude event name
    "fetch": {                             # optional, source-specific overrides
      "metric": "uniques" | "totals" | "count",
      "table": "subscribers",             # supabase table
      "filter": "created_at=gte.{since}",  # supabase PostgREST filter ({since}/{until} templated)
      "url": "https://example.com/",      # crux target URL/origin
      "form_factor": "PHONE",             # crux: PHONE|DESKTOP|TABLET
      "percentile_metric": "largest_contentful_paint",  # crux metric key
      "command": "git rev-list --count HEAD"  # script: shell command whose stdout is the value
    }
  }

  The "script" source is the LOCAL-FIRST seam: no SaaS credentials, any measurable-by-command
  number becomes a KPI today (DB query via psql, log grep, ls | wc -l, curl | jq). The command
  runs from the repo root with {since}/{until} templated in; stdout must parse as a float.

USAGE:
  python3 scripts/fetch_metrics.py [--since ISO] [--until ISO] [--out metrics.json] [--root DIR]
ENV (only what your KPIs actually use):
  AMPLITUDE_API_KEY, AMPLITUDE_SECRET_KEY, [AMPLITUDE_BASE=https://amplitude.com]   # use ...eu for EU data
  SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
  CRUX_API_KEY
"""
import argparse
import base64
import datetime
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

LOG = lambda *a: print("  [fetch_metrics]", *a, file=sys.stderr)


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai", "state")):
            return d
        p = os.path.dirname(d)
        if p == d:
            return None
        d = p


def http_json(req, timeout=30):
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


# ---------------------------------------------------------------------------
# Adapters: (kpi, fetch_cfg, since, until) -> float | None
# ---------------------------------------------------------------------------

def fetch_amplitude(kpi, cfg, since, until):
    """Amplitude Dashboard REST API — event segmentation (uniques/totals) over the window.
    Docs: https://www.docs.developers.amplitude.com/analytics/apis/dashboard-rest-api/
    """
    api_key = os.environ.get("AMPLITUDE_API_KEY")
    secret = os.environ.get("AMPLITUDE_SECRET_KEY")
    if not api_key or not secret:
        LOG(f"{kpi['id']}: amplitude env not set — skip")
        return None
    event = cfg.get("event") or kpi.get("instrumentation", {}).get("event")
    if not event:
        LOG(f"{kpi['id']}: no amplitude event defined — skip")
        return None
    base = os.environ.get("AMPLITUDE_BASE", "https://amplitude.com")
    metric = cfg.get("metric", "uniques")  # uniques | totals
    e = urllib.parse.quote(json.dumps({"event_type": event}))
    start = since.strftime("%Y%m%d")
    end = until.strftime("%Y%m%d")
    url = f"{base}/api/2/events/segmentation?e={e}&start={start}&end={end}&m={metric}&i=30"
    token = base64.b64encode(f"{api_key}:{secret}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {token}"})
    try:
        data = http_json(req)
        series = data.get("data", {}).get("series", [[]])
        total = sum(series[0]) if series and series[0] else 0
        return float(total)
    except urllib.error.HTTPError as ex:
        LOG(f"{kpi['id']}: amplitude HTTP {ex.code} — skip")
    except Exception as ex:
        LOG(f"{kpi['id']}: amplitude error {ex} — skip")
    return None


def fetch_supabase(kpi, cfg, since, until):
    """Supabase via PostgREST exact count. Counts rows in a table over the window.
    Uses HEAD + Prefer: count=exact and reads Content-Range. Service-role key required (server-side only).
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        LOG(f"{kpi['id']}: supabase env not set — skip")
        return None
    table = cfg.get("table")
    if not table:
        LOG(f"{kpi['id']}: no supabase table in instrumentation.fetch — skip")
        return None
    flt = cfg.get("filter", "")
    flt = flt.replace("{since}", since.isoformat()).replace("{until}", until.isoformat())
    q = f"?select=*"
    if flt:
        q += "&" + flt
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}{q}"
    req = urllib.request.Request(endpoint, method="HEAD", headers={
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Prefer": "count=exact",
        "Range-Unit": "items",
        "Range": "0-0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            cr = r.headers.get("Content-Range", "")  # e.g. "0-0/1234"
            if "/" in cr:
                tail = cr.split("/")[-1]
                return float(tail) if tail.isdigit() else None
        LOG(f"{kpi['id']}: supabase no Content-Range — skip")
    except urllib.error.HTTPError as ex:
        LOG(f"{kpi['id']}: supabase HTTP {ex.code} — skip")
    except Exception as ex:
        LOG(f"{kpi['id']}: supabase error {ex} — skip")
    return None


def fetch_crux(kpi, cfg, since, until):
    """Chrome UX Report API — field p75 for a Core Web Vital (LCP/CLS/INP).
    Docs: https://developer.chrome.com/docs/crux/api
    """
    api_key = os.environ.get("CRUX_API_KEY")
    if not api_key:
        LOG(f"{kpi['id']}: CRUX_API_KEY not set — skip")
        return None
    target = cfg.get("url")
    if not target:
        LOG(f"{kpi['id']}: no crux url in instrumentation.fetch — skip")
        return None
    metric = cfg.get("percentile_metric", "largest_contentful_paint")
    body = {"metrics": [metric]}
    # origin-level if a bare origin, else url-level
    if target.rstrip("/").count("/") <= 2:
        body["origin"] = target
    else:
        body["url"] = target
    ff = cfg.get("form_factor")
    if ff:
        body["formFactor"] = ff
    endpoint = f"https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={api_key}"
    req = urllib.request.Request(
        endpoint, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        data = http_json(req)
        m = data.get("record", {}).get("metrics", {}).get(metric, {})
        p75 = m.get("percentiles", {}).get("p75")
        if p75 is None:
            return None
        val = float(p75)
        # CrUX returns ms for LCP/INP; KPIs target seconds for LCP. Convert if the KPI unit is seconds.
        if kpi.get("unit") == "seconds" and val > 50:  # heuristic: ms -> s
            val = val / 1000.0
        return val
    except urllib.error.HTTPError as ex:
        LOG(f"{kpi['id']}: crux HTTP {ex.code} — skip")
    except Exception as ex:
        LOG(f"{kpi['id']}: crux error {ex} — skip")
    return None


def fetch_script(kpi, cfg, since, until):
    """Local-first adapter: run instrumentation.fetch.command from the repo root and parse its
    stdout as a float. No credentials, no network required — the command owns its own access.
    {since}/{until} are templated into the command as ISO dates."""
    command = cfg.get("command")
    if not command:
        LOG(f"{kpi['id']}: no script command in instrumentation.fetch — skip")
        return None
    command = command.replace("{since}", since.isoformat()).replace("{until}", until.isoformat())
    try:
        proc = subprocess.run(command, shell=True, cwd=ROOT or ".",
                              capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            LOG(f"{kpi['id']}: script exit {proc.returncode} ({proc.stderr.strip()[:120] or 'no stderr'}) — skip")
            return None
        return float(proc.stdout.strip())
    except subprocess.TimeoutExpired:
        LOG(f"{kpi['id']}: script timed out (60s) — skip")
    except ValueError:
        LOG(f"{kpi['id']}: script stdout {proc.stdout.strip()[:60]!r} is not a number — skip")
    except Exception as ex:
        LOG(f"{kpi['id']}: script error {ex} — skip")
    return None


# Repo root for fetch_script's cwd; set in main() once resolved.
ROOT = None

ADAPTERS = {
    "amplitude": fetch_amplitude,
    "amplitude-eu": fetch_amplitude,
    "supabase": fetch_supabase,
    "crux": fetch_crux,
    "script": fetch_script,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("PRAXIS_ROOT", "."))
    ap.add_argument("--out", default="metrics.json")
    ap.add_argument("--since", default="", help="ISO date; default = 7 days ago")
    ap.add_argument("--until", default="", help="ISO date; default = today")
    args = ap.parse_args()

    root = find_root(args.root) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    global ROOT
    ROOT = root
    kpis_path = os.path.join(root, ".ai", "state", "kpis.json")
    if not os.path.exists(kpis_path):
        LOG(f"kpis.json not found at {kpis_path}")
        return 1

    until = datetime.date.fromisoformat(args.until) if args.until else datetime.date.today()
    since = datetime.date.fromisoformat(args.since) if args.since else (until - datetime.timedelta(days=7))
    LOG(f"window {since} .. {until}")

    with open(kpis_path) as f:
        kpis = json.load(f).get("kpis", [])

    out = {}
    for kpi in kpis:
        src = (kpi.get("instrumentation", {}) or {}).get("source", "")
        # source may be a "a|b" hint in the template seed — take the first concrete token
        src = src.split("|")[0].split("+")[0].strip()
        cfg = (kpi.get("instrumentation", {}) or {}).get("fetch", {}) or {}
        adapter = ADAPTERS.get(src)
        if not adapter:
            LOG(f"{kpi['id']}: source '{src}' has no adapter — skip (will carry forward)")
            continue
        val = adapter(kpi, cfg, since, until)
        if val is None:
            continue
        out[kpi["id"]] = val
        LOG(f"{kpi['id']}: {val}")

    out_path = os.path.join(root, args.out) if not os.path.isabs(args.out) else args.out
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    LOG(f"wrote {out_path} with {len(out)} value(s)")
    print(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
