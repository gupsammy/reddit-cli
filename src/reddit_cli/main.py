#!/usr/bin/env python3
"""reddit-cli — search Reddit posts, subreddits, and threads via PRAW."""

import argparse
import os
import sys

from .commands import auth, comments, post, search, subreddits

VERSION = "1.0.0"


def _add_output_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-o", "--output",
        choices=["compact", "json"],
        default="compact",
        metavar="FORMAT",
        help="Output format: compact (default) or json",
    )


def _add_quiet_flag(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress progress messages on stderr",
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
  reddit-cli subreddits "AI coding tools" --by description
  reddit-cli post 1abc2de
  reddit-cli comments 1abc2de --min-score 10
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
        choices=["relevance", "hot", "top", "new", "comments"],
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
        help="Also fetch post body and top 5 comments per result",
    )
    _add_output_flag(p_search)
    _add_quiet_flag(p_search)

    # ── subreddits ───────────────────────────────────────────────────────────
    p_subs = sub.add_parser("subreddits", help="Find subreddits by name or description")
    p_subs.add_argument("query", help="Search query")
    p_subs.add_argument(
        "--by",
        choices=["name", "description"],
        default="name",
        help="Search by name or description (default: name)",
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
        help="Max top-level comments (default: 20)",
    )
    p_comments.add_argument(
        "--min-score",
        type=int,
        default=0,
        dest="min_score",
        metavar="N",
        help="Minimum upvote score to include (default: 0)",
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
