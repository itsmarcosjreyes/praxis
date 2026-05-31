# ADR 0003: Enforce a filled-in architecture description as a release gate

- **Decision ID:** dec-003
- **Status:** accepted
- **Date:** REPLACE_ISO_DATE
- **Author:** marcos@kineticmatrix.io
- **Category:** process
- **Supersedes / Superseded by:** — / —

## Context
Projects drift into tribal knowledge when the architecture lives only in code and people's heads. The
baseline had a `docs/architecture/` folder but nothing *required* or *verified* a real description, so a
project could ship with no written architecture at all.

## Options considered
1. **`status.json` boolean flag** — pros: simple, matches the checklist pattern; cons: self-reported, so it
   can be flipped `true` while the document stays empty.
2. **File-based gate on `docs/architecture/overview.md`** — pros: deterministic, can't be gamed, the
   artifact itself is the proof; cons: needs a content heuristic to judge "real."

## Decision
Add a file-based check to `scripts/check_release_gate.py`: `docs/architecture/overview.md` must exist,
contain no template placeholders (`REPLACE_`/`<FILL…>`/`<...>`), and have real substance
(≥ ~600 non-whitespace chars). Ship a canonical `overview.md` template and wire the requirement into the
Pre-Flight Protocol, the Build phase, and the release gate (CLAUDE.md §2/§10, rules/01).

## Tradeoff
A content heuristic (length + placeholder scan) verifies presence and effort, not quality — in exchange for
a deterministic gate that can't be faked by flipping a flag. Quality stays a human/review concern.

## Horizons
- **Short term:** releases are blocked until the architecture is actually written.
- **Mid term:** every project carries a current, readable architecture map; faster onboarding.
- **Long term:** portfolio-wide architectural legibility; less tribal knowledge as systems scale.

## Consequences
`docs/architecture/overview.md` ships as a required template and is copied into every new project by
`bootstrap.sh init`. The Praxis baseline repo itself keeps `REPLACE_` placeholders in the template, but its
`.praxis-template` marker short-circuits the gate, so the baseline is exempt while real projects are not.
