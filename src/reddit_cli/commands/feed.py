"""reddit-cli feed — browse a subreddit's listing without a search query."""

import sys

from ..auth import get_client
from ..output import (
    post_to_dict,
    print_posts_compact,
    print_posts_csv,
    print_posts_json,
)


def run(args) -> int:
    reddit = get_client()
    limit = min(args.limit, 100)

    if not args.quiet:
        time_note = f" time={args.time}" if args.sort in ("top", "controversial") else ""
        sys.stderr.write(
            f"[feed] r/{args.subreddit} sort={args.sort}{time_note} limit={limit}\n"
        )
        sys.stderr.flush()

    try:
        sub = reddit.subreddit(args.subreddit)
        if args.sort == "hot":
            gen = sub.hot(limit=limit)
        elif args.sort == "new":
            gen = sub.new(limit=limit)
        elif args.sort == "rising":
            gen = sub.rising(limit=limit)
        elif args.sort == "top":
            gen = sub.top(time_filter=args.time, limit=limit)
        else:  # controversial
            gen = sub.controversial(time_filter=args.time, limit=limit)

        results = list(gen)
    except Exception as e:
        sys.stderr.write(f"Error: Feed fetch failed — {e}\n")
        return 1

    if not args.quiet:
        sys.stderr.write(f"[feed] {len(results)} posts\n")
        sys.stderr.flush()

    items = [post_to_dict(p) for p in results]

    if args.output == "json":
        print_posts_json(items)
    elif args.output == "csv":
        print_posts_csv(items)
    else:
        print_posts_compact(items)

    return 0
