# Beaconfireinc CRM Copilot V3 Plugin

This private Claude Code plugin connects to the Beaconfireinc CRM Copilot V3 development MCP service over Streamable HTTP. It does not start a local server and does not contain CRM credentials.

## MCP endpoint and authentication

The configured QA endpoint is:

```text
https://api-crm-mcp-dev.beaconfireinc.com/mcp
```

After installing the plugin, open Claude Code's MCP panel, select `crm-copilot`, and choose **Authenticate**. Complete the company AuthSome OAuth flow in the browser. Claude Code manages the OAuth tokens; never place client secrets, access tokens, or Authorization headers in this repository.

## Local test

From the marketplace repository root:

```bash
claude --plugin-dir ./plugins/crm-copilot
```

Use `/mcp` to confirm the server is connected, then call `server_status` before performing CRM work.

## Install from the private marketplace

```text
/plugin marketplace add https://github.com/beaconfire-projects/agent-plugins
/plugin install crm-copilot@beaconfireinc
```

Restart Claude Code or reload plugins after installation.

The bundled `crm-copilot-v3` skill is the authoritative conversation and tool-routing contract for this MCP service.

Reminder creation has two separate outcomes: the MCP service persists the
CRM reminder, then Claude's host-native notification capability is invoked for
the user-facing alert when that capability is available. The plugin reports
the CRM reminder and host notification independently; a database insert alone
is never presented as a delivered notification. `reminder_create` returns a
`hostNotification` handoff payload; on mobile, the host notification/calendar
step is mandatory and must be executed immediately after the CRM insert.
