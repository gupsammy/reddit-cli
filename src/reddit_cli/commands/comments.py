"""reddit-cli comments — fetch comments from a Reddit post."""

import re
import sys

from praw.models import MoreComments

from ..auth import get_client
from ..output import (
    comment_to_dict,
    print_comments_compact,
    print_comments_json,
)


def _extract_id(id_or_url: str) -> str:
    match = re.search(r"/comments/([a-z0-9]+)", id_or_url, re.IGNORECASE)
    if match:
        return match.group(1)
    return id_or_url.strip()


def _collect_comments(submission, limit: int, min_score: int) -> list[dict]:
    """Collect top-level comments, sorted by score, respecting limit and min_score."""
    try:
        submission.comments.replace_more(limit=0)
    except Exception:
        pass

    items = []
    for comment in submission.comments:
        if isinstance(comment, MoreComments):
            continue
        d = comment_to_dict(comment, depth=0)
        if d is None:
            continue
        if d["score"] < min_score:
            continue
        items.append(d)

    # Sort by score descending, then cap
    items.sort(key=lambda c: c["score"], reverse=True)
    return items[:limit]


def run(args) -> int:
    reddit = get_client()
    sub_id = _extract_id(args.id_or_url)

    if not args.quiet:
        sys.stderr.write(f"[comments] id={sub_id} limit={args.limit} min_score={args.min_score}\n")
        sys.stderr.flush()

    try:
        submission = reddit.submission(sub_id)
        items = _collect_comments(submission, args.limit, args.min_score)
    except Exception as e:
        sys.stderr.write(f"Error: Could not fetch comments for {sub_id!r} — {e}\n")
        return 1

    if not args.quiet:
        sys.stderr.write(f"[comments] {len(items)} comments\n")
        sys.stderr.flush()

    if args.output == "json":
        print_comments_json(items)
    else:
        print_comments_compact(items)

    return 0
