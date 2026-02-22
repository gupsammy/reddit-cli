# CLAUDE.md

## Development

Install in editable mode (required to run `reddit-cli` as a command):

```bash
pip install -e .
```

No test suite — manual smoke-testing against the live Reddit API is the primary verification method.

## Credentials

Env vars: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT` (optional, default `reddit-cli/1.0`).

Resolution order (highest → lowest):
1. Shell environment variables
2. `~/.config/reddit-cli/.env` (dotenv format, no `export` needed)
3. `~/.secrets` (shell export format, loaded via dotenv)

## Architecture

Data flow: `main.py` parses args → dispatches to `commands/<cmd>.run(args)` → calls `auth.get_client()` → serializes via `output.*_to_dict()` → renders via `output.emit()`.

**Output contract:** Progress/debug lines → `stderr` (gated by `--quiet`); results → `stdout`. Keeps the tool pipe-friendly.

**Return codes:** 0 = success, 1 = API/fetch error, 2 = usage/argparse error, 3 = auth error.

**Adding a command:** (1) Add `commands/<name>.py` with `run(args) -> int`, (2) register subparser in `main.py:build_parser()`, (3) add to the `dispatch` dict in `main()`.

**`--enrich` on `search`:** Fetches `selftext` + top 5 comments per result — multiplies API calls significantly, opt-in only.

**Color output:** Controlled by `REDDIT_CLI_NO_COLOR=1` (via `--no-color`) or standard `NO_COLOR` env var; `output._use_color()` checks both plus `sys.stdout.isatty()`.

**JSON schema:** `search --output json` wraps results in `{"items": [...]}` to match `last30days` OpenAI Reddit parser expectations.
