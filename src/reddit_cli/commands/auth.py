"""reddit-cli auth — verify credentials are working."""

import sys

from ..auth import get_client, _CREDENTIAL_FILES


def run(_args) -> int:
    reddit = get_client()

    try:
        # read_only clients don't have an authenticated user, but we can
        # confirm the credentials are valid by fetching any subreddit.
        sub = reddit.subreddit("redditdev")
        _ = sub.id  # triggers credential check
        username = None
        try:
            username = reddit.user.me()
        except Exception:
            pass
    except Exception as e:
        sys.stderr.write(f"Auth failed: {e}\n")
        return 3

    if username:
        print(f"Authenticated as u/{username}")
    else:
        print("Read-only credentials OK (no username — script app without login)")

    print(f"Config: {_CREDENTIAL_FILES[0]}")
    return 0
