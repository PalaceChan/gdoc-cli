"""Google Drive API operations for gdoc-cli."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from googleapiclient.discovery import build

from gdoc_cli.auth import get_credentials


DOCS_MIME_TYPE = "application/vnd.google-apps.document"
DOC_URL_TEMPLATE = "https://docs.google.com/document/d/{doc_id}/edit"
EXPORT_MIME_TYPES = {
    "pdf": "application/pdf",
    "txt": "text/plain",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def drive_service():
    """Build an authenticated Google Drive API service."""
    return build("drive", "v3", credentials=get_credentials(), cache_discovery=False)


def _escape_drive_query_value(value: str) -> str:
    """Escape a string literal for use in a Drive query."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def doc_url(doc_id: str) -> str:
    """Return the standard Google Docs edit URL for a document ID."""
    return DOC_URL_TEMPLATE.format(doc_id=doc_id)


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


def share_doc(doc_id: str, email: str, role: str) -> dict[str, str]:
    """Share a Google Doc with a user email address."""
    permission = (
        drive_service()
        .permissions()
        .create(
            fileId=doc_id,
            body={
                "type": "user",
                "role": role,
                "emailAddress": email,
            },
            sendNotificationEmail=True,
            fields="id,emailAddress,role,type",
        )
        .execute()
    )
    return {
        "doc_id": doc_id,
        "email": permission.get("emailAddress", email),
        "role": permission.get("role", role),
        "permission_id": permission.get("id", ""),
        "url": doc_url(doc_id),
    }


def export_doc(doc_id: str, export_format: str, output: Path) -> dict[str, object]:
    """Export a Google Doc to a local file."""
    mime_type = EXPORT_MIME_TYPES[export_format]
    data = drive_service().files().export(fileId=doc_id, mimeType=mime_type).execute()
    output.write_bytes(data)
    return {
        "doc_id": doc_id,
        "format": export_format,
        "mime_type": mime_type,
        "output": str(output),
        "bytes": len(data),
    }


def print_jsonl(rows: Iterable[dict[str, object]]) -> None:
    """Print dictionaries as JSON Lines."""
    for row in rows:
        print(json.dumps(row, sort_keys=True, ensure_ascii=False))
