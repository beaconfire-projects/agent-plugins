# marketing-system

连接 Beaconfireinc Marketing System 的 MCP 服务（`https://api-marketing-mcp.beaconfireinc.com/mcp`），并提供 `staffing` Skill，用来对 Staffing（Meta Data Center 招聘流程）的数据做受控修改。目前只有生产环境（没有 dev 环境），所以只提供正式版插件 `marketing-system`。

## 安装

```text
/plugin marketplace add https://github.com/beaconfire-projects/agent-plugins
/plugin install marketing-system@beaconfireinc
```

首次使用时按提示完成 Authsome 登录。账号必须已被分配系统登记的角色，否则所有工具返回 403（`No role assigned` / `Role not allowed`）；分配角色后需要重新登录才生效。

## `staffing` Skill

按姓名、Candidate ID（`CAN-xxxxx`）、Interview 编号（`INT-xxxx`）或 Onboarding 编号（`ONB-xxxx`）处理五类请求：

| 请求 | 说明 | 参考文件 |
| --- | --- | --- |
| 修改面试时间或结果 | 改日期、时间、时区、结果（含 Need to Reschedule）、会议链接、Recruiter、备注；已取消或标了 Need to Reschedule 的面试重约会新建一条面试 | `references/interview.md` |
| 创建 Onboarding | 记录学员拿到 offer，必须有 offer 日期；已有记录时改为修改 | `references/onboarding-create.md` |
| 修改入职时间 | 设置、修改或清除 start date，状态在 Offered 与 Onboarding Scheduled 之间切换 | `references/onboarding-start-date.md` |
| 修改学员信息 | 姓名、邮箱、地点、工作授权、等级、年限、费率、Status Override | `references/candidate.md` |
| 面试 Slot | 按用户贴的时间表批量创建某天某轮次的 Slot（先 dry run 再确认）、给候选人占 Slot（L2 必须和 L1 同一个 Recruiter）、释放、作废；占 Slot 后状态是 `L1/L2 Slot Held`，邀请邮件到了建出面试才是 Scheduled | `references/slots.md` |

共同规则：先定位到唯一一条记录（重名或多条时必须询问）；写入前展示「字段：旧值 → 新值」并等待明确确认；更新必须带刚读取的 `version`；选项值只用 `staffing_list_options` 返回的；入职资料（SSN 后四位、出生日期、地址等）只在用户明确要求时读写，回复里不重复其值。

## 依赖的 MCP 工具

`staffing_search_candidates`、`staffing_get_candidate`、`staffing_list_interviews`、`staffing_update_interview`、`staffing_create_interview`、`staffing_list_onboardings`、`staffing_get_onboarding`、`staffing_create_onboarding`、`staffing_update_onboarding`、`staffing_update_candidate`、`staffing_list_options`、`staffing_get_history`、`staffing_list_slots`、`staffing_create_slots`、`staffing_hold_slot`、`staffing_release_slot`、`staffing_cancel_slots`。

## 说明

- 后端服务与工具定义在 `beaconfire-marketing-system` 仓库（`backend/app/modules/staffing/mcp/tools.py`）。
- Skill 里不含任何凭据；本地没有读写数据库或表格的能力，所有写入都经过 MCP 并记入变更记录。
