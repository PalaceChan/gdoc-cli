[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# gdoc-cli

A small Python CLI for creating, searching, updating, sharing, and exporting Google Docs from the command line.

This project is intended to support a simple skill-driven workflow for native Google Docs operations, not general Google Drive sync.

## Planned commands

- `gdoc auth` — complete Google OAuth and save a local token
- `gdoc search QUERY` — find Google Docs by title/text query
- `gdoc create --title TITLE --body-file FILE` — create a Google Doc
- `gdoc append --doc-id DOC_ID --body-file FILE` — append text to an existing doc
- `gdoc share --doc-id DOC_ID --email EMAIL --role reader|commenter|writer` — share a doc
- `gdoc export --doc-id DOC_ID --format pdf --output FILE` — export a doc
- `gdoc open --doc-id DOC_ID` — print the browser URL

## Install locally

```bash
python -m venv ~/.local/venvs/gdoc-cli
~/.local/venvs/gdoc-cli/bin/pip install -r ~/development/gdoc-cli/requirements.txt
ln -sf ~/development/gdoc-cli/scripts/gdoc ~/.local/bin/gdoc
```

Make sure `~/.local/bin` is on `PATH`, then verify:

```bash
gdoc --help
```

## OAuth setup

Create a Google OAuth Desktop client with access to the Google Docs API and Google Drive API. Save the downloaded client JSON here:

```text
~/.config/gdoc-cli/oauth_client.json
```

Then run:

```bash
gdoc auth
```

The resulting token is saved here:

```text
~/.config/gdoc-cli/token.json
```

Check setup without printing secrets:

```bash
gdoc auth --status
```

Do not commit OAuth client secrets or tokens.

## License

MIT
