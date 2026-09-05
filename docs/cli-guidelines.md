# CLI design guidelines

This project follows the [Command Line Interface Guidelines][clig]
(clig.dev) for how the `readeck-cli` command line tool should look and
behave. Read the guidelines themselves for the full rationale — this
document does not restate them. It only records the concrete,
project-specific checklist used to check new or changed CLI behavior
against them.

An [`llms.txt`][clig-llms] version of the guidelines is also available,
useful for feeding to an LLM/agent directly.

This checklist is also used by the `clig-check` skill (see
`.claude/skills/clig-check/SKILL.md`) when reviewing CLI-related changes.

## Checklist

### Help & discoverability

- Every command and subcommand supports `-h`/`--help`.
- Running `readeck-cli` with no arguments prints usage information, not an
  error.

### Naming & structure

- Subcommands follow a consistent noun/verb pattern. Actual command and
  subcommand names are a separate, not-yet-decided project choice — this
  checklist only requires that whatever names are chosen stay internally
  consistent.
- A flag means the same thing, and behaves the same way, everywhere it
  appears (e.g. `-o`/`--output`, `--format`).

### Output

- Human-readable output by default.
- A machine-readable mode (e.g. `--json` or `--format=json`) is available
  for scripting.
- Output adapts to whether stdout is a terminal: no color/interactive
  elements when piped or redirected.
- Errors go to stderr, not stdout.
- Exit codes are meaningful and distinct: `0` on success, non-zero on
  failure.

### Input

- Precedence for a given setting is flag > environment variable > config
  file > default, and that precedence is documented.
- Stdin is accepted where it makes sense (e.g. piping content in).
- The tool never blocks on an interactive prompt when run
  non-interactively; a non-interactive escape hatch (`--yes`/`--force`) or
  TTY detection is provided instead.
- `--` is supported to mark the end of flag parsing.

### Config & state

- Config and cache files follow the XDG base directory spec (e.g.
  `~/.config/readeck-cli`, `~/.cache/readeck-cli`).
- API tokens and other credentials are never printed or logged.

### Robustness

- Network calls (the `httpx` client) have sane timeouts.
- `Ctrl-C` is handled gracefully.
- Operations are idempotent where practical.

### Versioning

- A `--version` flag is available.
- Releases follow semantic versioning.

[clig]: https://clig.dev/
[clig-llms]: https://clig.dev/llms.txt
