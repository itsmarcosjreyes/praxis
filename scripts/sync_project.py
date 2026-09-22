#!/usr/bin/env python3
"""
sync_project.py — Compile PROJECT.md (human authoring surface) into .ai/state/project.json (machine SoT).

WHY THIS EXISTS:
  Editing JSON by hand is error-prone and unfriendly. PROJECT.md lets a human author (or drop in) the
  project's identity in Markdown; this script parses it and writes the canonical project.json that the rest
  of Praxis reads and validates (schemas, CI grep for active packs, agents reconstructing the project).

  PROJECT.md is the source you EDIT. project.json is GENERATED — do not hand-edit it; your changes would be
  overwritten on the next sync. The pre-commit hook runs this automatically so the two never drift.

CONTRACT:
  - Section headings in PROJECT.md are fixed; the parser keys off them.
  - `- **Key:** value` lines become scalars; `- **Key:**` followed by indented `- item` bullets become lists;
    bare `- item` bullets under a section become that section's list; plain paragraphs become prose.
  - Placeholder bullets ("...", "", "REPLACE…") are dropped from generated lists. Scalar REPLACE_ values are
    preserved so `validate_state.py --strict` still flags an unfilled project.
  - On the baseline template repo (has `.praxis-template`), meta dates stay as REPLACE_ISO_DATE so the
    template convention is preserved; real projects get today's date.

USAGE:
  python3 scripts/sync_project.py [--root DIR] [--check]
    (no flag)  write .ai/state/project.json from PROJECT.md
    --check    exit 1 if the generated JSON would differ from what's on disk (drift detection); writes nothing
"""
import argparse
import datetime
import json
import os
import re
import sys

GREEN, RED, YELLOW, RESET = ("\033[32m", "\033[31m", "\033[33m", "\033[0m") if sys.stdout.isatty() else ("", "", "", "")

ENUM_FIELDS = {"type", "status"}
KNOWN_PACKS = {"web-seo", "mobile", "ai-service", "streaming"}
PLACEHOLDER_ITEM = re.compile(r"^(\.\.\.|REPLACE)", re.IGNORECASE)


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai", "state")):
            return d
        p = os.path.dirname(d)
        if p == d:
            return None
        d = p


def norm(key):
    return re.sub(r"\s+", " ", key).strip().lower()


def clean_scalar(val):
    val = re.sub(r"<!--.*?-->", "", val)            # strip inline HTML comments
    val = re.sub(r"\s*\([^)]*\|[^)]*\)\s*$", "", val)  # strip "(a|b|c)" enum hints
    return val.strip()


def keep_item(item):
    item = item.strip()
    return bool(item) and not PLACEHOLDER_ITEM.match(item)


def split_sections(text):
    """Return {normalized H2 title: [lines]} for every `## Heading` section."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)  # drop block comments
    sections = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = norm(m.group(1))
            sections[cur] = []
        elif cur is not None:
            sections[cur].append(line)
    return sections


def parse_section(lines):
    """Return (scalars: dict, lists: dict, top_bullets: list, prose: str) for one section's lines."""
    scalars, lists, top, prose = {}, {}, [], []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        s = line.strip()
        if not s or s.startswith(">"):
            i += 1
            continue
        mkv = re.match(r"^- \*\*(.+?):\*\*\s*(.*)$", line)
        if mkv:
            key, val = norm(mkv.group(1)), mkv.group(2).strip()
            if val:
                scalars[key] = clean_scalar(val)
                i += 1
                continue
            # empty inline value: look ahead for indented bullets -> list; else empty scalar
            j, items = i + 1, []
            while j < n:
                if not lines[j].strip():
                    j += 1
                    continue
                mind = re.match(r"^[ \t]+- (.+)$", lines[j])
                if mind:
                    items.append(mind.group(1).strip())
                    j += 1
                    continue
                break
            if items:
                lists[key] = [x for x in items if keep_item(x)]
                i = j
                continue
            scalars[key] = ""
            i += 1
            continue
        mtop = re.match(r"^- (.+)$", line)
        if mtop:
            top.append(mtop.group(1).strip())
            i += 1
            continue
        prose.append(s)
        i += 1
    top = [x for x in top if keep_item(x)]
    return scalars, lists, top, " ".join(prose).strip()


