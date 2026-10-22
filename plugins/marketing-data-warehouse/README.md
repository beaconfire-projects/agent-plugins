# Beaconfireinc Marketing Data Warehouse MCP Claude Code Plugin

This private Claude Code plugin connects to the Beaconfireinc Marketing Data Warehouse MCP server over Streamable HTTP.

## Bundled skills

The `interview-question-search` skill searches interview questions, candidates, vendors, clients, rounds and technologies through the Marketing Data Warehouse MCP connector. Full question details also read the exact matched source Docs through the user's connected Google Drive plugin and preserve original text/image order in chat. This does not require warehouse image-reference backfill.

The `candidate-matching` skill covers `match_candidates` (shortlisting candidates for a job description or reference interview questions with evidence) and `ingest_resumes` (an explicitly requested admin refresh of the resume index) through the same connector.

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

Open the MCP panel and authenticate `plugin:marketing-data-warehouse:marketing-data-warehouse` if authentication is required.

## MCP environment routing

Warehouse skills bind to this plugin's `marketing-data-warehouse` server from `.mcp.json`.
Claude Code registers it as `plugin:marketing-data-warehouse:marketing-data-warehouse` and exposes tools as
`mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__<tool>`. Use `/mcp` to verify the server and
available tools after installing or reloading the plugin. A missing tool,
authorization failure or outage must not trigger fallback to the other environment
or a separately configured server with the same tool names.

The analyst agent's `tools` allowlist uses only these environment-specific tool
names. Each warehouse skill also declares its environment-specific tools in the
`allowed-tools` YAML header. This pre-approves those calls; it does not disable
other tools or remove the skill's user-confirmation requirements for refreshes
and exports. Skill routing text is not a client-wide security boundary. For hard
environment isolation, use separate client sessions/configurations or client
permission policies that exclude the other warehouse. The connected Google Drive workflow remains limited
to reading exact matched source documents, not warehouse discovery or fallback.

## Configuration and secrets

The MCP endpoint is fixed in `.mcp.json`. OAuth tokens or other credentials must not be stored in this repository.
