# Beaconfireinc CRM Reminder Dev Plugin

This private Claude Code plugin connects to the Beaconfireinc CRM Copilot development MCP service. It installs the CRM Reminder skill for customer lookup and updates, reminder scheduling, host-agent notifications, and Google Calendar synchronization.

The plugin does not bundle the CRM Copilot service. The service is deployed at:

```text
https://api-crm-copilot-dev.beaconfireinc.com/mcp
```

## Authentication

The development MCP service uses OAuth. After installation, open Claude Code's MCP panel, select `crm-reminder-dev`, and choose **Authenticate**. Complete the company OAuth flow in the browser, then return to Claude Code.

Claude Code manages OAuth tokens. Do not add client secrets, access tokens, or employee credentials to this repository.

## Local test

From the repository root:

```bash
claude --plugin-dir ./plugins/crm-reminder-dev
```

Use `/mcp` to confirm that `crm-reminder-dev` is connected.

## Install from the Marketplace

```text
/plugin marketplace add https://github.com/beaconfire-projects/agent-plugins
/plugin install crm-reminder-dev@beaconfireinc
```

Restart Claude Code or reload plugins after installation.
