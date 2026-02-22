"""reddit-cli post — read a single Reddit post by ID or URL."""

import json
import re
import sys

from ..auth import get_client
from ..output import format_ts, _bold, _cyan, _dim


def _extract_id(id_or_url: str) -> str:
    """Extract submission ID from a full Reddit URL or return bare ID."""
    # Match /comments/<id>/ in a Reddit URL
    match = re.search(r"/comments/([a-z0-9]+)", id_or_url, re.IGNORECASE)
    if match:
        return match.group(1)
    # Assume it's already a bare ID
    return id_or_url.strip()


def run(args) -> int:
    reddit = get_client()
    sub_id = _extract_id(args.id_or_url)

    if not args.quiet:
        sys.stderr.write(f"[post] id={sub_id}\n")
        sys.stderr.flush()

    try:
        post = reddit.submission(sub_id)
        # Force attribute fetch
        _ = post.title
    except Exception as e:
        sys.stderr.write(f"Error: Could not fetch post {sub_id!r} — {e}\n")
        return 1

    d = {
        "id": post.id,
        "title": post.title,
        "url": f"https://www.reddit.com{post.permalink}",
        "subreddit": post.subreddit.display_name,
        "score": post.score,
        "upvote_ratio": post.upvote_ratio,
        "num_comments": post.num_comments,
        "author": post.author.name if post.author else None,
        "date": format_ts(post.created_utc),
        "selftext": post.selftext or "",
    }

    if args.output == "json":
        print(json.dumps(d, indent=2))
    else:
        print(f"{_bold(d['title'])}")
        print(f"{_cyan('r/' + d['subreddit'])} · u/{d['author'] or '[deleted]'} · {d['date']}")
        print(f"Score: {d['score']} ({int(d['upvote_ratio']*100)}% upvoted) · {d['num_comments']} comments")
        print(_dim(d["url"]))
        if d["selftext"]:
            print()
            print(d["selftext"])

    return 0
