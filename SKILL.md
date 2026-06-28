---
name: gdoc
description: "Manage native Google Docs with the gdoc CLI: authenticate, search, inspect, create, append, share, export, and print document URLs."
metadata:
  version: "1.0"
---

# gdoc skill

Use the `gdoc` CLI for native Google Docs workflows: finding docs, creating docs, appending plain text, sharing with specific people, exporting files, and returning browser URLs.

The CLI help is the command source of truth. Before using an unfamiliar command or option, check:

```bash
gdoc --help
gdoc COMMAND --help
```

## Setup checks

1. Verify the command works:

   ```bash
   command -v gdoc && gdoc --help
   ```

2. Verify OAuth without printing secrets:

   ```bash
   gdoc auth --status
   ```

3. If auth is missing, invalid, or missing required scopes, ask the user to run:

   ```bash
   gdoc auth
   ```

   OAuth files should stay outside the repo under `~/.config/gdoc-cli/`. Never print or commit `oauth_client.json`, `token.json`, refresh tokens, access tokens, client secrets, or browser OAuth URLs containing sensitive codes.

## Operating rules

- Prefer document IDs for mutating operations. Use `gdoc search`, `gdoc info`, and `gdoc permissions` to resolve ambiguity before changing or sharing a doc.
- Treat `gdoc search`, `gdoc info`, `gdoc permissions`, `gdoc open`, and `gdoc export` as read-only or local-output operations.
- Treat `gdoc create`, `gdoc append`, and `gdoc share` as externally visible or persistent changes.
- Before `create`, `append`, or `share`, summarize the exact action and get the user's explicit confirmation unless the user already gave clear, specific instructions in the same request.
- Before sharing, confirm the document identity, recipient email, and role (`reader`, `commenter`, or `writer`).
- After any mutation, verify with a read-only command such as `gdoc info`, `gdoc permissions`, or `gdoc search`.
- Use temporary body files for generated text. Keep them outside the repo unless the user explicitly asks to save project artifacts.
- Remember content is plain text in v1. Do not promise rich Markdown formatting unless the CLI gains that capability.

## Recommended workflows

### Find and inspect a doc

```bash
gdoc search "query" --limit 5
gdoc info --doc-id DOC_ID
gdoc permissions --doc-id DOC_ID
```

Use search results to disambiguate with the user when multiple docs match.

### Create a doc from text

1. Write the intended plain-text body to a temporary file.
2. Confirm title/body summary if the user has not already been explicit.
3. Create the doc:

   ```bash
   gdoc create --title "Title" --body-file /tmp/body.txt
   ```

4. Return the created document URL from the JSON output.

### Append to an existing doc

1. Resolve the doc ID with `search`/`info` if needed.
2. Write append text to a temporary file.
3. Confirm the target doc and append summary.
4. Run `gdoc append --doc-id DOC_ID --body-file /tmp/body.txt`.
5. Verify with `gdoc info --doc-id DOC_ID`.

### Share a doc

1. Resolve and confirm the doc ID.
2. Confirm recipient email and role.
3. Run `gdoc share --doc-id DOC_ID --email EMAIL --role ROLE`.
4. Verify with `gdoc permissions --doc-id DOC_ID`.

### Export a doc

Use an explicit output path whose parent directory already exists:

```bash
gdoc export --doc-id DOC_ID --format pdf --output /tmp/doc.pdf
```

Then report the local output path and byte count from the JSON response.

## Troubleshooting

- `gdoc: command not found`: local install/symlink is missing; check the project README.
- `Not authenticated with required scopes`: run `gdoc auth` and complete browser OAuth.
- Empty search results: try a more specific title query, `--full-text`, or ask the user for the document URL/ID.
- Permission/share errors: verify the authenticated account owns or can share the doc with `gdoc info` and `gdoc permissions`.
- Export errors: verify the doc ID, requested format, and that the output parent directory exists.
