# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project state

This repository is the seed of a future **Readeck CLI** (tested against Readeck
0.23.2). The Python project scaffold exists (package, dev tooling, CI), but no
actual CLI commands are implemented yet — `readeck_cli.main()` is still a
placeholder. The `bruno/` API collection, reverse-engineered from Readeck's
OpenAPI spec, is the reference for the API surface the CLI will eventually
wrap. A generated Python API client plus a thin hand-written wrapper already
exist under `src/readeck_cli/infrastructure/` (see below) for future CLI
commands to build on.

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
- `src/readeck_cli/infrastructure/readeck_client/` — a Python client
  generated from Readeck's OpenAPI spec via `openapi-generator`. Vendored
  (committed) but never hand-edited — see "Working with the generated API
  client" below.
- `src/readeck_cli/infrastructure/client.py` — `ReadeckClient`, a small
  hand-written wrapper around the generated client (base URL + Bearer token
  configuration, one typed property per API area). This is regular
  hand-written source, not generated.
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

## Working with the generated API client

- `src/readeck_cli/infrastructure/readeck_client/` is generated code — do not
  hand-edit it. Regenerate it via the `openapi-generator` command documented
  in the README's "Generating the API client" section, which also rewrites
  the generated absolute imports (the generator assumes `readeck_client` is a
  top-level package, not a nested one).
- It is excluded from strict lint/type-checking (`extend-exclude` in
  `ruff.toml`, a `[mypy-readeck_cli.infrastructure.readeck_client.*]`
  `ignore_errors` override in `mypy.ini`) since generated openapi-generator
  code cannot realistically satisfy this repo's strict ruleset. It is still
  exercised by `tests/infrastructure/test_generated_client_imports.py`, which
  imports every generated submodule as a regression check on regeneration.
- `src/readeck_cli/infrastructure/client.py` (`ReadeckClient`) is hand-written
  and must stay fully strict-clean and tested like the rest of `src/`. It
  exposes the generated `*Api` classes directly (e.g. `client.bookmarks`) —
  future CLI commands call operations on them; no per-operation wrapper
  methods or docstrings are added on top.

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
