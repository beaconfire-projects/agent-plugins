# marketing-system

连接 Beaconfireinc Marketing System 的 MCP 服务（`https://api-marketing-mcp.beaconfireinc.com/mcp`），并提供 `marketing` 和 `staffing` Skills，用来对 Staffing（Meta Data Center 招聘流程）的数据做受控修改。目前只有生产环境（没有 dev 环境），所以只提供正式版插件 `marketing-system`。

## 安装

```text
/plugin marketplace add https://github.com/beaconfire-projects/agent-plugins
/plugin install marketing-system@beaconfireinc
```

首次使用时按提示完成 Authsome 登录。账号必须已被分配系统登记的角色，否则所有工具返回 403（`No role assigned` / `Role not allowed`）；分配角色后需要重新登录才生效。

## 工具名与版本

v0.21.0：Marketing skill 的创建 Candidate 流程改调 `marketing_add_candidate`（四个入口共用的完整版），并用同样带 `marketing` 标签的 `marketing_search_candidates`、`marketing_search_addable_people`、`marketing_get_candidate_detail` 搜索和读回；不再引用 `marketing_create_candidate`（后端稍后删除，不留旧名）。审计在 `module=staffing` 下，可用 `marketing_get_history` 读到。配套后端 0.1.0-169：这 15 个 Candidate 工具标签为 `staffing`、`marketing`、`candidates`。

v0.20.0：配套后端 Offer 接口整理：取消 Offer 的 MCP 工具统一叫 cancel——`marketing_withdraw_offer` 改为 `marketing_cancel_offer`，`marketing_undo_withdraw_offer` 改为 `marketing_undo_cancel_offer`，旧名已删除不留别名；Offer 选项里的 `withdraw_parties` 改叫 `cancel_parties`，Offer 返回里的撤回字段改叫 `cancel_party` / `cancel_reason` / `canceled_at`。取消的业务规则不变（候选人拒绝或公司撤回，任何阶段都可取消，可撤销，不动 Submission）。后端 Offer REST 同时改为 `/api/v1/offers`，skill 只调 MCP，不受路径影响。

v0.22.0：Submission 只有一套工具（与 Marketing skill 共用）——`marketing_get_workspace_submission`、`marketing_create_submission`（同一个人同一岗位可以有多条 Submission）、`marketing_update_workspace_submission`（Level、Lead、投递信息，用这条 Submission 自己的版本号）、`marketing_reject_submission`（必须带拒绝方 `Candidate` / `Company` 和原因）、`marketing_reopen_submission`（拒绝可撤销）；状态只存 `Active` / `Rejected`，Offered 只由这条 Submission 创建出的 Offer 推出；`marketing_get_submission`、`marketing_update_submission`、`marketing_submit_candidate_to_position`、`marketing_mark_submission_offered` 已删除，Staffing 的 Level / Lead / Status Override 不再用 `marketing_update_candidate_submission` 改。

v0.19.0：Offer 生命周期改版，配套后端 Offer lifecycle v2。Offer 状态 Offered / On Project / Off Project / Canceled **全部由日期和取消推导**（实际入职日到了才是 On Project，实际最后工作日的第二天起是 Off Project，实际日期可填未来、可改可清；预计日期不改状态）；创建 Offer 必填 PO Company，从 Submission 创建（`marketing_create_offer`），修改、确认入职 / 离职都用 `marketing_update_offer`，取消用 `marketing_cancel_offer` / `marketing_undo_cancel_offer`；人的营销状态随 Offer 自动变。**已删除**：`marketing_create_onboarding`、`marketing_update_onboarding`、`marketing_get_onboarding`、`marketing_list_onboardings`、`marketing_delete_onboarding`、`marketing_confirm_onboarding_start`、`marketing_cancel_onboarding`、`marketing_undo_cancel_onboarding`、`marketing_create_offboarding`、`marketing_update_offboarding`、`marketing_confirm_offboarding`、`marketing_cancel_offboarding`、`marketing_onboard_offer`、`marketing_offboard_offer`（不留旧名）；staffing 的四份 onboarding 参考文件合并为 `references/offer.md`，原 `staffing/references/offers.md` 并入其中；`marketing` Skill 的 `offer.md`、`offer-lifecycle.md`、`tool-boundary.md` 同步改为新规则。L2 通过后不再自动建，要先问 PO Company。

v0.14.1：`marketing_search_candidates` 和 Web / 表格菜单共用同一套筛选（`query`、`vendor`、`client`、`position`、`candidate_type`、`marketing_status`、`current_status`、`lead`、`yoe_min`、`yoe_max`）；原参数 `status` 改名 `current_status`（面试进度，必须有岗位范围，否则报错），`on_project` 已去掉（用 `marketing_status=On Project`）；不带筛选时返回看得到的全部范围，不再只看当前岗位。

