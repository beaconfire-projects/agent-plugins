# 操作规范

## 远程仓库

本仓库有两个远程仓库：

1. **dev 仓库** https://github.com/beaconfire-projects/agent-plugins.git — public，给 Claude 个人账号使用
2. **private 仓库** https://github.com/beaconfire-projects/beaconfire-agent-plugins.git — private，给 Claude 团队账号使用

## 项目命名

`xxx-dev` 的插件通常是给开发调试使用的，其对应的发布版本插件为 `xxx`。

## 插件版本管理

修改任何插件内容之后，必须同步提升该插件的版本号。

- 版本号位于各插件的 `plugins/<plugin-name>/.claude-plugin/plugin.json` 的 `version` 字段。
- 任何对插件内容的改动都算数：skills、agents、commands、hooks、`.mcp.json`、README 等。
- 版本号遵循语义化版本（semver）：
  - 新增功能 / 新 skill / 新 agent → minor（如 `0.2.1` → `0.3.0`）
  - 修复、措辞调整、小幅改动 → patch（如 `0.2.1` → `0.2.2`）
  - 不兼容的结构变更 → major
- 提交前检查：`git diff` 中只要包含某插件目录下的文件，`plugin.json` 的 `version` 就必须在同一提交中被提升。
