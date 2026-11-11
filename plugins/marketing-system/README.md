# marketing-system

连接 Beaconfireinc Marketing System 的 MCP 服务（`https://api-marketing-mcp.beaconfireinc.com/mcp`），并提供 `staffing` Skill，用来对 Staffing（Meta Data Center 招聘流程）的数据做受控修改。目前只有生产环境（没有 dev 环境），所以只提供正式版插件 `marketing-system`。

## 安装

```text
/plugin marketplace add https://github.com/beaconfire-projects/agent-plugins
/plugin install marketing-system@beaconfireinc
```

首次使用时按提示完成 Authsome 登录。账号必须已被分配系统登记的角色，否则所有工具返回 403（`No role assigned` / `Role not allowed`）；分配角色后需要重新登录才生效。

## `staffing` Skill

按姓名、Candidate ID（`PER-nnnnnn`）、Interview 编号（`INT-xxxx`）或 Onboarding 编号（`ONB-xxxx`）处理十一类请求：

| 请求 | 说明 | 参考文件 |
| --- | --- | --- |
| 查询面试 | 只读：某人有几个面试、每场的轮次、时间、结果和评分（重名先问是哪一个；已取消、Need to Reschedule 的保留为历史并标出当前有效的一场）；按 Interview 编号直接读一场；按轮次和日期查日程 | `references/interview.md` |
| 修改面试时间或结果 | 改日期、时间、时区、结果（含 Need to Reschedule）、评分、会议链接、Recruiter、面试官（客户方评估人，聊天反馈里的 Evaluator）、备注；已取消或标了 Need to Reschedule 的面试重约会新建一条面试 | `references/interview.md` |
| 创建 Onboarding | 记录学员拿到 offer，必须有 offer 日期；已有记录时改为修改。L2 改成 Passed（含批量）后，工具返回 `onboarding_suggestion` 时不再询问，保存成功后直接按建议的 offer 日期建 Onboarding 并在同一回复里报告；用 `status=L2 Passed` 找出之前漏建的人 | `references/onboarding-create.md` |
| 取消 offer | offer 被取消（候选人拒绝 `candidate_declined`，或公司撤回 `company_rescinded`）：Onboarding 记录保留，候选人变 Candidate Withdrew / Company Dropped（原因 `Offer rescinded: …`），Offer Status 和 Start Date 清空，客户的 Onboarding Info Sheet 里整行划删除线；类型必须来自用户的话，说不清就问；可撤销，撤销后恢复。已取消的记录不能改，候选人的 Status Override 要先撤销才能改；列表默认不含已取消的 | `references/onboarding-cancel.md` |
| 确认入职和 Offboarding | 业务确认学员真的到岗（填实际开始日期，状态变 Active）；创建 Offboarding（所有字段可空，更新时只合并非空值，可取消）；确认离开（结果 Remap / Quit / Fired，原因和下一步取自业务表单，投递关闭）。Offer 的状态只能由这些动作驱动 | `references/onboarding-start-end.md` |
| 修改入职时间 | 设置、修改或清除 start date，状态在 Offered 与 Onboarding Scheduled 之间切换 | `references/onboarding-start-date.md` |
| 创建、修改学员信息 | 创建 Candidate（必填类型、First、Last、Email，其余都可空：年限、签证类型和起止日期、电话、地址、出生日期、性别、LinkedIn、Facebook、手机和电脑偏好；Bench 不新建，从有批次信息的人里转）；修改时个人资料用 `staffing_update_person`（姓名只能改 First / Middle / Last / Preferred，没有 `name`；邮箱和电话不能属于别人；类型必填；地址和出生日期审计只记 changed），Level、Lead、费率、Status Override、SSN 后四位等用 `staffing_update_candidate`；确认时显示旧值 → 新值 | `references/candidate.md` |
| 创建、修改 Submission | 把候选人投递到自己 Vendor 的岗位（可同时给费率、可入职时间、出差、面试可约时间、同客户经历、C2C 雇主及联系人）；读取 Submission 详情；修改投递信息（只改给了的字段，改过的以后 Submission 邮件不再覆盖；投递里的 C2C 雇主和候选人自己的雇主互不影响；Level / Lead / 状态不在这里改） | `references/submission.md` |
| 面试 Slot | 按用户贴的时间表批量创建某天某轮次的 Slot（先用 `dry_run` 让服务端预览会建几个、跳过几个、为什么，同时核对已有 Slot；确认后用同样的参数只调用一次，成功后不要重复调用，否则会重复新建）、给候选人占 Slot（可以一次贴多人，如 `PER-010012 10AM, PER-010020 10AM`，同一时间有多个 Recruiter 会问；先用 `staffing_hold_slots` 的 `dry_run` 预览每一行会不会成功，整批一张确认表，确认后同样参数再执行；L2 必须和 L1 同一个 Recruiter）、释放、作废；占 Slot 后状态是 `L1/L2 Slot Held`，邀请邮件到了建出面试才是 Scheduled | `references/slots.md` |
| 删除记录 | 删除用错误数据建出来的候选人、面试或 Onboarding（不可恢复）；候选人名下还有面试或 Onboarding 时要先删它们；记录没发生过用改结果或 Status Override，不用删除 | `references/delete.md` |
| 统计分析 | 只读，只有数字没有姓名：各状态多少人、等 L1 / L2 排期多少人、每月 offer 数、面试通过率、按 Level / 工作授权 / 年限分布、两个口径的对比；数字来自指标服务（Cube），与 Staffing Dashboard 同一口径，**不要靠翻候选人列表自己数**；先 `insights_list_metrics` 取指标和维度，再 `insights_query`；也能按 Vendor（只算 Primary Vendor）/ Client 统计岗位数、Submission 数、Candidate 数、Offer 数和各阶段人数，Submission 按提交时间统计（这部分只有 Admin 能查，其他人目录里没有）；要看具体是谁时改用 `staffing_search_candidates` 等。服务不可用时直接告知，不用别的工具凑数 | `references/insights.md` |
| 立即处理邮件、读取客户群 | 用户要“现在就处理”时:先用只读的预览工具看会创建/更新多少、哪些要人看、会发哪些飞书告警，确认后再手动运行，再看运行结果 | `references/ingest.md` |

