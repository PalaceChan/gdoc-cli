# AGENTS.md

## Repository purpose

This repo contains a small Python CLI for Google Docs workflows: authenticate, search docs, create docs, append content, share docs, export docs, and print browser URLs.

The CLI should pair cleanly with a separate skill file by exposing predictable, scriptable commands with clear JSON or plain-text output.

## Important files

- `gdoc_cli/main.py` — command-line entry point and argument parsing.
- `scripts/gdoc` — local wrapper intended to be symlinked into `~/.local/bin/gdoc`.
- `requirements.txt` — Python dependencies for the local virtual environment.
- `README.md` — short install and usage overview.

## Design goals

- Keep v1 small and practical.
- Prefer explicit document IDs for mutating operations.
- Make commands safe for assistant use: predictable flags, non-interactive operation after auth, and useful exit codes.
- Keep credentials outside the repository, under `~/.config/gdoc-cli/`.
- Never log or commit OAuth client secrets, refresh tokens, or access tokens.

## Planned command surface

- `gdoc auth`
- `gdoc search QUERY`
- `gdoc create --title TITLE --body-file FILE`
- `gdoc append --doc-id DOC_ID --body-file FILE`
- `gdoc share --doc-id DOC_ID --email EMAIL --role reader|commenter|writer`
- `gdoc export --doc-id DOC_ID --format pdf --output FILE`
- `gdoc open --doc-id DOC_ID`

If this surface changes, update both `README.md` and the future `SKILL.md` together.

## Implementation notes

- Use Google API client libraries instead of hand-rolled OAuth.
- Store config/token paths in one small helper so they are easy to audit.
- Prefer deterministic, parseable output for commands that a skill will consume.
- Confirm destructive or externally visible operations at the skill layer, not by adding interactive prompts to the CLI.

## Testing

For now, keep tests lightweight and avoid real Google API calls by default. Future tests should mock Google client services and focus on request construction, argument validation, and output formatting.
