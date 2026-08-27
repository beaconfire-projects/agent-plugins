# Beaconfireinc Marketing Data Warehouse MCP Claude Code Plugin

This private Claude Code plugin connects to the Beaconfireinc Marketing Data Warehouse MCP server over Streamable HTTP.

## Bundled skill

The `interview-question-search` skill documents how to search interview questions, candidates, vendors, clients, interview rounds, and technologies through the Marketing Data Warehouse MCP connector.

## Bundled agent

The `interview-question-analyst` agent is a specialist subagent scoped to the ten connector tools. Delegate interview-data requests to it for searches, candidate histories, question-frequency analysis, and confirmed Excel exports with honest coverage reporting.

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
