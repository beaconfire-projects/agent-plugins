# marketing-system

连接 Beaconfireinc Marketing System 的 MCP 服务（`https://api-marketing-mcp.beaconfireinc.com/mcp`），并提供 `staffing` Skill，用来对 Staffing（Meta Data Center 招聘流程）的数据做受控修改。目前只有生产环境（没有 dev 环境），所以只提供正式版插件 `marketing-system`。

## 安装

```text
/plugin marketplace add https://github.com/beaconfire-projects/agent-plugins
/plugin install marketing-system@beaconfireinc
```

首次使用时按提示完成 Authsome 登录。账号必须已被分配系统登记的角色，否则所有工具返回 403（`No role assigned` / `Role not allowed`）；分配角色后需要重新登录才生效。

## `staffing` Skill

按姓名、Candidate ID（`CAN-xxxxx`）、Interview 编号（`INT-xxxx`）或 Onboarding 编号（`ONB-xxxx`）处理八类请求：

| 请求 | 说明 | 参考文件 |
| --- | --- | --- |
| 查询面试 | 只读：某人有几个面试、每场的轮次、时间、结果和评分（重名先问是哪一个；已取消、Need to Reschedule 的保留为历史并标出当前有效的一场）；按 Interview 编号直接读一场；按轮次和日期查日程 | `references/interview.md` |
| 修改面试时间或结果 | 改日期、时间、时区、结果（含 Need to Reschedule）、评分、会议链接、Recruiter、面试官（客户方评估人，聊天反馈里的 Evaluator）、备注；已取消或标了 Need to Reschedule 的面试重约会新建一条面试 | `references/interview.md` |
| 创建 Onboarding | 记录学员拿到 offer，必须有 offer 日期；已有记录时改为修改。L2 改成 Passed（含批量）后，工具返回 `onboarding_suggestion` 时不再询问，保存成功后直接按建议的 offer 日期建 Onboarding 并在同一回复里报告；用 `status=L2 Passed` 找出之前漏建的人 | `references/onboarding-create.md` |
| 取消 offer | offer 被取消（候选人拒绝 `candidate_declined`，或公司撤回 `company_rescinded`）：Onboarding 记录保留，候选人变 Candidate Withdrew / Company Dropped（原因 `Offer rescinded: …`），Offer Status 和 Start Date 清空，客户的 Onboarding Info Sheet 里整行划删除线；类型必须来自用户的话，说不清就问；可撤销，撤销后恢复。已取消的记录不能改，候选人的 Status Override 要先撤销才能改；列表默认不含已取消的 | `references/onboarding-cancel.md` |
| 修改入职时间 | 设置、修改或清除 start date，状态在 Offered 与 Onboarding Scheduled 之间切换 | `references/onboarding-start-date.md` |
| 修改学员信息 | 姓名（只能改 First / Middle / Last / Preferred，没有 `name`；用户只给全名时先拆成三段并展示给用户确认）、邮箱、地点、工作授权、等级、年限、费率、Status Override；入职资料（地址、电话、出生日期、SSN 后四位等，不含姓名）和其他字段一样直接读写，确认时显示旧值 → 新值，SSN 只存后四位 | `references/candidate.md` |
| 面试 Slot | 按用户贴的时间表批量创建某天某轮次的 Slot（先用 `dry_run` 让服务端预览会建几个、跳过几个、为什么，同时核对已有 Slot；确认后用同样的参数只调用一次，成功后不要重复调用，否则会重复新建）、给候选人占 Slot（可以一次贴多人，如 `CAN-00012 10AM, CAN-00020 10AM`，同一时间有多个 Recruiter 会问；先用 `staffing_hold_slots` 的 `dry_run` 预览每一行会不会成功，整批一张确认表，确认后同样参数再执行；L2 必须和 L1 同一个 Recruiter）、释放、作废；占 Slot 后状态是 `L1/L2 Slot Held`，邀请邮件到了建出面试才是 Scheduled | `references/slots.md` |
| 删除记录 | 删除用错误数据建出来的候选人、面试或 Onboarding（不可恢复）；候选人名下还有面试或 Onboarding 时要先删它们；记录没发生过用改结果或 Status Override，不用删除 | `references/delete.md` |
| 立即处理邮件、读取客户群 | 用户要“现在就处理”时:先用只读的预览工具看会创建/更新多少、哪些要人看、会发哪些飞书告警，确认后再手动运行，再看运行结果 | `references/ingest.md` |

共同规则：先定位到唯一一条记录（重名或多条时必须询问）；写入前展示「字段：旧值 → 新值」并等待明确确认；更新必须带刚读取的 `version`；选项值只用 `staffing_list_options` 返回的；入职资料（SSN 后四位、出生日期、地址等）和其他字段一样直接读写（变更记录里只显示 changed）；L2 改成 Passed 后必须问是否创建 Onboarding。

## 依赖的 MCP 工具

`staffing_search_candidates`、`staffing_get_candidate`、`staffing_get_interview`、`staffing_list_interviews`、`staffing_update_interview`、`staffing_create_interview`、`staffing_list_onboardings`、`staffing_get_onboarding`、`staffing_create_onboarding`、`staffing_update_onboarding`、`staffing_cancel_onboarding`、`staffing_undo_cancel_onboarding`、`staffing_update_candidate`、`staffing_list_options`、`staffing_get_history`、`staffing_list_slots`、`staffing_create_slots`、`staffing_hold_slot`、`staffing_release_slot`、`staffing_cancel_slots`、`staffing_delete_candidate`、`staffing_delete_interview`、`staffing_delete_onboarding`、`staffing_hold_slots`、`staffing_preview_mail_ingest`、`staffing_run_mail_ingest`、`staffing_get_mail_ingest_status`、`staffing_preview_chat_ingest`、`staffing_run_chat_ingest`、`staffing_get_chat_ingest_status`。

## 说明

- 后端服务与工具定义在 `beaconfire-marketing-system` 仓库（`backend/app/modules/staffing/mcp/tools.py`）。
- Skill 里不含任何凭据；本地没有读写数据库或表格的能力，所有写入都经过 MCP 并记入变更记录。