v0.14.0：Candidate 能力收敛为四个入口共用的一组工具——`marketing_add_candidate`（已有 Person 传 `person_code`，或新建，同一个动作）、`marketing_search_addable_people`、`marketing_update_candidate`（个人资料含营销状态）；原 `marketing_create_candidate`、`marketing_convert_person_to_candidate`、`marketing_search_bench_pool`、`marketing_update_candidate_profile`、`marketing_delete_candidate` 已删除（删除 Candidate 只在 Admin 网页后台）；原 `marketing_update_candidate`（Level / Lead / Status Override 等）改名 `marketing_update_candidate_submission`。

v0.13.0 起 MCP 工具名从 `staffing_*` 改为 `marketing_*`（统计工具仍是 `insights_*`），旧名不再保留；候选人自己的资料更新叫 `marketing_update_candidate`（`marketing_update_person` 是 Admin / Manager 用的共用 Person / HR 资料管理工具，两者不同）。**插件和后端要配套**：先发后端，再更新到 v0.19.0；只更新插件而后端还是旧版时，Skill 找不到工具；后端已发新版而插件还是旧版时同理。

## `marketing` Skill：Person 与 Interview Management（v0.18.0）

共享 Person/HR 支持查询、手动创建、HR 导入、修改、选项及字段审计。 支持显式确认后的单条删除：Person 只在存在 Submission 时禁止删除；Interview 对应 Submission 存在任意状态的 Offer 时禁止删除。Interview 页面按钮显示 Cancel，实际删除当前记录，与保留记录的 Canceled 结果不同。删除和操作日志同事务，失败回滚；不支持批量或连带删除。创建 Person 的必填信息、联系方式替换、HR/签证/批次的字段含义见 `skills/marketing/references/person.md` 和 `create-person.md`。

Interview Management 支持用人名、PER ID、邮箱/电话、Submission ID、Position、Vendor/Client 搜索已有投递，选择后带出人、岗位与轮次，再创建/查看/修改面试及查询审计。场景限制、预约必填项、评分追问、确认与失败恢复见 `skills/marketing/references/interview.md`。内部 INT 与 Sheet HIST-IV 是两个编号。

这次只更新 marketing Skill，staffing 文件保持不变。共享 Person/HR 和 Submission 驱动的面试管理走 marketing；已有 Staffing Candidate/Slot 流程仍走 staffing（旧 ONB 工具已在 v0.19.0 删除，Offer 统一走 `marketing_*_offer`），不混用自动后续动作。Marketing 面试保存返回的 onboarding_suggestion 不会授权自动创建 ONB/OFR。运行时工具须符合 `skills/marketing/references/tool-boundary.md` 的能力清单（本次源码验证 Person/Interview 14 个工具，其余 35 项保留已有契约）；后端部署未提供新工具时报告版本缺口。

## `staffing` Skill

按姓名、Candidate ID（`PER-nnnnnn`）、Interview 编号（`INT-xxxx`）或 Offer 编号（`OFR-nnnnnn`）处理九类请求：

