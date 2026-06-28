"""Command-line entry point for gdoc-cli.

The implementation is intentionally minimal for the initial scaffold. Future
work will add Google OAuth and Docs/Drive API operations behind these commands.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROLES = ("reader", "commenter", "writer")
EXPORT_FORMATS = ("pdf", "txt", "docx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gdoc",
        description="Create, update, share, and export Google Docs from the command line.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("auth", help="complete Google OAuth and save a local token")

    search_parser = subparsers.add_parser("search", help="search Google Docs")
    search_parser.add_argument("query", help="search query")

    create_parser = subparsers.add_parser("create", help="create a Google Doc")
    create_parser.add_argument("--title", required=True, help="document title")
    create_parser.add_argument("--body-file", type=Path, help="plain-text body file")

    append_parser = subparsers.add_parser("append", help="append text to a Google Doc")
    append_parser.add_argument("--doc-id", required=True, help="Google Doc ID")
    append_parser.add_argument("--body-file", required=True, type=Path, help="plain-text body file")

    share_parser = subparsers.add_parser("share", help="share a Google Doc")
    share_parser.add_argument("--doc-id", required=True, help="Google Doc ID")
    share_parser.add_argument("--email", required=True, help="recipient email address")
    share_parser.add_argument("--role", required=True, choices=ROLES, help="permission role")

    export_parser = subparsers.add_parser("export", help="export a Google Doc")
    export_parser.add_argument("--doc-id", required=True, help="Google Doc ID")
    export_parser.add_argument("--format", required=True, choices=EXPORT_FORMATS, help="export format")
    export_parser.add_argument("--output", required=True, type=Path, help="output file path")

    open_parser = subparsers.add_parser("open", help="print a Google Docs browser URL")
    open_parser.add_argument("--doc-id", required=True, help="Google Doc ID")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "open":
        print(f"https://docs.google.com/document/d/{args.doc_id}/edit")
        return 0

    parser.error(f"{args.command!r} is planned but not implemented yet")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
