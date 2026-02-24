#!/usr/bin/env python3
"""reddit-cli — search Reddit posts, subreddits, and threads via PRAW."""

import argparse
import os
import sys

from .commands import auth, comments, domain, feed, post, search, subreddits, user

VERSION = "1.1.0"


def _add_output_flag(parser: argparse.ArgumentParser, *, include_csv: bool = False) -> None:
    choices = ["compact", "json", "csv"] if include_csv else ["compact", "json"]
    help_text = "Output format: compact (default), json" + (", or csv" if include_csv else "")
    parser.add_argument(
        "-o", "--output",
        choices=choices,
        default="compact",
        metavar="FORMAT",
        help=help_text,
    )


def _add_quiet_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress messages on stderr",
    )


def _add_sort_time_flags(parser: argparse.ArgumentParser, *, sorts: list[str], default_sort: str = "hot") -> None:
    """Add --sort and --time flags used by feed, domain, and user commands."""
    parser.add_argument(
        "--sort",
        choices=sorts,
        default=default_sort,
        help=f"Sort order (default: {default_sort})",
    )
    parser.add_argument(
        "--time",
        choices=["day", "week", "month", "year", "all"],
        default="week",
        metavar="PERIOD",
        help="Time filter for top/controversial sorts (default: week)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reddit-cli",
        description="Search Reddit via PRAW — no OpenAI needed.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  reddit-cli search "Claude Code skills"
  reddit-cli search "prompt engineering" -s LocalLLaMA --output json
  reddit-cli search "Midjourney v7" --days 7 --enrich --output json
  reddit-cli feed python --sort hot -n 10
  reddit-cli feed all --sort top --time day --output csv
  reddit-cli user spez --what posts --sort new -n 10
  reddit-cli user spez --what comments --output json
  reddit-cli domain github.com --sort top --time week
  reddit-cli subreddits "AI coding tools" --by description
  reddit-cli subreddits --popular -n 10
  reddit-cli post 1abc2de
  reddit-cli comments 1abc2de --min-score 10 --depth 2
  reddit-cli auth
        """,
    )
    parser.add_argument("--version", action="version", version=f"reddit-cli {VERSION}")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color output")

    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # ── search ──────────────────────────────────────────────────────────────
    p_search = sub.add_parser("search", help="Search posts across Reddit")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument(
        "-s", "--subreddit",
        default="all",
        metavar="SUB",
        help="Subreddit to search in (default: all)",
    )
    p_search.add_argument(
        "--sort",
        choices=["relevance", "hot", "top", "new", "comments", "controversial"],
        default="top",
        help="Sort order (default: top)",
    )
    p_search.add_argument(
        "--days",
        type=int,
        default=30,
        metavar="N",
        help="Look-back window in days: 1, 7, 30, 365 (default: 30)",
    )
    p_search.add_argument(
        "-n", "--limit",
        type=int,
        default=25,
        metavar="N",
        help="Max results, up to 100 (default: 25)",
    )
    p_search.add_argument(
        "--enrich",
        action="store_true",
        help="Also fetch post body and top comments per result",
    )
    p_search.add_argument(
        "--enrich-comments",
        type=int,
        default=5,
        dest="enrich_comments",
        metavar="N",
        help="Comments per post when --enrich is set (default: 5)",
    )
    _add_output_flag(p_search, include_csv=True)
    _add_quiet_flag(p_search)

    # ── feed ─────────────────────────────────────────────────────────────────
    p_feed = sub.add_parser("feed", help="Browse a subreddit's listing (hot/new/rising/top)")
    p_feed.add_argument("subreddit", help="Subreddit name (use 'all' for front page)")
    _add_sort_time_flags(p_feed, sorts=["hot", "new", "rising", "top", "controversial"])
    p_feed.add_argument(
        "-n", "--limit",
        type=int,
        default=25,
        metavar="N",
        help="Max posts, up to 100 (default: 25)",
    )
    _add_output_flag(p_feed, include_csv=True)
    _add_quiet_flag(p_feed)

    # ── user ─────────────────────────────────────────────────────────────────
    p_user = sub.add_parser("user", help="Fetch a redditor's recent posts or comments")
    p_user.add_argument("username", help="Reddit username (with or without u/ prefix)")
    p_user.add_argument(
        "--what",
        choices=["posts", "comments"],
        default="posts",
        help="Fetch posts or comments (default: posts)",
    )
    _add_sort_time_flags(p_user, sorts=["new", "hot", "top", "controversial"], default_sort="new")
    p_user.add_argument(
        "-n", "--limit",
        type=int,
        default=25,
        metavar="N",
        help="Max results, up to 100 (default: 25)",
    )
    _add_output_flag(p_user, include_csv=True)
    _add_quiet_flag(p_user)

    # ── domain ───────────────────────────────────────────────────────────────
    p_domain = sub.add_parser("domain", help="Find Reddit posts linking to a domain")
    p_domain.add_argument("domain", help="Domain name (e.g. github.com, nytimes.com)")
    _add_sort_time_flags(p_domain, sorts=["hot", "new", "rising", "top", "controversial"])
    p_domain.add_argument(
        "-n", "--limit",
        type=int,
        default=25,
        metavar="N",
        help="Max posts, up to 100 (default: 25)",
    )
    _add_output_flag(p_domain, include_csv=True)
    _add_quiet_flag(p_domain)

    # ── subreddits ───────────────────────────────────────────────────────────
    p_subs = sub.add_parser("subreddits", help="Find subreddits by name or description")
    p_subs.add_argument("query", nargs="?", default=None, help="Search query (omit with --popular)")
    p_subs.add_argument(
        "--by",
        choices=["name", "description"],
        default="name",
        help="Search by name or description (default: name)",
    )
    p_subs.add_argument(
        "--popular",
        action="store_true",
        help="List popular subreddits instead of searching",
    )
    p_subs.add_argument(
        "-n", "--limit",
        type=int,
        default=10,
        metavar="N",
        help="Max results (default: 10)",
    )
    _add_output_flag(p_subs)
    _add_quiet_flag(p_subs)

    # ── post ─────────────────────────────────────────────────────────────────
    p_post = sub.add_parser("post", help="Read a specific post by ID or URL")
    p_post.add_argument("id_or_url", help="Post ID (e.g. 1abc2de) or full Reddit URL")
    _add_output_flag(p_post)
    _add_quiet_flag(p_post)

    # ── comments ─────────────────────────────────────────────────────────────
    p_comments = sub.add_parser("comments", help="Read comments from a post")
    p_comments.add_argument("id_or_url", help="Post ID or full Reddit URL")
    p_comments.add_argument(
        "-n", "--limit",
        type=int,
        default=20,
        metavar="N",
        help="Max comments to collect (default: 20)",
    )
    p_comments.add_argument(
        "--min-score",
        type=int,
        default=0,
        dest="min_score",
        metavar="N",
        help="Minimum upvote score to include (default: 0)",
    )
    p_comments.add_argument(
        "--depth",
        type=int,
        default=0,
        metavar="N",
        help="Levels of nested replies to traverse (default: 0 = top-level only)",
    )
    _add_output_flag(p_comments)
    _add_quiet_flag(p_comments)

    # ── auth ─────────────────────────────────────────────────────────────────
    p_auth = sub.add_parser("auth", help="Verify Reddit credentials")
    _add_quiet_flag(p_auth)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Propagate --no-color to output module via env var
    if args.no_color:
        os.environ["REDDIT_CLI_NO_COLOR"] = "1"

    # Attach quiet default for commands that don't have it (auth)
    if not hasattr(args, "quiet"):
        args.quiet = False

    dispatch = {
        "search": search.run,
        "feed": feed.run,
        "user": user.run,
        "domain": domain.run,
        "subreddits": subreddits.run,
        "post": post.run,
        "comments": comments.run,
        "auth": auth.run,
    }

    runner = dispatch.get(args.command)
    if runner is None:
        parser.print_help(sys.stderr)
        sys.exit(2)

    sys.exit(runner(args))


if __name__ == "__main__":
    main()
