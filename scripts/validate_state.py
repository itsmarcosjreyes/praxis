#!/usr/bin/env python3
"""
validate_state.py — Validate .ai/state/*.json against .ai/schemas and enforce integrity rules.

Used by the pre-commit hook and the state-validation CI workflow. Dependency-light: Python stdlib,
with optional `jsonschema` for full schema validation (parse-only fallback if absent).

Checks:
  1. Every state file is valid JSON.
  2. Every state file validates against its schema (if jsonschema installed).
  3. IDs within each file's arrays are unique.
  4. (--strict) No leftover REPLACE_* placeholder TOKENS remain (drift in a real project). Matched as
     whole tokens (REPLACE_FOO), so prose that mentions the pattern does not count.

Template exemption: the Praxis baseline repo is a TEMPLATE and intentionally keeps REPLACE_* placeholders in
its seed state. A `.praxis-template` marker at the repo root downgrades strict placeholder failures to
warnings, so the same workflow (`validate_state.py --strict`) passes on the baseline and stays strict for
real projects (which must NOT have the marker). JSON/schema/duplicate-ID checks always apply.

Exit code 0 = pass, 1 = fail.

Usage:
  python3 scripts/validate_state.py [--strict] [--root DIR]
Env:
  PRAXIS_ROOT can set the repo root.
"""
import argparse
import re
import glob
import json
import os
import sys

GREEN, RED, YELLOW, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = YELLOW = RESET = ""


def find_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai", "state")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def collect_ids(node, found):
    """Recursively collect (container_is_list_of_objects) ids to check uniqueness per array."""
    if isinstance(node, list):
        ids = [x["id"] for x in node if isinstance(x, dict) and "id" in x]
        if ids:
            found.append(ids)
        for x in node:
            collect_ids(x, found)
    elif isinstance(node, dict):
        for v in node.values():
            collect_ids(v, found)


PLACEHOLDER_RE = re.compile(r"\bREPLACE_[A-Z0-9_]+\b")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="Fail on REPLACE_* placeholders.")
    ap.add_argument("--root", default=os.environ.get("PRAXIS_ROOT", "."))
    args = ap.parse_args()

    root = find_root(args.root) or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    state_dir = os.path.join(root, ".ai", "state")
    schema_dir = os.path.join(root, ".ai", "schemas")

    if not os.path.isdir(state_dir):
        print(f"{RED}✗ No .ai/state directory found under {root}{RESET}")
        return 1

    # Template exemption: the baseline repo keeps REPLACE_* placeholders on purpose. When the marker is
    # present, --strict placeholders become warnings (not failures). Real projects have no marker.
    is_template = os.path.exists(os.path.join(root, ".praxis-template"))
    strict_placeholders = args.strict and not is_template
    if args.strict and is_template:
        print(f"{YELLOW}  (.praxis-template present — strict placeholder check downgraded to warnings for the baseline.){RESET}")

    try:
        import jsonschema  # type: ignore
        have_schema = True
    except Exception:
        have_schema = False
        print(f"{YELLOW}  (jsonschema not installed — parse-only. `pip install jsonschema` for full checks.){RESET}")

    ok = True
    files = sorted(glob.glob(os.path.join(state_dir, "*.json")))
    if not files:
        print(f"{RED}✗ No state files found in {state_dir}{RESET}")
        return 1

    for path in files:
        name = os.path.basename(path)
        try:
            with open(path) as f:
                raw = f.read()
            data = json.loads(raw)
        except Exception as e:
            print(f"{RED}✗ {name}: invalid JSON — {e}{RESET}")
            ok = False
            continue

        # Schema
        schema_path = os.path.join(schema_dir, name.replace(".json", ".schema.json"))
        if have_schema and os.path.exists(schema_path):
            try:
                with open(schema_path) as f:
                    schema = json.load(f)
                jsonschema.validate(data, schema)
                schema_msg = "valid (schema)"
            except jsonschema.ValidationError as e:
                loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
                print(f"{RED}✗ {name}: schema error at {loc} — {e.message}{RESET}")
                ok = False
                continue
            except Exception as e:
                print(f"{RED}✗ {name}: schema load error — {e}{RESET}")
                ok = False
                continue
        else:
            schema_msg = "parses"

        # Unique IDs per array
        id_arrays = []
        collect_ids(data, id_arrays)
        dup_found = False
        for ids in id_arrays:
            dupes = {i for i in ids if ids.count(i) > 1}
            if dupes:
                print(f"{RED}✗ {name}: duplicate id(s) {sorted(dupes)}{RESET}")
                ok = False
                dup_found = True

        # Placeholders
        # Token match, not substring: only a real placeholder token (REPLACE_FOO) counts. Prose that merely
        # mentions "REPLACE_*" (e.g. a memory entry describing this very check) must not trip it.
        tokens = sorted(set(PLACEHOLDER_RE.findall(raw)))
        placeholder = bool(tokens)
        if placeholder and strict_placeholders:
            print(f"{RED}✗ {name}: leftover placeholder(s) {', '.join(tokens)} — fill in the value(s) "
                  f"(PROJECT.md + ./bootstrap.sh sync stamps REPLACE_PRODUCTION_ORIGIN){RESET}")
            ok = False
        elif placeholder:
            print(f"{YELLOW}⚠ {name}: contains placeholder(s) {', '.join(tokens)}{RESET}")

        if not dup_found and not (placeholder and strict_placeholders):
            print(f"{GREEN}✓ {name}: {schema_msg}{RESET}")

    print()
    print(f"{GREEN}STATE VALID{RESET}" if ok else f"{RED}STATE INVALID — fix the above before committing{RESET}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
