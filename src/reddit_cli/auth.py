"""Credential loading and Reddit client initialisation."""

import os
import sys
from pathlib import Path

import praw
from dotenv import load_dotenv

_H = Path.home()

# Searched in order; first file that provides REDDIT_CLIENT_ID wins.
_CREDENTIAL_FILES = [
    _H / ".config" / "reddit-cli" / ".env",  # explicit config (highest priority)
    _H / ".secrets",                          # common secrets file
    _H / ".zshenv",                           # zsh — all sessions, incl. non-interactive
    _H / ".zshrc",                            # zsh — interactive (macOS default shell)
    _H / ".zprofile",                         # zsh — login shell
    _H / ".profile",                          # POSIX fallback
    _H / ".bash_profile",                     # bash — login shell
    _H / ".bashrc",                           # bash — interactive
    _H / ".env",                              # bare dotenv convention
]

_AUTH_HELP = """\
Error: Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET.

Create a Reddit app (script type, read-only is fine) at:
  https://www.reddit.com/prefs/apps

Then export credentials in any of the usual places:
  ~/.config/reddit-cli/.env  (dotenv format, recommended)
  ~/.secrets / ~/.zshenv / ~/.zshrc / ~/.profile  (export KEY=value lines)

Or export them as environment variables before running reddit-cli.
"""


def load_credentials() -> tuple[str, str, str]:
    """Return (client_id, client_secret, user_agent), exiting on error.

    Precedence (highest → lowest):
      1. Env vars already exported in the shell
      2–10. Files in _CREDENTIAL_FILES order (stops at first file that sets the var)

    load_dotenv handles both plain KEY=value and shell `export KEY=value` syntax,
    and silently skips lines it cannot parse (functions, conditionals, etc.).
    """
    if not os.getenv("REDDIT_CLIENT_ID"):
        for path in _CREDENTIAL_FILES:
            if path.exists():
                load_dotenv(path)
            if os.getenv("REDDIT_CLIENT_ID"):
                break

    client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    user_agent = os.getenv("REDDIT_USER_AGENT", "reddit-cli/1.0").strip()

    if not client_id or not client_secret:
        sys.stderr.write(_AUTH_HELP)
        sys.exit(3)

    return client_id, client_secret, user_agent


def get_client() -> praw.Reddit:
    """Return an authenticated (read-only) PRAW Reddit instance."""
    client_id, client_secret, user_agent = load_credentials()
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )
