# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project state

This repository is the seed of a future **Readeck CLI** (tested against Readeck
0.23.2). No CLI source code exists yet — the repository currently contains
only a Bruno API collection reverse-engineered from Readeck's OpenAPI spec,
which serves as the reference for the API surface the CLI will eventually
wrap. When actual CLI code is added, this file should be updated with the
language/toolchain, build/test/lint commands, and code architecture.

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

## Working with the Bruno collection

- Do not hand-edit the generated per-endpoint request files if the OpenAPI
  spec changes — resync via Bruno's OpenAPI sync (`bruno.openapi` config in
  `opencollection.yml`) instead, then review the diff.

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
