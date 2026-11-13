# 独立 Offers 管理（OFR 编号）

适用：新 Offers 页对应的查询、创建、资料/HR 编辑、确认实际入职和离职、Audit trail。**不是旧 Staffing Onboarding 工作流**：不调用 `marketing_create_onboarding`，不要求 L2 通过，不应用旧自动建入职/改人员状态/关闭 Submission 规则。旧 ONB 功能仍按其原 reference 执行；用户明确管理新 Offer 时本文件优先。

## 权限与定位

全部工具复用新 Marketing Offer service：Admin/Manager 全范围，AM 按 Vendor。无默认岗位参数。精确以 OFR 编号操作，同一 Submission 可有多个进行中的 Offer，不能只选最新一个。

- `marketing_list_offers(query={q,status,page,page_size})` 搜索候选人、岗位、Submission/Offer 基本信息；分页返回，status 为精确存储值数组。
- `marketing_get_offer(code)` 读取字段、stage、version 和真实历史。
- `marketing_offer_options()` 获取 PO Company、州、离职原因/下一步、状态选项。
- `marketing_get_offer_history(code)` 只读审计；只有当前 Offer 的可见用户可查询。敏感字段只显示 changed，不能反推地址或联系人。
- 404 同时表示不存在/无权查看，不换旧接口绕过，不猜编号。

## 创建：先选 Submission，再整体确认面试

1. `marketing_search_offer_submissions(query={q,page,page_size})`，按候选人、岗位或 Submission 基本信息查找。
2. 结果不唯一先让用户选；`marketing_preview_offer_submission(code)` 展示该 Submission **全部**面试的编号、轮次、日期/时间和结果。
3. 用户整体确认。不强制通过、不选择来源 interview、不自动把 Submission 标 Offered。
4. Offer Date、Tentative Start Date 均选填，默认 null；不取今天、不继承其他记录。
5. `marketing_create_offer(request={request_id,submission_code,interviews_confirmed:true,offer_date?,onboarding_tentative_start_date?})`。
   - request_id 是此创建尝试的 UUID，同一明确另建动作只用一个；后续独立 Offer 用新 UUID。
   - 相同 ID/相同内容只返回原 Offer，不再写审计。相同 ID/不同内容为409，不换新 ID 来绕过冲突。
   - 网络超时/未知结果先核对，不盲目另发新 ID；确需重放只用原 ID 和原始内容，不根据后续编辑改请求。
6. 报告返回 OFR、关联 Submission、空日期和当前 stage。

## 生命周期

`created → onboarded → offboarded`，仅动作改变。无撤销、重复入职、未入职直接离职；再次入职新建 Offer。

- `marketing_onboard_offer(code,request={version,...入职字段})`：实际开始日期、PO Company (`Invct/BSS/BFS`)、Work Location 的 State 必填。其余入职日期、BGC 信息、Marketing Email、Notes、PO Vendor、Rate、四个检查项选填。
- PO Vendor 先 `marketing_search_offer_po_vendors(query={q,page,page_size})`，使用真实公司 code，填 `po_vendor_code`，可清空。不创建公司。
- Rate 非负 **USD/hour**，映射 offers.rate；不是 Salary，本期不处理 Salary，也不转换旧 ext_salary 历史文本。
- `marketing_offboard_offer(code,request={version,offboarding_last_day?,offboarding_current_status?,offboarding_reason?,offboarding_next_step?,offboarding_notes?})`：业务五项**全部选填**，全部空也确认离职。无 planned last day。current_status 仅 Remap/Quit/Fired 或空；日期填了不得早于实际入职。
- 新状态 offer_status 为 In Progress/Active/Offboarded，离职结果单独保存。优先看 stage 判动作资格，不以 last_day 有无判断结束。
- 每次先读版本，展示将保存的字段和动作，等待明确确认；409重新读取并再次确认，不自动重试。
- 新操作仅改当前 Offer，不修改候选人、Submission 或营销状态，不触发旧 Sheet 同步。

## 编辑与 HR

`marketing_update_offer(code,request={version,...dirty字段})`。仅发修改字段，显式 null 清空，省略保持不变。禁止直接传 stage/offer_status/actor/source/person_id/position_id。

创建后所有阶段可编辑 HR，权限相同，不触发生命周期：
- `onboarding_i9_completed`、`onboarding_everify_completed` 是完成标记，不是日期；与 `onboarding_ts_setup_done` 及全部离职 HR 检查项一样使用 true/false/null 三态。
- 离职 HR：`offboarding_hr_email_sent`（界面 ob_email_sent）、`offboarding_equipment_returned`、`offboarding_adp_status_updated`、`offboarding_final_paycheck_processed`、`offboarding_hr_admin_complete`、`offboarding_hr_notified_date`、`offboarding_hr_notes`。HR notes 不覆盖普通离职 notes。
- 地址对象统一 `{line1,line2,city,state,zipcode}`。Work Location 入职只要求州；Shipping Address `onboarding_shipping_address` 整体可空，否则 line1/city/state/zipcode 必填，line2 选填。美国50州不含DC，所有组件禁逗号。两地址彼此及候选人住址互不覆盖。
- 已入职的实际日期、PO Company、State 不能被编辑清空；日期更正仍校验先后。
- `work_location_raw` / `onboarding_shipping_address_raw` 和 `legacy_check_values` 是不能无损解释的旧值提示，不是编辑字段。只改别的字段时不能把这些值悄悄改成 null/false。

## 审计与异常

成功实际变化有操作者、可信渠道、时间和旧值 → 新值；敏感值只记 changed。创建/修改/状态与审计同事务，失败一起回滚；查看、无变化保存、不成功请求无审计。真实旧事件可能没有字段差异，不补造。时间显示 ET（夏令时自动处理）。写入返回异常时不声称成功；未知结果读取核对，版本冲突重新确认，权限拒绝停止。
