"""reddit-cli subreddits — find subreddits by name or description, or browse popular ones."""

import sys

from ..auth import get_client
from ..output import (
    subreddit_to_dict,
    print_subreddits_compact,
    print_subreddits_json,
)


def run(args) -> int:
    reddit = get_client()

    if not args.quiet:
        if args.popular or not args.query:
            sys.stderr.write(f"[subreddits] popular limit={args.limit}\n")
        else:
            sys.stderr.write(f"[subreddits] q={args.query!r} by={args.by} limit={args.limit}\n")
        sys.stderr.flush()

    try:
        if args.popular or not args.query:
            source = reddit.subreddits.popular(limit=args.limit)
        elif args.by == "name":
            source = reddit.subreddits.search_by_name(args.query, include_nsfw=False)
        else:
            source = reddit.subreddits.search(args.query)

        items = []
        for sub in source:
            items.append(subreddit_to_dict(sub))
            if len(items) >= args.limit:
                break
    except Exception as e:
        sys.stderr.write(f"Error: Subreddit search failed — {e}\n")
        return 1

    if not args.quiet:
        sys.stderr.write(f"[subreddits] {len(items)} results\n")
        sys.stderr.flush()

    if args.output == "json":
        print_subreddits_json(items)
    else:
        print_subreddits_compact(items)

    return 0
