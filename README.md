# Beaconfireinc Agent Plugins

Beaconfireinc 内部 Claude Code 插件市场，当前提供以下插件：

- `mgt`：连接 Beaconfireinc MGT MCP 服务并通过 OAuth 完成认证。
- `crm-reminder-dev`：连接 Beaconfireinc CRM Copilot 开发环境，用于 CRM 客户查询、客户更新和提醒管理。
- `crm-copilot`：连接 Beaconfireinc CRM Copilot V3 QA MCP 服务，按 V3 流程处理客户、关系、地址、组织、提醒、推荐和证据。
- `marketing-data-warehouse`：连接 Beaconfireinc Marketing Data Warehouse MCP 服务。

- GitHub：<https://github.com/beaconfire-projects/agent-plugins>
- Marketplace：`beaconfireinc`
- 当前插件：`mgt`、`crm-reminder-dev`、`crm-copilot`、`marketing-data-warehouse`
- MGT MCP endpoint：`https://api-mcp-oauth-dev.beaconfireinc.com/mcp`
- Marketing Data Warehouse MCP endpoint：`https://marketing-data-warehouse-dev.beaconfireinc.com/mcp`

> 本仓库及插件面向内部使用，请勿提交到公开插件市场，也不要在仓库中保存密钥、Token 或员工凭据。

## 前置条件

- 已安装并登录 [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- 拥有 Beaconfireinc MGT MCP 服务的访问权限
- 能够访问公司的 OAuth / IdP 服务

## 使用方式

### 方式一：从 GitHub 添加 Marketplace

在 Claude Code 中执行：

```text
/plugin marketplace add https://github.com/beaconfire-projects/agent-plugins
/plugin install mgt@beaconfireinc
```

安装后重启 Claude Code，或按照 Claude Code 的提示重新加载插件。

### 方式二：从本地仓库加载

```bash
git clone https://github.com/beaconfire-projects/agent-plugins.git
cd agent-plugins
claude --plugin-dir ./plugins/mgt
```

也可以在 Claude Code 中添加本地 Marketplace：

```text
/plugin marketplace add /path/to/agent-plugins
/plugin install mgt@beaconfireinc
```

### 安装 Marketing Data Warehouse 插件

```text
/plugin install marketing-data-warehouse@beaconfireinc
```

本地加载：

```bash
claude --plugin-dir ./plugins/marketing-data-warehouse
```

插件包含 `interview-question-search` skill，连接 `marketing-data-warehouse` MCP 服务。

### 完成 OAuth 认证

1. 打开 Claude Code 的 MCP 面板。
2. 找到 `mgt` 服务。
3. 选择 **Authenticate**。
4. 在浏览器中完成公司的 OAuth 登录和授权。
5. 返回 Claude Code 后即可使用 MGT MCP 工具。

OAuth Token 由 Claude Code 管理，无需手动填写到配置文件中。

### CRM Reminder Dev 认证

`crm-reminder-dev` 使用 OAuth。安装后在 Claude Code 的 MCP 面板中选择 `crm-reminder-dev`，点击 **Authenticate**，并在浏览器中完成公司 OAuth 授权。OAuth Token 由 Claude Code 管理，绝不能提交到仓库。

### CRM Copilot V3 认证

`crm-copilot` 使用 OAuth，连接 QA MCP：

```text
https://api-crm-mcp-dev.beaconfireinc.com/mcp
```

安装后在 Claude Code 的 MCP 面板中选择 `crm-copilot`，点击 **Authenticate**，并在浏览器中完成 AuthSome OAuth 授权。OAuth Token 由 Claude Code 管理，绝不能提交到仓库。

安装命令：

```text
/plugin install crm-copilot@beaconfireinc
```

## 本地配置

Marketing Data Warehouse 插件配置位于：

```text
plugins/marketing-data-warehouse/.mcp.json
```

```text
https://marketing-data-warehouse-dev.beaconfireinc.com/mcp
```

MGT 插件配置位于：

```text
plugins/mgt/.mcp.json
```

当前默认连接开发环境：

```text
https://api-mcp-oauth-dev.beaconfireinc.com/mcp
```

该 MCP 服务需要：

- 使用 HTTPS；
- 在 `/mcp` 暴露 Streamable HTTP MCP endpoint；
- 提供 OAuth protected-resource metadata 和有效的 `WWW-Authenticate` challenge；
- 配置固定的 FastMCP OIDC proxy 回调：`${BASE_URL}/auth/callback`。

如需切换环境，请先确认目标环境和 OAuth 配置，再修改 `.mcp.json`，不要提交任何敏感信息。

## 故障排查

- **找不到 Marketplace**：确认仓库地址或本地路径可访问，并检查是否拥有私有仓库权限。
- **找不到插件**：确认已执行 `/plugin install mgt@beaconfireinc`，并重新加载 Claude Code。
- **认证失败**：确认账号已获授权，并检查 MCP 服务是否返回正确的 OAuth 元数据和 `WWW-Authenticate` challenge。
- **连接失败**：确认网络可以访问 `api-mcp-oauth-dev.beaconfireinc.com`，以及 endpoint 地址为 `/mcp`。

更多插件专属说明请参阅 [`plugins/mgt/README.md`](plugins/mgt/README.md)。
