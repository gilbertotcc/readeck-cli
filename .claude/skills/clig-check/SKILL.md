---
name: clig-check
description: >
  Review CLI command code (new or changed) against this project's
  clig.dev-based checklist in docs/cli-guidelines.md. Use for "check CLI
  guidelines", "clig check", /clig-check, or proactively whenever CLI
  command behavior is authored or reviewed (including during
  /code-review).
---

Review the diff or command implementation under discussion against every
item in `docs/cli-guidelines.md`. That file is the checklist; do not
re-derive or restate clig.dev's guidance from memory.

## Procedure

1. Read `docs/cli-guidelines.md`.
2. Identify what CLI-facing surface actually changed: new/changed
   commands, flags, output formats, exit codes, config/env handling.
3. Walk each checklist section (help & discoverability, naming &
   structure, output, input, config & state, robustness, versioning) and
   check it against the actual change — not against the codebase in the
   abstract.
4. Report findings as a concrete list, each with a file:line reference
   where applicable:
   - Pass: skip it, don't list every passing item.
   - Fail: what's missing/wrong and which checklist item it violates.
   - Not applicable: state briefly why (e.g. no output change in this
     diff, so the output section doesn't apply).

## Boundaries

This skill reviews and reports. It does not implement fixes on its own —
apply changes only if the user asks for that after seeing the findings.
