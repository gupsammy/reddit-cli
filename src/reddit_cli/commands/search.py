"""reddit-cli search — search posts across Reddit."""

import sys
from praw.models import MoreComments

from ..auth import get_client
from ..output import (
    comment_to_dict,
    post_to_dict,
    print_posts_compact,
    print_posts_csv,
    print_posts_json,
)

# Canonical day counts for each PRAW time_filter bucket
_BUCKET_DAYS = {"day": 1, "week": 7, "month": 30, "year": 365}


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


def _snap_note(days: int, resolved: str) -> str | None:
    """Return a note string if the user's --days value didn't map cleanly."""
    canonical = _BUCKET_DAYS.get(resolved)
    if canonical is None or days == canonical:
        return None
    return f"[search] note: --days {days} snapped to time_filter={resolved} (nearest PRAW bucket)\n"


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
        note = _snap_note(args.days, time_filter)
        if note:
            sys.stderr.write(note)
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

    enrich_limit = getattr(args, "enrich_comments", 5)
    items = []
    for post in results:
        comments = _fetch_top_comments(post, enrich_limit) if args.enrich else None
        items.append(post_to_dict(post, include_selftext=args.enrich, comments=comments))

    if args.output == "json":
        print_posts_json(items)
    elif args.output == "csv":
        print_posts_csv(items)
    else:
        print_posts_compact(items)

    return 0
