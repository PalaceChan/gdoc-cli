"""Google Drive API operations for gdoc-cli."""

from __future__ import annotations

import json
from collections.abc import Iterable

from googleapiclient.discovery import build

from gdoc_cli.auth import get_credentials


DOCS_MIME_TYPE = "application/vnd.google-apps.document"
DOC_URL_TEMPLATE = "https://docs.google.com/document/d/{doc_id}/edit"


def drive_service():
    """Build an authenticated Google Drive API service."""
    return build("drive", "v3", credentials=get_credentials(), cache_discovery=False)


def _escape_drive_query_value(value: str) -> str:
    """Escape a string literal for use in a Drive query."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def search_docs(query: str, *, page_size: int = 20, full_text: bool = False) -> list[dict[str, str]]:
    """Search Google Docs visible to the authenticated user.

    By default, search document titles because that works with read-only Drive
    metadata scope. Pass ``full_text=True`` to ask Drive to search document
    contents too when the authenticated account/scopes support it.

    Returns dictionaries containing a small, stable, secret-free surface that is
    suitable for CLI output and assistant consumption.
    """
    safe_query = _escape_drive_query_value(query)
    search_clause = f"fullText contains '{safe_query}'" if full_text else f"name contains '{safe_query}'"
    drive_query = f"mimeType = '{DOCS_MIME_TYPE}' and trashed = false and {search_clause}"

    response = (
        drive_service()
        .files()
        .list(
            q=drive_query,
            pageSize=page_size,
            orderBy="modifiedTime desc",
            fields="files(id,name,mimeType,modifiedTime,webViewLink)",
        )
        .execute()
    )

    docs = []
    for item in response.get("files", []):
        doc_id = item["id"]
        docs.append(
            {
                "id": doc_id,
                "name": item.get("name", ""),
                "url": item.get("webViewLink") or DOC_URL_TEMPLATE.format(doc_id=doc_id),
                "mimeType": item.get("mimeType", ""),
                "modifiedTime": item.get("modifiedTime", ""),
            }
        )
    return docs


def print_jsonl(rows: Iterable[dict[str, object]]) -> None:
    """Print dictionaries as JSON Lines."""
    for row in rows:
        print(json.dumps(row, sort_keys=True, ensure_ascii=False))
