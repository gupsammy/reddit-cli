<div align="center">

<h1>reddit-cli</h1>

<p>Search Reddit posts, subreddits, and threads from the terminal — no OpenAI required.</p>

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/gupsammy/reddit-cli?label=version)](https://github.com/gupsammy/reddit-cli/releases)

</div>

---

`reddit-cli` is a fast, pipe-friendly command-line tool that searches Reddit via [PRAW](https://praw.readthedocs.io). It was built as a drop-in replacement for OpenAI-based Reddit search workflows — same compact or JSON output, zero LLM dependency. Useful for researchers, developers, and anyone who wants to query Reddit programmatically without a browser.

## Features

- Search posts across all of Reddit or a specific subreddit, with flexible sort and time filters
- Find subreddits by name or description
- Fetch a single post by ID or full URL, with optional self-text body
- Read comments from any thread with minimum-score filtering
- Two output modes: **compact** (human-readable) and **json** (pipe-friendly, `{"items": [...]}` schema)
- `--enrich` flag adds post body and top 5 comments per search result
- Color output auto-disables in pipes; also controllable via `--no-color` or `NO_COLOR`
- Structured exit codes: `0` success · `1` API error · `2` usage error · `3` auth error

## Installation

**Prerequisites:** Python 3.11+

```bash
git clone https://github.com/gupsammy/reddit-cli.git
cd reddit-cli
pip install -e .
```

Then verify credentials are wired up:

```bash
reddit-cli auth
```

## Usage

```bash
# Search posts (defaults: r/all, sort=top, last 30 days, 25 results)
reddit-cli search "Claude Code"

# Narrow to a subreddit, week window, JSON output
reddit-cli search "prompt engineering" -s LocalLLaMA --days 7 --output json

# Fetch post body + top comments per result
reddit-cli search "Midjourney v7" --days 7 --enrich --output json

# Find subreddits matching a topic
reddit-cli subreddits "AI coding tools" --by description

# Read a specific post
reddit-cli post 1abc2de

# Read top comments, minimum 10 upvotes
reddit-cli comments 1abc2de --min-score 10

# Pipe JSON results to jq
reddit-cli search "python" --output json --quiet | jq '.items[].title'
```

## Configuration

Credential resolution order (highest → lowest precedence):

| Source | Format | Path |
|--------|--------|------|
| Shell environment | `export VAR=val` | Inherited from shell |
| Config file | dotenv (`KEY=val`, no `export`) | `~/.config/reddit-cli/.env` |
| Secrets file | shell export format | `~/.secrets` |

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REDDIT_CLIENT_ID` | Yes | — | Client ID from Reddit app settings |
| `REDDIT_CLIENT_SECRET` | Yes | — | Client secret from Reddit app settings |
| `REDDIT_USER_AGENT` | No | `reddit-cli/1.0` | User-agent string sent to Reddit API |

Create a Reddit "script" app (read-only scope is sufficient) at https://www.reddit.com/prefs/apps to obtain credentials.

**Color control:** Set `REDDIT_CLI_NO_COLOR=1` or the standard `NO_COLOR` env var to disable ANSI output unconditionally. Color is also automatically suppressed when stdout is not a TTY.

## Roadmap

- [ ] `user` subcommand — fetch a user's recent post and comment history
- [ ] `trending` subcommand — surface rising posts across selected subreddits
- [ ] `--enrich` depth control (configurable comment limit, include nested replies)
- [ ] Result caching to avoid redundant API calls in scripted workflows
- [ ] Config file for persistent defaults (subreddit, sort, limit)

## Acknowledgments

- [PRAW](https://github.com/praw-dev/praw) — the Python Reddit API Wrapper that powers all data fetching
- [python-dotenv](https://github.com/theskumar/python-dotenv) — credential file loading

## License

MIT — see [LICENSE](LICENSE) for details.
