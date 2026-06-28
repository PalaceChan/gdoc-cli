"""Command-line entry point for gdoc-cli."""

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
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Create, inspect, update, share, and export native Google Docs.",
        epilog=(
            "Output conventions:\n"
            "  - Commands that return one object print JSON.\n"
            "  - Commands that return multiple rows print JSON Lines.\n"
            "  - OAuth client secrets and tokens are read from ~/.config/gdoc-cli/ and never printed.\n\n"
            "Common workflow:\n"
            "  gdoc auth --status\n"
            "  gdoc search \"meeting notes\" --limit 5\n"
            "  gdoc create --title \"Meeting Notes\" --body-file notes.txt\n"
            "  gdoc share --doc-id DOC_ID --email person@example.com --role reader\n"
            "  gdoc info --doc-id DOC_ID\n\n"
            "Run `gdoc COMMAND --help` for command-specific examples and output details."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_parser = subparsers.add_parser(
        "auth",
        help="complete Google OAuth or print auth status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Complete browser-based Google OAuth and save a local token.\n\n"
            f"Before first use, save the downloaded OAuth Desktop client JSON at:\n  {OAUTH_CLIENT_FILE}\n\n"
            f"The resulting token is saved at:\n  {TOKEN_FILE}\n\n"
            "The status command prints only secret-free metadata."
        ),
        epilog=(
            "Examples:\n"
            "  gdoc auth --status\n"
            "  gdoc auth"
        ),
    )
    auth_parser.add_argument("--status", action="store_true", help="print secret-free auth status and exit")

    search_parser = subparsers.add_parser(
        "search",
        help="search Google Docs by title or full text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Search Google Docs visible to the authenticated account.\n\n"
            "By default, searches document titles. Use --full-text to ask Drive to search document contents.\n"
            "Prints one JSON object per line with id, name, url, mimeType, and modifiedTime."
        ),
        epilog=(
            "Examples:\n"
            "  gdoc search \"meeting notes\"\n"
            "  gdoc search \"proposal\" --limit 5\n"
            "  gdoc search \"action item\" --full-text --limit 5"
        ),
    )
    search_parser.add_argument("query", help="search query")
    search_parser.add_argument("--limit", type=int, default=20, help="maximum results to return")
    search_parser.add_argument("--full-text", action="store_true", help="search document contents instead of titles")

    info_parser = subparsers.add_parser(
        "info",
        help="print Google Doc metadata as JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Print one JSON object with basic document metadata and owner information.",
        epilog="Example:\n  gdoc info --doc-id DOC_ID",
    )
    info_parser.add_argument("--doc-id", required=True, help="Google Doc ID")

    permissions_parser = subparsers.add_parser(
        "permissions",
        help="print Google Doc permissions as JSON Lines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Print non-secret permissions for a document.\n"
            "Each permission is printed as one JSON object per line."
        ),
        epilog="Example:\n  gdoc permissions --doc-id DOC_ID",
    )
    permissions_parser.add_argument("--doc-id", required=True, help="Google Doc ID")

    create_parser = subparsers.add_parser(
        "create",
        help="create a Google Doc and optionally insert plain text",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Create a native Google Doc. If --body-file is provided, its UTF-8 text is inserted as plain text.\n"
            "Prints one JSON object with id, name, url, mimeType, and modifiedTime."
        ),
        epilog=(
            "Examples:\n"
            "  gdoc create --title \"Meeting Notes\"\n"
            "  gdoc create --title \"Meeting Notes\" --body-file notes.txt"
        ),
    )
    create_parser.add_argument("--title", required=True, help="document title")
    create_parser.add_argument("--body-file", type=Path, help="UTF-8 plain-text body file")

    append_parser = subparsers.add_parser(
        "append",
        help="append plain text to a Google Doc",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Append a UTF-8 plain-text file to the end of an existing Google Doc.\n"
            "Prints one JSON object with id, url, and appended_chars."
        ),
        epilog="Example:\n  gdoc append --doc-id DOC_ID --body-file notes.txt",
    )
    append_parser.add_argument("--doc-id", required=True, help="Google Doc ID")
    append_parser.add_argument("--body-file", required=True, type=Path, help="UTF-8 plain-text body file")

    share_parser = subparsers.add_parser(
        "share",
        help="share a Google Doc with a user",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Create or update a user permission for a Google Doc and send Google's normal sharing notification.\n"
            "Prints one JSON object with doc_id, email, role, permission_id, and url.\n\n"
            "Roles:\n"
            "  reader     view only\n"
            "  commenter  comment access\n"
            "  writer     edit access"
        ),
        epilog=(
            "Examples:\n"
            "  gdoc share --doc-id DOC_ID --email person@example.com --role reader\n"
            "  gdoc share --doc-id DOC_ID --email person@example.com --role writer"
        ),
    )
    share_parser.add_argument("--doc-id", required=True, help="Google Doc ID")
    share_parser.add_argument("--email", required=True, help="recipient email address")
    share_parser.add_argument("--role", required=True, choices=ROLES, help="permission role")

    export_parser = subparsers.add_parser(
        "export",
        help="export a Google Doc to a local file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Export a native Google Doc to a local file. The output parent directory must already exist.\n"
            "Prints one JSON object with doc_id, format, mime_type, output, and bytes."
        ),
        epilog=(
            "Examples:\n"
            "  gdoc export --doc-id DOC_ID --format pdf --output doc.pdf\n"
            "  gdoc export --doc-id DOC_ID --format txt --output doc.txt\n"
            "  gdoc export --doc-id DOC_ID --format docx --output doc.docx"
        ),
    )
    export_parser.add_argument("--doc-id", required=True, help="Google Doc ID")
    export_parser.add_argument("--format", required=True, choices=EXPORT_FORMATS, help="export format")
    export_parser.add_argument("--output", required=True, type=Path, help="output file path")

    open_parser = subparsers.add_parser(
        "open",
        help="print a Google Docs browser URL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Print the standard Google Docs edit URL for a document ID.",
        epilog="Example:\n  gdoc open --doc-id DOC_ID",
    )
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
