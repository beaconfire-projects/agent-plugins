# Beaconfireinc Marketing Data Warehouse MCP Claude Code Plugin

This private Claude Code plugin connects to the Beaconfireinc Marketing Data Warehouse MCP server over Streamable HTTP.

## Bundled skill

The `interview-question-search` skill searches interview questions, candidates, vendors, clients, rounds and technologies through the Marketing Data Warehouse MCP connector. Full question details also read the exact matched source Docs through the user's connected Google Drive plugin and preserve original text/image order in chat. This does not require warehouse image-reference backfill.

## Bundled agent

The `interview-question-analyst` agent is scoped to warehouse tools. Delegate discovery, histories, frequency analysis and confirmed Excel exports to it. For full details it returns source IDs/text to the caller, which uses Google Drive for source images and reports image coverage separately.

## Original images in full question details

Follow `skills/interview-question-search/references/source-images.md`. Python 3's standard-library helper archives original image bytes to `~/Documents/interview-question-archives/<run-id>/`, emits source-ordered Markdown with absolute image paths, and records coverage without storing temporary Google image URLs. Saving is local; no Drive files are created or shared. Files remain viewable on the same computer while the archive exists.

The Google Drive plugin must be available and authorized for the matched documents. Missing access, unsupported objects and download limits leave explicit placeholders; text-only results must not be labelled complete. The output preserves reading order and table cell boundaries, not Google Docs pagination or floating-image coordinates. Visual inspection in the final Codex conversation is required to verify display.

Run offline tests from this plugin directory:

```sh
python3 -B -m unittest discover -s skills/interview-question-search/tests -v
```

## Export delivery

Excel exports are delivered per the server's `EXPORT_MODE`: the deployed HTTP server (`EXPORT_MODE=drive`) uploads the workbook to the shared Drive folder `Interview Question Exports`, names it `{user_name}_{YYYY-MM-DD_HHmm}.xlsx` after the caller, and returns a `web_view_link`; a locally-run stdio server (`EXPORT_MODE=local`) writes `~/Downloads/question_bank/` with the confirm flow. The skill and agent teach the model to read the response rather than assume a mode.

## Local test

From the repository root:

```bash
claude --plugin-dir ./plugins/marketing-data-warehouse
```

The plugin is configured with the production MCP endpoint:

```text
https://marketing-data-warehouse.beaconfireinc.com/mcp
```

Open the MCP panel and authenticate `marketing-data-warehouse` if authentication is required.

## Configuration and secrets

The MCP endpoint is fixed in `.mcp.json`. OAuth tokens or other credentials must not be stored in this repository.
