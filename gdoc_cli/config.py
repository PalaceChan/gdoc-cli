"""Configuration paths for gdoc-cli.

All runtime credentials live outside the repository under ``~/.config/gdoc-cli``.
"""

from __future__ import annotations

from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "gdoc-cli"
OAUTH_CLIENT_FILE = CONFIG_DIR / "oauth_client.json"
TOKEN_FILE = CONFIG_DIR / "token.json"


def ensure_config_dir() -> Path:
    """Create and return the gdoc-cli config directory."""
    CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        CONFIG_DIR.chmod(0o700)
    except PermissionError:
        # Best effort only; commands will still fail later if permissions block use.
        pass
    return CONFIG_DIR
