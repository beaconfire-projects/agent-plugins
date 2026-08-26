# Authsome MGT MCP Claude Code Plugin

This private Claude Code plugin connects to the existing Authsome MGT MCP server over Streamable HTTP and lets Claude Code authenticate with OAuth.

The plugin does **not** start a local copy of the Python server. The MCP server must already be deployed at a stable HTTPS URL.

## Local test

From the repository root:

```bash
claude --plugin-dir ./plugins/mcp-oauth-test
```

The plugin is preconfigured with the development MCP endpoint:

```text
https://api-mcp-oauth-dev.beaconfireinc.com/mcp
```

Open the MCP panel and choose **Authenticate** for `authsome-mgt` if OAuth is required.

## Private team distribution

This repository root is a private marketplace. From a trusted checkout, add it to Claude Code:

```text
/plugin marketplace add /path/to/mcp-oauth-test
/plugin install mcp-oauth-test@authsome-internal
```

The marketplace should remain in the company's private GitHub repository. Do not submit it to a public marketplace.

## Server requirements

The configured endpoint must:

- use HTTPS in shared environments;
- expose the Streamable HTTP MCP endpoint at `/mcp`;
- expose OAuth protected-resource metadata and return a usable `WWW-Authenticate` challenge;
- use the FastMCP OIDC proxy's fixed upstream IdP callback, `${BASE_URL}/auth/callback`;
- restrict access to authorized company users in the IdP and MCP server.

The company IdP should register only the fixed FastMCP callback. Claude Code's OAuth callback is handled by the MCP client and must not be added as a per-user redirect URI in the upstream IdP.

## Configuration and secrets

The MCP endpoint is fixed in `.mcp.json` and intentionally points to the development environment. OAuth tokens are managed by Claude Code. Never put client secrets, access tokens, or employee credentials in `.mcp.json` or this repository.
