<div align="center">

<h1>reddit-cli</h1>

<p>Search Reddit posts, browse subreddits, and read threads from the terminal — no OpenAI required.</p>

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/gupsammy/reddit-cli?label=version)](https://github.com/gupsammy/reddit-cli/releases)

</div>

---

`reddit-cli` is a fast, pipe-friendly command-line tool that queries Reddit via [PRAW](https://praw.readthedocs.io). It was built as a drop-in replacement for OpenAI-based Reddit search workflows — same compact or JSON output, zero LLM dependency. Useful for researchers, developers, and anyone who wants to query Reddit programmatically without a browser.

## ✨ Features

- **8 commands** covering every common Reddit access pattern: search, feed, user, domain, subreddits, post, comments, and auth
- Search posts across all of Reddit or a specific subreddit, with flexible sort and time filters
- Browse a subreddit's live listing by hot, new, rising, top, or controversial
- Fetch a redditor's recent posts or comment history
- Find all Reddit posts linking to any domain (great for tracking OSS project discussions)
- Discover subreddits by name, description, or popularity
- Read threaded comments with depth traversal and minimum-score filtering
- Three output modes: **compact** (human-readable), **json** (`{"items": [...]}` schema), **csv** (pipe to `xsv`, `mlr`)
- `--enrich` fetches post body + top N comments per search result
- Color auto-disables in pipes; controllable via `--no-color` or `NO_COLOR`
- Structured exit codes: `0` success · `1` API error · `2` usage error · `3` auth error

## 🚀 Quick Start

**One-line install** (macOS and Linux):

```bash
curl -fsSL https://raw.githubusercontent.com/gupsammy/reddit-cli/main/install.sh | bash
```

This downloads a pre-built binary to `~/.local/bin/reddit-cli`. No Python installation required. Pre-built binaries for macOS (arm64, x86_64) and Linux (x86_64) are available on the [Releases page](https://github.com/gupsammy/reddit-cli/releases).

> **macOS Gatekeeper:** On first run, macOS may block the unsigned binary. Run once to allow it:
> ```bash
> xattr -d com.apple.quarantine ~/.local/bin/reddit-cli
> ```

**Install from source** (Python 3.11+ required):

```bash
git clone https://github.com/gupsammy/reddit-cli.git
cd reddit-cli
pip install -e .
```

**Verify credentials:**

```bash
reddit-cli auth
```

## 💻 Usage

```bash
# Search posts (defaults: r/all, sort=top, last 30 days, 25 results)
reddit-cli search "Claude Code"

# Narrow to a subreddit, 7-day window, JSON output
reddit-cli search "prompt engineering" -s LocalLLaMA --days 7 --output json

# Fetch post body + top 5 comments per result
reddit-cli search "Midjourney v7" --days 7 --enrich --output json

# Browse r/python's hot feed
reddit-cli feed python --sort hot -n 10

# Browse front page, top posts today, CSV output
reddit-cli feed all --sort top --time day --output csv

# Get a redditor's recent posts
reddit-cli user spez --what posts --sort new -n 10

# Find all Reddit discussions linking to a domain
reddit-cli domain github.com --sort top --time week

# Discover subreddits matching a topic
reddit-cli subreddits "AI coding tools" --by description

# List currently popular subreddits
reddit-cli subreddits --popular -n 10

# Read a specific post by ID or URL
reddit-cli post 1abc2de

# Read comments with nested replies (2 levels), min 10 upvotes
reddit-cli comments 1abc2de --min-score 10 --depth 2

# Pipe JSON results to jq
reddit-cli search "python" --output json --quiet | jq '.items[].title'
```

## ⚙️ Configuration

`reddit-cli` needs a Reddit "script" app — create one (read-only scope is sufficient) at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).

**Credential variables:**

| Variable | Required | Default | Description |
|---|---|---|---|
| `REDDIT_CLIENT_ID` | Yes | — | Client ID from Reddit app settings |
| `REDDIT_CLIENT_SECRET` | Yes | — | Client secret from Reddit app settings |
| `REDDIT_USER_AGENT` | No | `reddit-cli/1.0` | User-agent string sent to the Reddit API |

**Resolution order** (first file that sets the variable wins):

| Priority | Source | Path / format |
|---|---|---|
| 1 | Shell environment | Already exported in current shell |
| 2 | Config file | `~/.config/reddit-cli/.env` — dotenv format, no `export` needed |
| 3 | Secrets file | `~/.secrets` — shell export format |
| 4 | Shell rc files | `~/.zshenv`, `~/.zshrc`, `~/.zshprofile`, `~/.profile`, `~/.bash_profile`, `~/.bashrc`, `~/.env` |

**Color control:** `REDDIT_CLI_NO_COLOR=1` or the standard `NO_COLOR` env var disables ANSI output unconditionally. Color is also automatically suppressed when stdout is not a TTY.

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
