"""Credential loading and Reddit client initialisation."""

import os
import sys
from pathlib import Path

import praw
from dotenv import load_dotenv

_CONFIG_PATH = Path.home() / ".config" / "reddit-cli" / ".env"

_AUTH_HELP = """\
Error: Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET.

Create a Reddit app (script type, read-only is fine) at:
  https://www.reddit.com/prefs/apps

Then add credentials to ~/.config/reddit-cli/.env:
  REDDIT_CLIENT_ID=your_client_id
  REDDIT_CLIENT_SECRET=your_client_secret

Or export them as environment variables before running reddit-cli.
"""


def load_credentials() -> tuple[str, str, str]:
    """Return (client_id, client_secret, user_agent), exiting on error."""
    # Config file is lower-priority than env vars
    if _CONFIG_PATH.exists():
        load_dotenv(_CONFIG_PATH)

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
