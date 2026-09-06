# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project state

This repository is an in-progress **Readeck CLI** (tested against Readeck
0.23.2). The Python project scaffold (package, dev tooling, CI) is in place,
and `readeck-cli` already implements `info`, `highlights get`, and the
`bookmarks` group (`list`, `get`, `share`) — see the README's Commands
section for the full list. The `bruno/` API collection, reverse-engineered
from Readeck's OpenAPI spec, remains the reference for the rest of the API
surface the CLI has yet to wrap.

## Repository layout

- `bruno/Readeck API/` — a [Bruno](https://www.usebruno.com/) API collection,
  one `.yml` request file per endpoint, organized into folders by API area
  (e.g. `bookmarks`, `oauth`, `user profile`). This is the authoritative map
  of the Readeck API endpoints, request shapes, and auth requirements — read
  the relevant `.yml` file(s) here before implementing any CLI command that
  talks to a given endpoint.
- `bruno/Readeck API/opencollection.yml` — collection metadata, including the
  OAuth flows (Authorization Code and Device Code) and token-auth
  documentation for the Readeck API, and the `bruno.openapi` sync config that
  regenerates this collection from the downloaded OpenAPI spec.
- `src/readeck_cli/` — the CLI package (`src` layout), installed as the
  `readeck-cli` entry point.
- `tests/` — pytest suite, mirroring `src/readeck_cli/`.
- `pyproject.toml`, `uv.lock` — project metadata and dependency lockfile,
  managed with [uv](https://github.com/astral-sh/uv).
- `ruff.toml`, `mypy.ini`, `pytest.ini` — standalone tool configs (not
  `[tool.*]` tables in `pyproject.toml`) for lint/format, type checking, and
  tests, respectively.

## Architecture

`src/readeck_cli/` is layered:

- `cli/` — Click command/group definitions and output rendering
  (`output.py`). Calls into `commands/`; never imports
  `readeck_cli.infrastructure` directly.
- `commands/` — application logic per API area (`bookmarks.py`,
  `highlights.py`, `info.py`). The only layer allowed to import
  `readeck_cli.infrastructure`.
- `infrastructure/readeck_client/` — the low-level Readeck API client
  (HTTP requests, pagination, config, errors).

New commands must follow this layering: Click plumbing goes in `cli/`,
application logic in `commands/`, and any new HTTP calls in
`infrastructure/readeck_client/`.

## Python tooling

- Install dependencies: `uv sync --dev` (add `--dev` to get ruff/mypy/pytest).
- Run the CLI: `uv run readeck-cli`.
- Lint/format: `uv run ruff check` and `uv run ruff format --check`.
- Type check: `uv run mypy src tests`.
- Tests: `uv run pytest`.
- All of the above run in CI on PRs/pushes to `main` touching Python files
  (see `.github/workflows/check-python.yml`), as three separate jobs (lint,
  typecheck, test).

## CLI output regression fixtures

Full human-readable CLI output — a "get"-style command's rendered record, a
"list" command's rendered items, or a single-line summary like `bookmarks
share`'s — is tested with
[pytest-regressions](https://pytest-regressions.readthedocs.io/en/latest/)'
`file_regression` fixture instead of an inline expected string, so each
tested output scenario lives in its own reviewable `.txt` file (see
`tests/cli/test_bookmarks_get_command/` for the current example).

- One test function per output scenario, asserting
  `file_regression.check(result.output, extension=".txt")` (`result.output`,
  not `result.stdout` — it interleaves stdout and stderr in write order,
  matching what actually appears on an interactive terminal). Do not
  `@pytest.mark.parametrize` these tests: pytest-regressions sanitizes the
  test node name into the fixture filename, and parametrize IDs make that
  mangled and hard to scan.
- Fixture files live at pytest-regressions' default path — a directory
  named after the test module, sibling to it, e.g.
  `tests/cli/test_bookmarks_get_command/<test_function_name>.txt` — not a
  custom `basename`/`fullpath`.
- Two equally valid ways to update a fixture: hand-edit the `.txt` file
  first as the literal spec of desired output, then adjust the CLI code
  until the test passes; or implement the code change first, run
  `uv run pytest --force-regen` (or `--regen-all`), and review the diff
  before committing. Neither is a fallback for the other — pick whichever
  fits how you're approaching the change.
- Never pass `--force-regen`/`--regen-all` in CI — it would make CI accept
  whatever the code currently outputs instead of checking it against the
  committed baseline.
- `--json` output stays on `json.loads(result.output) == {...}` equality
  assertions, not `file_regression` — it's a machine contract, not a
  human-reviewed spec, so a byte-for-byte snapshot would just add noise.
- A passing fixture only proves the output matches what was last approved,
  not that the output is good — still run the `clig-check` skill (below)
  whenever a fixture is added or changed.

## Working with the Bruno collection

- Do not hand-edit the generated per-endpoint request files if the OpenAPI
  spec changes — resync via Bruno's OpenAPI sync (`bruno.openapi` config in
  `opencollection.yml`) instead, then review the diff.

## CLI design guidelines

- `docs/cli-guidelines.md` is the project's checklist for how
  `readeck-cli` should look and behave, based on
  [Command Line Interface Guidelines](https://clig.dev/) (clig.dev). Do
  not duplicate clig.dev's content elsewhere — link to it instead.
- Any change that adds or modifies CLI command behavior (a new command, a
  new flag, a changed output format, etc.) must be checked against that
  checklist.
- Before finishing such a change, or when reviewing one (including during
  `/code-review`), proactively run the `clig-check` skill.

## Readeck API basics

- Base API endpoint: `http://<HOST>/readeck/api`.
- Simple scripts authenticate with a per-user API token via
  `Authorization: Bearer <TOKEN>`.
- Third-party apps use OAuth 2.0 with **ephemeral clients**: a new client must
  be registered (`POST /oauth/client`) for each auth flow and is only valid
  for 10 minutes. Supports the Authorization Code flow (with mandatory PKCE,
  S256 only) and the Device Code flow (for browserless clients), with scopes
  `bookmarks:read`, `bookmarks:write`, `profile:read`. Full flow diagrams and
  code examples are in `opencollection.yml`.

## Markdown linting

Markdown files are linted in CI on PRs/pushes touching `**.md` (see
`.github/workflows/check-markdown.yml`):

- `markdownlint-cli2` using the rules in `.markdownlint-cli2.yaml` (ATX-style
  headings, 80-char line length except in tables/code blocks/headings,
  sibling-only duplicate heading check, aligned tables required).
- `lychee` link checker, configured via `.lycheeignore`, run across the whole
  repo with a 30s timeout.
