"""reddit-cli domain — find Reddit posts linking to a specific domain."""

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
            f"[domain] {args.domain} sort={args.sort}{time_note} limit={limit}\n"
        )
        sys.stderr.flush()

    try:
        domain_obj = reddit.domain(args.domain)
        if args.sort == "hot":
            gen = domain_obj.hot(limit=limit)
        elif args.sort == "new":
            gen = domain_obj.new(limit=limit)
        elif args.sort == "rising":
            gen = domain_obj.rising(limit=limit)
        elif args.sort == "top":
            gen = domain_obj.top(time_filter=args.time, limit=limit)
        else:  # controversial
            gen = domain_obj.controversial(time_filter=args.time, limit=limit)

        results = list(gen)
    except Exception as e:
        sys.stderr.write(f"Error: Domain fetch failed — {e}\n")
        return 1

    if not args.quiet:
        sys.stderr.write(f"[domain] {len(results)} posts\n")
        sys.stderr.flush()

    items = [post_to_dict(p) for p in results]

    if args.output == "json":
        print_posts_json(items)
    elif args.output == "csv":
        print_posts_csv(items)
    else:
        print_posts_compact(items)

    return 0
