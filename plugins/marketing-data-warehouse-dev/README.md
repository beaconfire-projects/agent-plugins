# Beaconfireinc Marketing Data Warehouse MCP Claude Code Plugin

This private Claude Code plugin connects to the Beaconfireinc Marketing Data Warehouse MCP server over Streamable HTTP.

## Bundled skill

The `interview-question-search` skill documents how to search interview questions, candidates, vendors, clients, interview rounds, and technologies through the Marketing Data Warehouse MCP connector.

## Bundled agent

The `interview-question-analyst` agent is a specialist subagent scoped to the ten connector tools. Delegate interview-data requests to it for searches, candidate histories, question-frequency analysis, and confirmed Excel exports with honest coverage reporting.

## Export delivery

Excel exports are delivered per the server's `EXPORT_MODE`: the deployed HTTP server (`EXPORT_MODE=drive`) uploads the workbook to the shared Drive folder `Interview Question Exports`, names it `{user_name}_{YYYY-MM-DD_HHmm}.xlsx` after the caller, and returns a `web_view_link`; a locally-run stdio server (`EXPORT_MODE=local`) writes `~/Downloads/question_bank/` with the confirm flow. The skill and agent teach the model to read the response rather than assume a mode.

## Local test

From the repository root:

```bash
claude --plugin-dir ./plugins/marketing-data-warehouse
```

The plugin is configured with the development MCP endpoint:

```text
https://marketing-data-warehouse-dev.beaconfireinc.com/mcp
```

Open the MCP panel and authenticate `marketing-data-warehouse` if authentication is required.

## Configuration and secrets

The MCP endpoint is fixed in `.mcp.json`. OAuth tokens or other credentials must not be stored in this repository.
