[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# gdoc-cli

A small Python CLI for creating, searching, updating, sharing, and exporting Google Docs from the command line.

This project is intended to support a simple skill-driven workflow for native Google Docs operations, not general Google Drive sync.

## Planned commands

- `gdoc auth` — complete Google OAuth and save a local token
- `gdoc search QUERY` — find Google Docs by title and print JSON Lines
- `gdoc info --doc-id DOC_ID` — print Google Doc metadata as JSON
- `gdoc permissions --doc-id DOC_ID` — print Google Doc permissions as JSON Lines
- `gdoc create --title TITLE --body-file FILE` — create a Google Doc and print JSON
- `gdoc append --doc-id DOC_ID --body-file FILE` — append plain text to an existing doc and print JSON
- `gdoc share --doc-id DOC_ID --email EMAIL --role reader|commenter|writer` — share a doc and print JSON
- `gdoc export --doc-id DOC_ID --format pdf|txt|docx --output FILE` — export a doc and print JSON
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

## Skill

`SKILL.md` contains concise agent usage guidance. Keep command details in `gdoc --help` and subcommand help to avoid documentation drift.

## OAuth setup

Create a Google OAuth Desktop client with access to the Google Docs API and Google Drive API. The CLI requests Docs access, app-file Drive access, and read-only Drive access for searching/exporting existing docs. Save the downloaded client JSON here:

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

## Search docs

```bash
gdoc search "meeting notes"
gdoc search "proposal" --limit 5
gdoc search "action item" --full-text --limit 5
```

By default, search matches document titles. Use `--full-text` to ask Drive to search document contents instead. Each result is printed as one JSON object per line with the document ID, name, URL, MIME type, and modified time.

## Inspect docs

```bash
gdoc info --doc-id DOC_ID
gdoc permissions --doc-id DOC_ID
```

`info` prints one JSON object with document metadata. `permissions` prints one JSON object per line with non-secret permission fields.

## Create docs

```bash
gdoc create --title "Meeting Notes" --body-file notes.txt
```

The body file is inserted as plain text. The command prints one JSON object with the created document ID, name, URL, MIME type, and modified time.

## Share docs

```bash
gdoc share --doc-id DOC_ID --email person@example.com --role reader
gdoc share --doc-id DOC_ID --email person@example.com --role commenter
gdoc share --doc-id DOC_ID --email person@example.com --role writer
```

The command sends Google's normal sharing notification and prints one JSON object with the document ID, recipient email, role, permission ID, and URL.

## Append to docs

```bash
gdoc append --doc-id DOC_ID --body-file notes.txt
```

The body file is appended as plain text. The command prints one JSON object with the document ID, URL, and appended character count.

## Export docs

```bash
gdoc export --doc-id DOC_ID --format pdf --output doc.pdf
gdoc export --doc-id DOC_ID --format txt --output doc.txt
gdoc export --doc-id DOC_ID --format docx --output doc.docx
```

The output parent directory must already exist. The command prints one JSON object with the document ID, format, MIME type, output path, and byte count.

## License

MIT