| 请求 | 说明 | 参考文件 |
| --- | --- | --- |
| 查询面试 | 只读：某人有几个面试、每场的轮次、时间、结果和评分（重名先问是哪一个；已取消、Need to Reschedule 的保留为历史并标出当前有效的一场）；按 Interview 编号直接读一场；按轮次和日期查日程 | `references/interview.md` |
| 修改面试时间或结果 | 改日期、时间、时区、结果（含 Need to Reschedule）、评分、会议链接、Recruiter、面试官（客户方评估人，聊天反馈里的 Evaluator）、备注；已取消或标了 Need to Reschedule 的面试重约会新建一条面试 | `references/interview.md` |
| Offer | 从 Submission 创建 Offer（必填 PO Company，日期可空；创建前要看过全部面试）；查询 Offer（同一 Submission 可有多条）；设置、修改、清除预计或实际入职日 / 最后工作日（状态由日期推导，不能直接改；实际日期可填未来；实际离职需要实际入职且不早于它）；确认入职、确认离职（Remap / Quit / Fired，原因和下一步取自业务表单）；BGC、HR 清单、地址、费率等字段；取消 offer（候选人拒绝 `Candidate` 或公司撤回 `Company`，任何阶段都可，可撤销，不动 Submission）。L2 改成 Passed 后返回 `onboarding_suggestion` 时要提示并询问 PO Company，不自动建 | `references/offer.md` |
| 创建、修改学员信息 | 创建 Candidate（必填类型、First、Last、Email，其余都可空：年限、签证类型和起止日期、电话、地址、出生日期、性别、LinkedIn、Facebook、手机和电脑偏好；Bench 不新建，从已有的人里添加（`marketing_search_addable_people`））；修改时个人资料用 `marketing_update_candidate`（姓名只能改 First / Middle / Last / Preferred，没有 `name`；邮箱和电话不能属于别人；类型必填；地址和出生日期审计只记 changed），SSN 后四位、其他邮箱、OSHA 等用 `marketing_update_candidate_submission`（Level、Lead、费率、拒绝和重开已归 Submission 统一的工具，见 `references/submission.md`）；确认时显示旧值 → 新值 | `references/candidate.md` |
| 创建、修改 Submission | 把候选人投递到自己 Vendor 的岗位（可同时给费率、可入职时间、出差、面试可约时间、同客户经历、C2C 雇主及联系人）；读取 Submission 详情；修改投递信息（只改给了的字段，改过的以后 Submission 邮件不再覆盖；投递里的 C2C 雇主和候选人自己的雇主互不影响；Level / Lead / 状态不在这里改） | `references/submission.md` |
| 面试 Slot | 按用户贴的时间表批量创建某天某轮次的 Slot（先用 `dry_run` 让服务端预览会建几个、跳过几个、为什么，同时核对已有 Slot；确认后用同样的参数只调用一次，成功后不要重复调用，否则会重复新建）、给候选人占 Slot（可以一次贴多人，如 `PER-010012 10AM, PER-010020 10AM`，同一时间有多个 Recruiter 会问；先用 `marketing_hold_slots` 的 `dry_run` 预览每一行会不会成功，整批一张确认表，确认后同样参数再执行；L2 必须和 L1 同一个 Recruiter）、释放、作废；占 Slot 后状态是 `L1/L2 Slot Held`，邀请邮件到了建出面试才是 Scheduled | `references/slots.md` |
| 删除记录 | 删除用错误数据建出来的面试（不可恢复；候选人只能由 Admin 在网页后台删除，Offer 不能删除、只能取消）；记录没发生过用改结果，或拒绝这条 Submission，不用删除 | `references/delete.md` |
| 统计分析 | 只读，只有数字没有姓名：各状态多少人、等 L1 / L2 排期多少人、每月 offer 数、面试通过率、按 Level / 工作授权 / 年限分布、两个口径的对比；数字来自指标服务（Cube），与 Staffing Dashboard 同一口径，**不要靠翻候选人列表自己数**；先 `insights_list_metrics` 取指标和维度，再 `insights_query`；也能按 Vendor（只算 Primary Vendor）/ Client 统计岗位数、Submission 数、Candidate 数、Offer 数和各阶段人数，Submission 按提交时间统计（这部分只有 Admin 能查，其他人目录里没有）；要看具体是谁时改用 `marketing_search_candidates` 等。服务不可用时直接告知，不用别的工具凑数 | `references/insights.md` |
| 立即处理邮件、读取客户群 | 用户要“现在就处理”时:先用只读的预览工具看会创建/更新多少、哪些要人看、会发哪些飞书告警，确认后再手动运行，再看运行结果 | `references/ingest.md` |

共同规则：先定位到唯一一条记录（重名或多条时必须询问）；写入前展示「字段：旧值 → 新值」并等待明确确认；更新必须带刚读取的 `version`；选项值只用 `marketing_list_options` 返回的；入职资料（SSN 后四位、出生日期、地址等）和其他字段一样直接读写（变更记录里只显示 changed）；L2 改成 Passed 后要提示可以建 Offer 并询问 PO Company。

## 依赖的 MCP 工具

`marketing_search_candidates`、`marketing_get_candidate`、`marketing_get_interview`、`marketing_list_interviews`、`marketing_update_interview`、`marketing_create_interview`、`marketing_list_offers`、`marketing_get_offer`、`marketing_get_offer_history`、`marketing_search_offer_submissions`、`marketing_preview_offer_submission`、`marketing_create_offer`、`marketing_update_offer`、`marketing_cancel_offer`、`marketing_undo_cancel_offer`、`marketing_offer_options`、`marketing_search_offer_po_vendors`、`marketing_update_candidate_submission`、`marketing_get_candidate_detail`、`marketing_add_candidate`、`marketing_search_addable_people`、`marketing_get_workspace_submission`、`marketing_update_workspace_submission`、`marketing_reject_submission`、`marketing_reopen_submission`、`marketing_list_options`、`marketing_get_history`、`marketing_list_slots`、`marketing_create_slots`、`marketing_hold_slot`、`marketing_release_slot`、`marketing_cancel_slots`、`marketing_delete_interview`、`marketing_hold_slots`、`marketing_preview_mail_ingest`、`marketing_run_mail_ingest`、`marketing_get_mail_ingest_status`、`marketing_preview_chat_ingest`、`marketing_run_chat_ingest`、`marketing_get_chat_ingest_status`、`insights_list_metrics`、`insights_query`。

## 说明

- 后端服务与工具定义在 `beaconfire-marketing-system` 仓库（`backend/app/modules/staffing/mcp/tools.py`）。
- Skill 里不含任何凭据；本地没有读写数据库或表格的能力，所有写入都经过 MCP 并记入变更记录。
