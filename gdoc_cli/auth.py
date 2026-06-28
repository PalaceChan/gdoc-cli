"""OAuth helpers for gdoc-cli."""

from __future__ import annotations

import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from gdoc_cli.config import OAUTH_CLIENT_FILE, TOKEN_FILE, ensure_config_dir


SCOPES = (
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
)


def credentials_exist() -> bool:
    """Return whether a saved OAuth token is present."""
    return TOKEN_FILE.exists()


def load_credentials() -> Credentials | None:
    """Load saved credentials if present."""
    if not TOKEN_FILE.exists():
        return None
    return Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)


def save_credentials(credentials: Credentials) -> None:
    """Persist credentials to the configured token file."""
    ensure_config_dir()
    TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")
    try:
        TOKEN_FILE.chmod(0o600)
    except PermissionError:
        pass


def get_credentials(*, allow_browser: bool = False) -> Credentials:
    """Return valid credentials, refreshing or running OAuth if allowed.

    Args:
        allow_browser: If true, start a browser-based OAuth flow when no valid
            refreshable token exists.

    Raises:
        FileNotFoundError: If interactive auth is requested but the OAuth client
            file does not exist.
        RuntimeError: If credentials are missing/expired and browser auth is not
            allowed.
    """
    credentials = load_credentials()

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(credentials)
        return credentials

    if not allow_browser:
        raise RuntimeError("Not authenticated. Run `gdoc auth` first.")

    if not OAUTH_CLIENT_FILE.exists():
        raise FileNotFoundError(
            f"OAuth client file not found: {OAUTH_CLIENT_FILE}\n"
            "Create a Google OAuth Desktop client and save its downloaded JSON there."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(OAUTH_CLIENT_FILE), SCOPES)
    credentials = flow.run_local_server(port=0)
    save_credentials(credentials)
    return credentials


def auth_status() -> dict[str, object]:
    """Return a small, secret-free auth status dictionary."""
    credentials = load_credentials()
    return {
        "config_dir": str(ensure_config_dir()),
        "oauth_client_file": str(OAUTH_CLIENT_FILE),
        "oauth_client_exists": OAUTH_CLIENT_FILE.exists(),
        "token_file": str(TOKEN_FILE),
        "token_exists": TOKEN_FILE.exists(),
        "token_valid": bool(credentials and credentials.valid),
        "scopes": list(SCOPES),
    }


def print_auth_status() -> None:
    """Print auth status as pretty JSON without token/client-secret contents."""
    print(json.dumps(auth_status(), indent=2, sort_keys=True))
