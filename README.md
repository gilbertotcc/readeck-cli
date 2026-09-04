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

Run the checks locally:

```shell
uv run ruff check
uv run ruff format --check
uv run mypy src tests
uv run pytest
```

## Generating the API client

`src/readeck_cli/infrastructure/readeck_client/` is a Python client
generated from Readeck's OpenAPI spec with
[openapi-generator](https://openapi-generator.tech/docs/installation). It is
vendored (committed to the repository) but never hand-edited — regenerate it
instead:

```shell
# 1. Download the OpenAPI spec to a local file (it is not committed).
curl http://<HOST>/readeck/docs/api -o /path/to/openapi-spec.json

# 2. Generate the client into a scratch directory.
openapi-generator generate \
  -g python \
  -i /path/to/openapi-spec.json \
  -o /path/to/scratch-output \
  --package-name readeck_client \
  --skip-validate-spec \
  --global-property apiTests=false,modelTests=false,apiDocs=false,modelDocs=false

# 3. Replace the vendored package.
rm -rf src/readeck_cli/infrastructure/readeck_client
cp -r /path/to/scratch-output/readeck_client src/readeck_cli/infrastructure/

# 4. The generator assumes `readeck_client` is a top-level package; rewrite
#    its absolute imports to match its nested location.
python3 -c "
import re
from pathlib import Path

root = Path('src/readeck_cli/infrastructure/readeck_client')
pattern = re.compile(r'\breadeck_client\b')
for path in root.rglob('*.py'):
    text = path.read_text()
    path.write_text(pattern.sub('readeck_cli.infrastructure.readeck_client', text))
"
```

`src/readeck_cli/infrastructure/client.py` is a small hand-written
`ReadeckClient` wrapper around the generated client (base URL and Bearer
token configuration, one typed property per API area) — it is not generated
and should be edited like any other source file.

## Claude Code

This repository is configured for [Claude Code](https://claude.com/claude-code),
Anthropic's CLI for agentic coding, via the `.claude/` directory. It may pull
in skills from [Skills](https://www.skills.sh/), a marketplace of skills,
tracked in `skills-lock.json`.
