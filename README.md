# Readeck CLI

CLI for Readeck

> Tested on **Readeck 0.23.2**

## Bruno collection

In `bruno/` you can find the Bruno collection generated from the OpenAPI file
downloaded from `http://<HOST>/readeck/docs/api`.

## Python CLI

This project is managed with [uv](https://github.com/astral-sh/uv). Python
3.14 is required.

To install the runtime dependencies:

```shell
uv sync
```

To also install development dependencies (linting, type checking, tests):

```shell
uv sync --dev
```

Run the CLI with:

```shell
uv run readeck-cli
```

### Configuration

Commands that talk to the Readeck API read the following environment
variables:

- `READECK_BASE_URL` — the Readeck API base URL (e.g.
  `http://<HOST>/readeck/api`).
- `READECK_BEARER_TOKEN` — a Readeck API token, sent as a `Bearer` token.

```shell
export READECK_BASE_URL="http://<HOST>/readeck/api"
export READECK_BEARER_TOKEN="<TOKEN>"
```

### Commands

- `readeck-cli bookmarks list [SEARCH]` — list bookmarks, optionally
  filtered by search.
- `readeck-cli bookmarks get <BOOKMARK_ID>` — show a single bookmark's
  full details.
- `readeck-cli bookmarks share <BOOKMARK_ID>` — create a public share
  link for a bookmark.
- `readeck-cli highlights get <BOOKMARK_ID>` — list a bookmark's
  highlights.
- `readeck-cli info` — show the Readeck instance's version and enabled
  features.

Run the checks locally:

```shell
uv run ruff check
uv run ruff format --check
uv run mypy src tests
uv run pytest
```

### CLI design guidelines

`readeck-cli` is designed to follow the
[Command Line Interface Guidelines](https://clig.dev/). See
[`docs/cli-guidelines.md`](docs/cli-guidelines.md) for the
project-specific checklist derived from them.

## Claude Code

This repository is configured for [Claude Code](https://claude.com/claude-code),
Anthropic's CLI for agentic coding, via the `.claude/` directory. It may pull
in skills from [Skills](https://www.skills.sh/), a marketplace of skills,
tracked in `skills-lock.json`.

It also uses the [Context7](https://context7.com/) plugin to fetch
up-to-date library and framework documentation. Context7 requires a
`CONTEXT7_API_KEY` environment variable, set in a local `.env` file (not
committed to version control).