def enum_token(val):
    """For type/status: take the first token, lowercased."""
    return val.split()[0].strip().lower() if val else val


def build_project(md_text, existing, today, templated):
    sec = split_sections(md_text)

    def S(name):
        return parse_section(sec.get(name, []))

    ident_s, _, _, _ = S("identity")
    _, _, nongoals, goal_prose = S("non-goals")
    _, _, _, goal_text = S("goal (one sentence)")
    _, _, _, kpi_text = S("primary kpi")
    aud_s, aud_l, _, _ = S("audience")
    mvp_s, mvp_l, _, _ = S("mvp")
    hor_s, _, _, _ = S("horizons")
    con_s, con_l, _, _ = S("constraints")
    stk_s, stk_l, _, _ = S("stack")
    _, _, packs_top, _ = S("active packs")

    date_val = "REPLACE_ISO_DATE" if templated else today
    meta = existing.get("meta", {}) if isinstance(existing, dict) else {}
    meta = {
        "schema_version": meta.get("schema_version", "1.0.0"),
        "created": meta.get("created", date_val),
        "last_updated": date_val,
        "updated_by": "sync_project.py (from PROJECT.md)",
        "source": "PROJECT.md",
    }

    primary_kpi = (kpi_text.split() or ["kpi-001"])[0]

    project = {
        "$schema": "../schemas/project.schema.json",
        "_generated": "GENERATED FROM PROJECT.md by scripts/sync_project.py — edit the Markdown, then run ./bootstrap.sh sync. Do not hand-edit this file.",
        "meta": meta,
        "identity": {
            "name": ident_s.get("name", "REPLACE_PROJECT_NAME"),
            "codename": ident_s.get("codename", ""),
            "slug": ident_s.get("slug", "replace-project-slug"),
            "type": enum_token(ident_s.get("type", "web")) or "web",
            "owner": ident_s.get("owner", "marcos@kineticmatrix.io"),
            "ecosystem": ident_s.get("ecosystem", "kinetic-matrix"),
            "repository": ident_s.get("repository", ""),
            "production_url": ident_s.get("production url", ""),
        },
        "goal": {
            "one_sentence": goal_text or "REPLACE: state the one-sentence goal.",
            "non_goals": nongoals,
            "primary_kpi_id": primary_kpi,
        },
        "audience": {
            "primary": aud_s.get("primary", ""),
            "secondary": aud_s.get("secondary", ""),
            "jobs_to_be_done": aud_l.get("jobs to be done", []),
        },
        "mvp": {
            "definition": mvp_s.get("definition", "The smallest shippable thing that delivers the one-sentence goal."),
            "in_scope": mvp_l.get("in scope", []),
            "out_of_scope": mvp_l.get("out of scope", []),
            "acceptance_criteria": mvp_l.get("acceptance criteria", []),
            "target_date": mvp_s.get("target date", ""),
            "status": enum_token(mvp_s.get("status", "not-started")) or "not-started",
        },
        "horizons": {
            "short_term": hor_s.get("short term", ""),
            "mid_term": hor_s.get("mid term", ""),
            "long_term": hor_s.get("long term", ""),
        },
        "constraints": {
            "business": con_l.get("business", []),
            "platform_compliance": con_l.get("platform compliance", []),
            "technical": con_l.get("technical", []),
            "budget": con_s.get("budget", ""),
        },
        "stack": {
            "frontend": stk_s.get("frontend", "vercel"),
            "backend": stk_s.get("backend", "supabase"),
            "compute": stk_s.get("compute", "modal"),
            "automation": stk_s.get("automation", "n8n"),
            "llm_routing": stk_s.get("llm routing", "openrouter"),
            "cloud": stk_s.get("cloud", "aws"),
            "ci_cd": stk_s.get("ci/cd", "github-actions"),
            "analytics": stk_s.get("analytics", "segment+amplitude"),
            "overrides": stk_l.get("overrides", []),
        },
        "active_packs": [p for p in packs_top if p in KNOWN_PACKS],
    }
    return project


