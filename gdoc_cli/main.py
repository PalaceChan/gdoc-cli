"""Command-line entry point for gdoc-cli.

The implementation is intentionally minimal for the initial scaffold. Future
work will add Google OAuth and Docs/Drive API operations behind these commands.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from gdoc_cli.auth import get_credentials, print_auth_status
from gdoc_cli.config import OAUTH_CLIENT_FILE, TOKEN_FILE
from gdoc_cli.docs import append_doc, create_doc, read_body_file
from gdoc_cli.drive import doc_info, doc_permissions, export_doc, print_jsonl, search_docs, share_doc


ROLES = ("reader", "commenter", "writer")
EXPORT_FORMATS = ("pdf", "txt", "docx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gdoc",
        description="Create, update, share, and export Google Docs from the command line.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser(
        "auth",
        help="complete Google OAuth and save a local token",
        description=(
            "Complete browser-based Google OAuth. Save the downloaded OAuth "
            f"Desktop client JSON at {OAUTH_CLIENT_FILE} before running this command. "
            f"The resulting token is saved at {TOKEN_FILE}."
        ),
    )
    auth_parser.add_argument("--status", action="store_true", help="print secret-free auth status and exit")

    search_parser = subparsers.add_parser("search", help="search Google Docs")
    search_parser.add_argument("query", help="search query")
    search_parser.add_argument("--limit", type=int, default=20, help="maximum results to return")
    search_parser.add_argument("--full-text", action="store_true", help="search document contents instead of titles")

    info_parser = subparsers.add_parser("info", help="print Google Doc metadata as JSON")
    info_parser.add_argument("--doc-id", required=True, help="Google Doc ID")

    permissions_parser = subparsers.add_parser("permissions", help="print Google Doc permissions as JSON Lines")
    permissions_parser.add_argument("--doc-id", required=True, help="Google Doc ID")

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

    if args.command == "auth":
        if args.status:
            print_auth_status()
            return 0
        get_credentials(allow_browser=True)
        print(f"Authenticated. Token saved to {TOKEN_FILE}")
        return 0

    if args.command == "search":
        if args.limit < 1:
            parser.error("--limit must be at least 1")
        print_jsonl(search_docs(args.query, page_size=args.limit, full_text=args.full_text))
        return 0

    if args.command == "info":
        print(json.dumps(doc_info(args.doc_id), sort_keys=True, ensure_ascii=False))
        return 0

    if args.command == "permissions":
        print_jsonl(doc_permissions(args.doc_id))
        return 0

    if args.command == "create":
        if args.body_file and not args.body_file.is_file():
            parser.error(f"--body-file does not exist or is not a file: {args.body_file}")
        body = read_body_file(args.body_file)
        print(json.dumps(create_doc(args.title, body), sort_keys=True, ensure_ascii=False))
        return 0

    if args.command == "share":
        print(json.dumps(share_doc(args.doc_id, args.email, args.role), sort_keys=True, ensure_ascii=False))
        return 0

    if args.command == "append":
        if not args.body_file.is_file():
            parser.error(f"--body-file does not exist or is not a file: {args.body_file}")
        body = read_body_file(args.body_file)
        print(json.dumps(append_doc(args.doc_id, body), sort_keys=True, ensure_ascii=False))
        return 0

    if args.command == "export":
        if args.output.exists() and args.output.is_dir():
            parser.error(f"--output is a directory: {args.output}")
        if not args.output.parent.exists():
            parser.error(f"output parent directory does not exist: {args.output.parent}")
        print(json.dumps(export_doc(args.doc_id, args.format, args.output), sort_keys=True, ensure_ascii=False))
        return 0

    if args.command == "open":
        print(f"https://docs.google.com/document/d/{args.doc_id}/edit")
        return 0

    parser.error(f"{args.command!r} is planned but not implemented yet")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
