#!/usr/bin/env bash
# bootstrap.sh — Drop the AI Guidance baseline into any project, validate state, manage hooks.
#
# Usage:
#   ./bootstrap.sh init <target-dir> [project-name]   Copy baseline, stamp dates, install git hooks
#   ./bootstrap.sh validate [dir]                      Validate all .ai/state/*.json against schemas
#   ./bootstrap.sh gate [dir]                          Check the release gate (status.json)
#   ./bootstrap.sh hooks [dir]                         (Re)install git hooks (core.hooksPath -> .githooks)
#   ./bootstrap.sh snapshot <release> [dir]            Append a KPI snapshot for a release tag
#   ./bootstrap.sh sync [dir]                          Regenerate .ai/state/project.json from PROJECT.md
#   ./bootstrap.sh crucible [dir]                      Check idea viability (is a Crucible audit owed?)
#   ./bootstrap.sh export [dir]                         Emit praxis-export.json (stable dashboard contract)
#   ./bootstrap.sh new-feature <slug>                  Create docs/features/<slug>.feature.md from template
#
# Designed for the Claude VS Code extension: CLAUDE.md at the repo root is auto-loaded as instructions.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TODAY="$(date +%Y-%m-%d)"

stamp_dates() {
  local root="$1"
  if command -v grep >/dev/null && grep -rl "REPLACE_ISO_DATE" "$root" >/dev/null 2>&1; then
    grep -rl "REPLACE_ISO_DATE" "$root" | while read -r f; do
      sed -i.bak "s/REPLACE_ISO_DATE/${TODAY}/g" "$f" && rm -f "${f}.bak"
    done
  fi
}

scrub_baseline_memory() {
  # The baseline's memory.json carries Praxis's OWN history (its releases, fixes, learnings). A fresh
  # project must not inherit it: reset the timeline to a single init entry and clear learnings, so the
  # product's memory holds only the product's events. (Other seed state stays as-is.)
  local root="$1" name="${2:-}"
  local f="$root/.ai/state/memory.json"
  [ -f "$f" ] && command -v python3 >/dev/null || return 0
  python3 - "$f" "$TODAY" "$name" <<'PY'
import json, sys
path, today, name = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(path))
label = name or "This project"
d["summary"] = {
    "what": f"{label}: one-paragraph plain-language description of the project as it stands today.",
    "where_we_are": "Freshly initialized from the Praxis baseline; nothing shipped yet.",
    "whats_next": "Run the Pre-Flight Protocol; the Crucible audits the idea before any build work.",
    "key_risks": [],
}
d["timeline"] = [{
    "id": "mem-001", "date": today, "type": "init",
    "title": "Project initialized from the Praxis baseline.",
    "detail": "Baseline copied by bootstrap.sh init. Praxis's own history was scrubbed so this timeline holds only this project's events.",
    "links": {"decision": None, "release": None, "feature_doc": None},
}]
d["learnings"] = []
d.setdefault("meta", {})["next_id"] = 2
d["meta"]["last_updated"] = today
with open(path, "w") as fh:
    json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")
PY
  echo "✓ memory.json reset: baseline history scrubbed, timeline starts at mem-001 (today)."
}

install_hooks() {
  local dir="$1"
  if [ -d "$dir/.git" ] || git -C "$dir" rev-parse --git-dir >/dev/null 2>&1; then
    chmod +x "$dir/.githooks/"* 2>/dev/null || true
    chmod +x "$dir/scripts/"*.py 2>/dev/null || true
    chmod +x "$dir/scripts/"*.sh 2>/dev/null || true
    git -C "$dir" config core.hooksPath .githooks
    echo "✓ Git hooks active (core.hooksPath -> .githooks): pre-commit (validate), pre-push (gate on v* tags)."
  else
    echo "⚠ $dir is not a git repo yet. After 'git init', run: ./bootstrap.sh hooks ."
  fi
}

