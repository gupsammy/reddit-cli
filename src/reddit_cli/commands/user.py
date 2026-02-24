"""reddit-cli user — fetch a redditor's recent posts or comments."""

import sys

import prawcore.exceptions

from ..auth import get_client
from ..output import (
    comment_to_dict,
    post_to_dict,
    print_comments_compact,
    print_comments_json,
    print_posts_compact,
    print_posts_csv,
    print_posts_json,
)


def run(args) -> int:
    reddit = get_client()
    username = args.username.lstrip("u/").lstrip("/")
    limit = min(args.limit, 100)

    if not args.quiet:
        time_note = f" time={args.time}" if args.sort in ("top", "controversial") else ""
        sys.stderr.write(
            f"[user] u/{username} what={args.what} sort={args.sort}{time_note} limit={limit}\n"
        )
        sys.stderr.flush()

    try:
        redditor = reddit.redditor(username)
        listing = redditor.submissions if args.what == "posts" else redditor.comments

        if args.sort == "new":
            gen = listing.new(limit=limit)
        elif args.sort == "hot":
            gen = listing.hot(limit=limit)
        elif args.sort == "top":
            gen = listing.top(time_filter=args.time, limit=limit)
        else:  # controversial
            gen = listing.controversial(time_filter=args.time, limit=limit)

        results = list(gen)
    except prawcore.exceptions.Forbidden:
        sys.stderr.write(f"Error: u/{username} has a private history — access denied.\n")
        return 1
    except prawcore.exceptions.NotFound:
        sys.stderr.write(f"Error: u/{username} not found.\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Error: Could not fetch user history — {e}\n")
        return 1

    if not args.quiet:
        sys.stderr.write(f"[user] {len(results)} {args.what}\n")
        sys.stderr.flush()

    if args.what == "posts":
        items = [post_to_dict(p) for p in results]
        if args.output == "json":
            print_posts_json(items)
        elif args.output == "csv":
            print_posts_csv(items)
        else:
            print_posts_compact(items)
    else:
        items = []
        for c in results:
            d = comment_to_dict(c)
            if d is not None:
                items.append(d)
        if args.output == "json":
            print_comments_json(items)
        else:
            print_comments_compact(items)

    return 0
