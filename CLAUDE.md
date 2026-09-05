# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project state

This repository is the seed of a future **Readeck CLI** (tested against Readeck
0.23.2). The Python project scaffold exists (package, dev tooling, CI), but no
actual CLI commands are implemented yet — `readeck_cli.main()` is still a
placeholder. The `bruno/` API collection, reverse-engineered from Readeck's
OpenAPI spec, is the reference for the API surface the CLI will eventually
wrap.

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

## Python tooling

- Install dependencies: `uv sync --dev` (add `--dev` to get ruff/mypy/pytest).
- Run the CLI: `uv run readeck-cli`.
- Lint/format: `uv run ruff check` and `uv run ruff format --check`.
- Type check: `uv run mypy src tests`.
- Tests: `uv run pytest`.
- All of the above run in CI on PRs/pushes to `main` touching Python files
  (see `.github/workflows/check-python.yml`), as three separate jobs (lint,
  typecheck, test).

## Working with the Bruno collection

- Do not hand-edit the generated per-endpoint request files if the OpenAPI
  spec changes — resync via Bruno's OpenAPI sync (`bruno.openapi` config in
  `opencollection.yml`) instead, then review the diff.

## CLI design guidelines

- `docs/cli-guidelines.md` is the project's checklist for how
  `readeck-cli` should look and behave, based on the [Command Line
  Interface Guidelines](https://clig.dev/) (clig.dev). Do not duplicate
  clig.dev's content elsewhere — link to it instead.
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