PRODUCTION_ORIGIN_TOKEN = "https://REPLACE_PRODUCTION_ORIGIN/"


def find_key(obj, key):
    """Depth-first lookup of the first value stored under `key` anywhere in a nested dict/list."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            hit = find_key(v, key)
            if hit is not None:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = find_key(v, key)
            if hit is not None:
                return hit
    return None


def stamp_production_origin(root, project):
    """Fill the seed kpis.json CrUX example URL from PROJECT.md's Production URL.

    The baseline ships kpi-002 with `https://REPLACE_PRODUCTION_ORIGIN/`; strict validation (pre-commit and
    CI) rejects that token, so a fresh project could never commit until someone hand-edited kpis.json.
    Syncing PROJECT.md is the moment the origin becomes known, so stamp it here. No-op when the URL is
    blank/placeholder or the token is already gone.
    """
    url = find_key(project, "production_url")
    if not isinstance(url, str) or not url.strip() or "REPLACE_" in url:
        return
    kpis_path = os.path.join(root, ".ai", "state", "kpis.json")
    if not os.path.exists(kpis_path):
        return
    with open(kpis_path) as f:
        raw = f.read()
    if PRODUCTION_ORIGIN_TOKEN not in raw:
        return
    origin = url.strip().rstrip("/") + "/"
    with open(kpis_path, "w") as f:
        f.write(raw.replace(PRODUCTION_ORIGIN_TOKEN, origin))
    print(f"{GREEN}✓ Stamped production origin {origin} into .ai/state/kpis.json (was REPLACE_PRODUCTION_ORIGIN).{RESET}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.environ.get("PRAXIS_ROOT", "."))
    ap.add_argument("--check", action="store_true", help="Exit 1 if project.json is out of sync with PROJECT.md; write nothing.")
    args = ap.parse_args()

    root = find_root(args.root) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path = os.path.join(root, "PROJECT.md")
    json_path = os.path.join(root, ".ai", "state", "project.json")

    if not os.path.exists(md_path):
        print(f"{YELLOW}⚠ No PROJECT.md at {md_path} — nothing to sync.{RESET}")
        return 0

    with open(md_path) as f:
        md_text = f.read()

    existing = {}
    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    templated = os.path.exists(os.path.join(root, ".praxis-template"))
    today = datetime.date.today().isoformat()
    project = build_project(md_text, existing, today, templated)
    rendered = json.dumps(project, indent=2) + "\n"

    if args.check:
        current = ""
        if os.path.exists(json_path):
            with open(json_path) as f:
                current = f.read()
        # Compare ignoring last_updated churn so a date-only diff doesn't fail CI spuriously.
        def normalize(s):
            try:
                d = json.loads(s)
                d.get("meta", {}).pop("last_updated", None)
                return json.dumps(d, indent=2, sort_keys=True)
            except Exception:
                return s
        if normalize(rendered) != normalize(current):
            print(f"{RED}✗ project.json is out of sync with PROJECT.md. Run ./bootstrap.sh sync.{RESET}")
            return 1
        print(f"{GREEN}✓ project.json is in sync with PROJECT.md.{RESET}")
        return 0

    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w") as f:
        f.write(rendered)
    print(f"{GREEN}✓ Generated {os.path.relpath(json_path, root)} from PROJECT.md "
          f"(name={project['identity']['name']}, type={project['identity']['type']}, "
          f"packs={project['active_packs'] or 'none'}).{RESET}")
    if not templated:
        stamp_production_origin(root, project)
    return 0


if __name__ == "__main__":
    sys.exit(main())
