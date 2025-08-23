from __future__ import annotations
import argparse, sys, os, webbrowser, json
from .client import Rule34Client

def _print_post_json(post):
    """Prints a single post's details as a JSON object."""
    data = {
        "id": post.id,
        "page_url": post.page_url,
        "image_url": post.image_url,
        "sample_url": post.sample_url,
        "thumbnail_url": post.thumbnail_url,
        "rating": getattr(post, 'rating', None),
        "tags": getattr(post, 'tags', []),
        "author": getattr(post, 'author', None),
        "source": getattr(post, 'source', None),
        "width": getattr(post, 'width', None),
        "height": getattr(post, 'height', None),
        "file_ext": getattr(post, 'file_ext', None),
    }
    print(json.dumps(data, indent=2))

def _print_post_list(posts):
    """Prints a list of posts in a simple, parsable format."""
    for p in posts:
        print(f"{p.id}\t{p.thumbnail_url or ''}\t{p.page_url}")

def cmd_search(args):
    """Handler for the 'search' command."""
    with Rule34Client() as client:
        posts = client.search_posts(args.tags.split(), page=args.page, per_page=args.limit)
        _print_post_list(posts[:args.limit])

def cmd_random(args):
    """Handler for the 'random' command (single post)."""
    with Rule34Client() as client:
        post = client.random_post(args.tags.split())
        _print_post_json(post)
        if args.open and post.image_url:
            webbrowser.open(post.image_url)

def cmd_random_posts(args):
    """Handler for the new 'random-posts' command."""
    with Rule34Client() as client:
        posts = client.random_posts(args.tags.split(), count=args.count)
        _print_post_list(posts)

def cmd_autocomplete(args):
    """Handler for the 'autocomplete' command."""
    with Rule34Client() as client:
        tags = client.autocomplete(args.prefix, limit=args.limit)
        for t in tags:
            print(f"{t.name}\t{t.count}")

def cmd_download(args):
    """Handler for the 'download' command."""
    with Rule34Client() as client:
        path = client.download(args.id, args.out)
        print(f"Downloaded to: {os.path.abspath(path)}")
        if args.open:
            webbrowser.open(f"file://{os.path.abspath(path)}")

def main(argv=None):
    parser = argparse.ArgumentParser(prog="r34", description="A CLI for rule34.xxx using the rule34html library.")
    sub = parser.add_subparsers(required=True, dest="command")

    # Search command
    p_search = sub.add_parser("search", help="Search posts by tags")
    p_search.add_argument("tags", type=str, help="Space-separated tags (use underscores for multi-word tags)")
    p_search.add_argument("--page", type=int, default=0, help="Page number (0-indexed)")
    p_search.add_argument("--limit", type=int, default=10, help="How many items to list from the page")
    p_search.set_defaults(func=cmd_search)

    # Random (single) command
    p_random = sub.add_parser("random", help="Get a single random post from tags (full details)")
    p_random.add_argument("tags", type=str, help="Space-separated tags")
    p_random.add_argument("--open", action="store_true", help="Open the post image in a web browser")
    p_random.set_defaults(func=cmd_random)

    # Random Posts (multiple) command
    p_random_posts = sub.add_parser("random-posts", help="Get multiple random posts from tags (list view)")
    p_random_posts.add_argument("tags", type=str, help="Space-separated tags")
    p_random_posts.add_argument("--count", type=int, default=5, help="Number of random posts to fetch")
    p_random_posts.set_defaults(func=cmd_random_posts)

    # Autocomplete command
    p_ac = sub.add_parser("autocomplete", help="Autocomplete a tag prefix")
    p_ac.add_argument("prefix", type=str, help="The prefix of the tag to autocomplete")
    p_ac.add_argument("--limit", type=int, default=10, help="Maximum number of suggestions to return")
    p_ac.set_defaults(func=cmd_autocomplete)

    # Download command
    p_dl = sub.add_parser("download", help="Download the original file for a given post ID")
    p_dl.add_argument("--id", type=int, required=True, help="The ID of the post to download")
    p_dl.add_argument("--out", type=str, default=".", help="Output directory for the downloaded file")
    p_dl.add_argument("--open", action="store_true", help="Open the downloaded file after saving")
    p_dl.set_defaults(func=cmd_download)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()
