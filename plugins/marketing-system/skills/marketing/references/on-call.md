# On-Call Schedule（值班 Trainer 周排班）

仅可使用实际声明 tags 含 `marketing` 的 MCP 工具；本页三个工具已核对 `marketing/mcp/on_call.py` 的 `{"marketing", "on-call"}` 声明。无法验证标签或工具不在目录里时停止并说明能力缺口，不得通过 REST、SQL 或脚本绕过，也不得改用 staffing-only 工具。

每周有一个值班 **Primary** Trainer 和一个可选的 **Secondary** Trainer，显示在 Marketing 日历（`/calendar`）标题行里，也在网页 Settings → On-Call Schedule 里维护。

## 适用场景

- 查某一周、某段时间或"本周"谁值班。
- 换班、补排、改备份、改备注（节假日或换班原因）。
- 清除某一周的排班（回到"未安排"）。

不适用：批量铺排整年轮换、自动轮换、从表格同步。这些没有工具；2026 年历史排班是后端一次性脚本导入的。

## 前置条件和权限

- **查看**（`marketing_list_on_call_schedule`）：所有登录用户都能用。
- **修改和清除**（`marketing_set_on_call_week`、`marketing_clear_on_call_week`）：token 的角色代码必须含 `admin` 或 `trainer`；其他人这两个工具不在工具列表里。此时直接说明权限不足并停止，不要找别的办法。
- 值班人必须是 Authsome 里**持有 trainer 角色**的在职成员，用**登录邮箱**指定，不接受姓名；不要凭姓名猜邮箱。邮箱不确定时，先向用户确认，或让用户在网页 Settings 里选。

## 周的定义

- 一周是**纽约时区（America/New_York）的周一到周日**，用周一的日期 `week_start`（YYYY-MM-DD）标识。
- `week_start` 必须是周一；传了别的日子会被拒绝，并告诉你那一周的周一。
- 没有出现在 list 结果里的周就是"未安排"。

## 调用顺序

### 查看

1. `marketing_list_on_call_schedule(date_from?, date_to?)`：不传日期返回本周；两个日期都传时，返回和这个区间重叠的所有周，区间最长约 800 天。
2. 返回的每一项有 `week_start`、`week_end`、`primary`（`email`、`name`）、`secondary`（可为 null）、`note`。

### 修改（先查、再确认、再写）

1. 先 `marketing_list_on_call_schedule` 查出这一周现在的值班人，展示给用户。
2. 向用户确认**改动内容**（哪一周、谁换成谁、备注），得到明确的"是"之后才调用写工具。
3. `marketing_set_on_call_week(week_start, primary_email?, secondary_email?, clear_secondary?, note?, clear_note?)`：
   - 只更新传入的字段，没传的保持不变。
   - 清空备份传 `clear_secondary=true`（不能同时传 `secondary_email`）；清空备注传 `clear_note=true`（不能同时传 `note`）。
   - 这一周还没有排班时，必须同时传 `primary_email` 才能创建。
   - Primary 不能清空；要整周移除用清除工具。
4. 用返回值或再次 list 回读，把结果报告给用户。

### 清除

确认后调用 `marketing_clear_on_call_week(week_start)`。这一周没有排班时会报错；清除后该周显示"未安排"。要改人而不是清除，用 set。

## 业务约束

- Primary 必填；Secondary 可空；两人不能是同一个人。
- 过去的周也可以改，不锁定。每次修改都有审计记录（渠道 `mcp`）。
- 备注（note）只在 Settings 页面显示，日历上不显示。
- 换班没有申请流程：直接把那一周的 Primary 或 Secondary 改掉，原因写进 note。

## 异常处理

- `must be a Monday`：按报错里给出的周一重试。
- `Not an active Authsome trainer: ...`：邮箱不是在职 trainer。让用户确认邮箱，或先在 Authsome 里给这个人 trainer 角色；不要换一个邮箱猜。
- `Trainers are given by login email ... names are not accepted`：改传邮箱。
- `Primary and secondary must be different people` / `primary_email is required`：按提示改参数后重试。
- Authsome 名单读不到：整次没有写入，稍后重试。
- 错误里说结果可能未知（`on_call_operation_failed`）：先用 `marketing_list_on_call_schedule` 回读当前状态，再决定是否重试，不要盲目重复写入。