共同规则：先定位到唯一一条记录（重名或多条时必须询问）；写入前展示「字段：旧值 → 新值」并等待明确确认；更新必须带刚读取的 `version`；选项值只用 `staffing_list_options` 返回的；入职资料（SSN 后四位、出生日期、地址等）和其他字段一样直接读写（变更记录里只显示 changed）；L2 改成 Passed 后必须问是否创建 Onboarding。

## 依赖的 MCP 工具

`staffing_search_candidates`、`staffing_get_candidate`、`staffing_get_interview`、`staffing_list_interviews`、`staffing_update_interview`、`staffing_create_interview`、`staffing_list_onboardings`、`staffing_get_onboarding`、`staffing_create_onboarding`、`staffing_update_onboarding`、`staffing_confirm_onboarding_start`、`staffing_create_offboarding`、`staffing_update_offboarding`、`staffing_cancel_offboarding`、`staffing_confirm_offboarding`、`staffing_cancel_onboarding`、`staffing_undo_cancel_onboarding`、`staffing_update_candidate`、`staffing_list_options`、`staffing_get_history`、`staffing_list_slots`、`staffing_create_slots`、`staffing_hold_slot`、`staffing_release_slot`、`staffing_cancel_slots`、`staffing_delete_candidate`、`staffing_delete_interview`、`staffing_delete_onboarding`、`staffing_hold_slots`、`staffing_preview_mail_ingest`、`staffing_run_mail_ingest`、`staffing_get_mail_ingest_status`、`staffing_preview_chat_ingest`、`staffing_run_chat_ingest`、`staffing_get_chat_ingest_status`、`insights_list_metrics`、`insights_query`。

## 说明

- 后端服务与工具定义在 `beaconfire-marketing-system` 仓库（`backend/app/modules/staffing/mcp/tools.py`）。
- Skill 里不含任何凭据；本地没有读写数据库或表格的能力，所有写入都经过 MCP 并记入变更记录。
