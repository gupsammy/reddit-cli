"""reddit-cli search — search posts across Reddit."""

import sys
from praw.models import MoreComments

from ..auth import get_client
from ..output import (
    comment_to_dict,
    post_to_dict,
    print_posts_compact,
    print_posts_json,
)

def _resolve_time_filter(days: int) -> str:
    """Map --days to PRAW time_filter. Snap to nearest bucket."""
    if days <= 1:
        return "day"
    if days <= 7:
        return "week"
    if days <= 30:
        return "month"
    if days <= 365:
        return "year"
    return "all"


def _fetch_top_comments(submission, limit: int = 5) -> list[dict]:
    """Fetch top-level comments sorted by score."""
    try:
        submission.comments.replace_more(limit=0)
    except Exception:
        return []
    comments = []
    for comment in submission.comments:
        if isinstance(comment, MoreComments):
            continue
        d = comment_to_dict(comment)
        if d:
            comments.append(d)
        if len(comments) >= limit:
            break
    return sorted(comments, key=lambda c: c["score"], reverse=True)


def run(args) -> int:
    reddit = get_client()
    time_filter = _resolve_time_filter(args.days)
    limit = min(args.limit, 100)

    if not args.quiet:
        sys.stderr.write(
            f"[search] q={args.query!r} sub=r/{args.subreddit} "
            f"sort={args.sort} days={args.days}({time_filter}) limit={limit}\n"
        )
        sys.stderr.flush()

    try:
        subreddit = reddit.subreddit(args.subreddit)
        results = list(subreddit.search(
            args.query,
            sort=args.sort,
            time_filter=time_filter,
            limit=limit,
        ))
    except Exception as e:
        sys.stderr.write(f"Error: Reddit search failed — {e}\n")
        return 1

    if not args.quiet:
        sys.stderr.write(f"[search] {len(results)} results\n")
        sys.stderr.flush()

    items = []
    for post in results:
        comments = _fetch_top_comments(post, 5) if args.enrich else None
        items.append(post_to_dict(post, include_selftext=args.enrich, comments=comments))

    if args.output == "json":
        print_posts_json(items)
    else:
        print_posts_compact(items)

    return 0
