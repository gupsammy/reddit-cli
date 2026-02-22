"""Rendering helpers: compact lines and JSON output."""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any


# Honour NO_COLOR and --no-color (set via env after flag parsing)
def _use_color() -> bool:
    return sys.stdout.isatty() and not os.getenv("NO_COLOR") and os.getenv("REDDIT_CLI_NO_COLOR") != "1"


def _dim(text: str) -> str:
    return f"\033[2m{text}\033[0m" if _use_color() else text


def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m" if _use_color() else text


def _cyan(text: str) -> str:
    return f"\033[36m{text}\033[0m" if _use_color() else text


def format_ts(utc_ts: float) -> str:
    """Unix timestamp → YYYY-MM-DD."""
    return datetime.fromtimestamp(utc_ts, tz=timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Post (search result / single post)
# ---------------------------------------------------------------------------

def post_to_dict(post, *, include_selftext: bool = False, comments: list | None = None) -> dict:
    d = {
        "id": post.id,
        "title": post.title,
        "url": f"https://www.reddit.com{post.permalink}",
        "subreddit": post.subreddit.display_name,
        "score": post.score,
        "num_comments": post.num_comments,
        "author": post.author.name if post.author else None,
        "date": format_ts(post.created_utc),
        "upvote_ratio": post.upvote_ratio,
    }
    if include_selftext:
        d["selftext"] = post.selftext or ""
    if comments is not None:
        d["comments"] = comments
    return d


def print_post_compact(d: dict) -> None:
    score = _bold(f"[{d['score']:>6}]")
    sub = _cyan(f"r/{d['subreddit']}")
    print(f"{score} {sub} · {d['title']}")
    print(f"         {_dim(d['url'])}")


def print_posts_compact(items: list[dict]) -> None:
    for d in items:
        print_post_compact(d)


def print_posts_json(items: list[dict]) -> None:
    # Schema matches last30days openai_reddit parser expectations
    print(json.dumps({"items": items}, indent=2))


# ---------------------------------------------------------------------------
# Subreddits
# ---------------------------------------------------------------------------

def subreddit_to_dict(sub) -> dict:
    return {
        "name": sub.display_name,
        "url": f"https://www.reddit.com{sub.url}",
        "subscribers": getattr(sub, "subscribers", None),
        "public_description": getattr(sub, "public_description", "") or "",
        "created_utc": format_ts(sub.created_utc),
    }


def print_subreddits_compact(items: list[dict]) -> None:
    for s in items:
        subs = f"{s['subscribers']:,}" if s["subscribers"] else "?"
        print(f"{_cyan('r/' + s['name'])} ({subs} members)")
        if s["public_description"]:
            print(f"  {_dim(s['public_description'][:120])}")
        print(f"  {_dim(s['url'])}")


def print_subreddits_json(items: list[dict]) -> None:
    print(json.dumps({"subreddits": items}, indent=2))


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

def comment_to_dict(comment, depth: int = 0) -> dict | None:
    try:
        body = comment.body
    except AttributeError:
        return None  # MoreComments stub
    return {
        "id": comment.id,
        "author": comment.author.name if comment.author else None,
        "score": comment.score,
        "date": format_ts(comment.created_utc),
        "body": body,
        "depth": depth,
    }


def print_comments_compact(items: list[dict]) -> None:
    for c in items:
        indent = "  " * c.get("depth", 0)
        author = c["author"] or "[deleted]"
        score = _bold(f"[{c['score']}]")
        print(f"{indent}{score} {_dim('u/' + author)} · {_dim(c['date'])}")
        for line in c["body"].splitlines():
            print(f"{indent}  {line}")
        print()


def print_comments_json(items: list[dict]) -> None:
    print(json.dumps({"comments": items}, indent=2))


# ---------------------------------------------------------------------------
# Generic dispatcher
# ---------------------------------------------------------------------------

def emit(data: Any, fmt: str, *, compact_fn, json_fn) -> None:
    if fmt == "json":
        json_fn(data)
    else:
        compact_fn(data)
