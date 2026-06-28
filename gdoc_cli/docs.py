"""Google Docs API operations for gdoc-cli."""

from __future__ import annotations

from pathlib import Path

from googleapiclient.discovery import build

from gdoc_cli.auth import get_credentials
from gdoc_cli.drive import DOCS_MIME_TYPE, DOC_URL_TEMPLATE, drive_service


def docs_service():
    """Build an authenticated Google Docs API service."""
    return build("docs", "v1", credentials=get_credentials(), cache_discovery=False)


def read_body_file(path: Path | None) -> str:
    """Read a UTF-8 body file, returning an empty string when omitted."""
    if path is None:
        return ""
    return path.read_text(encoding="utf-8")


def create_doc(title: str, body: str = "") -> dict[str, str]:
    """Create a Google Doc and optionally insert plain text at the start."""
    document = docs_service().documents().create(body={"title": title}).execute()
    doc_id = document["documentId"]

    if body:
        docs_service().documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": body,
                        }
                    }
                ]
            },
        ).execute()

    # Fetch Drive metadata so output is consistent with search results and uses
    # Drive's canonical webViewLink when available.
    metadata = (
        drive_service()
        .files()
        .get(fileId=doc_id, fields="id,name,mimeType,modifiedTime,webViewLink")
        .execute()
    )

    return {
        "id": doc_id,
        "name": metadata.get("name", title),
        "url": metadata.get("webViewLink") or DOC_URL_TEMPLATE.format(doc_id=doc_id),
        "mimeType": metadata.get("mimeType", DOCS_MIME_TYPE),
        "modifiedTime": metadata.get("modifiedTime", ""),
    }