cmd_init() {
  local target="${1:?Usage: bootstrap.sh init <target-dir> [project-name]}"
  local name="${2:-}"
  mkdir -p "$target"
  echo "→ Copying baseline into: $target"
  # NOTE: .praxis-template and CHANGELOG.md are intentionally NOT copied — they belong to the baseline repo
  # only. Omitting .praxis-template means projects get the full, enforced release gate.
  # PROJECT.md is the human authoring surface; project.json is generated from it by scripts/sync_project.py.
  for item in CLAUDE.md README.md PROJECT.md .gitignore .ai rules docs packs scripts .githooks .github lighthouserc.json bootstrap.sh; do
    [ -e "$HERE/$item" ] && cp -R "$HERE/$item" "$target/"
  done
  stamp_dates "$target/.ai"
  stamp_dates "$target/docs"
  scrub_baseline_memory "$target" "$name"
  if [ -n "$name" ]; then
    # Stamp the name into the authoring Markdown; project.json is regenerated from it below.
    sed -i.bak "s/REPLACE_PROJECT_NAME/${name}/g" "$target/PROJECT.md" && rm -f "$target/PROJECT.md.bak"
  fi
  # Generate project.json from PROJECT.md so the machine source-of-truth exists immediately.
  if command -v python3 >/dev/null; then
    python3 "$target/scripts/sync_project.py" --root "$target" || true
  fi
  install_hooks "$target"
  echo "✓ Baseline installed. Next steps:"
  echo "  1) git init (if needed), then: ./bootstrap.sh hooks ."
  echo "  2) Open $target in VS Code (CLAUDE.md auto-loads as Claude instructions)."
  echo "  3) Fill in PROJECT.md: name, slug, type, goal, MVP, packs. (Edit the Markdown, NOT project.json.)"
  echo "  4) Run: ./bootstrap.sh sync   (regenerates .ai/state/project.json from PROJECT.md)."
  echo "  5) Tell Claude: 'Run the Pre-Flight Protocol in CLAUDE.md.' Pre-Flight will detect the fresh idea"
  echo "     and convene the Crucible (rules/09-crucible.md) to stress-test it BEFORE any build work."
}

cmd_validate() {
  local dir="${1:-$HERE}"
  if command -v python3 >/dev/null; then
    python3 "$dir/scripts/validate_state.py" --root "$dir"
  else
    echo "python3 not found; cannot validate."; exit 1
  fi
}

cmd_gate() {
  local dir="${1:-$HERE}"
  python3 "$dir/scripts/check_release_gate.py" --root "$dir"
}

cmd_hooks() {
  local dir="${1:-$HERE}"
  install_hooks "$dir"
}

cmd_snapshot() {
  local release="${1:?Usage: bootstrap.sh snapshot <release> [dir]}"
  local dir="${2:-$HERE}"
  python3 "$dir/scripts/snapshot_kpis.py" --release "$release" --root "$dir" --reset-status
}

cmd_sync() {
  local dir="${1:-$HERE}"
  python3 "$dir/scripts/sync_project.py" --root "$dir"
}

cmd_crucible() {
  local dir="${1:-$HERE}"
  python3 "$dir/scripts/check_viability.py" --root "$dir"
}

cmd_export() {
  local dir="${1:-$HERE}"
  python3 "$dir/scripts/export_state.py" --root "$dir" --pretty
}

cmd_new_feature() {
  local slug="${1:?Usage: bootstrap.sh new-feature <slug>}"
  local dest="$HERE/docs/features/${slug}.feature.md"
  cp "$HERE/docs/features/_TEMPLATE.feature.md" "$dest"
  echo "✓ Created $dest"
}

case "${1:-}" in
  init)        shift; cmd_init "$@";;
  validate)    shift; cmd_validate "$@";;
  gate)        shift; cmd_gate "$@";;
  hooks)       shift; cmd_hooks "$@";;
  snapshot)    shift; cmd_snapshot "$@";;
  sync)        shift; cmd_sync "$@";;
  crucible)    shift; cmd_crucible "$@";;
  export)      shift; cmd_export "$@";;
  new-feature) shift; cmd_new_feature "$@";;
  *) echo "Usage: $0 {init <dir> [name] | validate [dir] | gate [dir] | hooks [dir] | snapshot <release> [dir] | sync [dir] | crucible [dir] | export [dir] | new-feature <slug>}"; exit 1;;
esac
