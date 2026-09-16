---
name: crm-copilot-dev
description: Use the user-connected Beaconfireinc CRM Copilot MCP for CRM-relevant business notes and requests involving people, customers, colleagues, vendors/companies, roles, relationships, meetings, visits, customer facts, lookups, position searches, creation, updates, merges, address and organization normalization, recommendations, reminders, and evidence. Reminder requests require both CRM persistence and a host-native Claude notification/calendar reminder. Business-context notes can be routed even without create/save wording; ordinary non-business social chat is not a CRM task. Always follow the server-side route, check, preview, and explicit-confirmation workflow.
---

# CRM Copilot

Use the user-connected `crm-copilot-dev` MCP server as the only source of truth for CRM work. The user explicitly connected this plugin for authorized business CRM assistance; this is not a request to exfiltrate data or to write silently. Do not use direct REST calls, the admin API, SQL, shell scripts, invented customer IDs, or a different CRM plugin to complete a chat request.

The MCP server is authoritative for the database contract, but the Agent is
responsible for extracting intent and following the returned `nextAction`. The
tool names and UI boundaries below are the contract (not hypothetical
tool names). Any tool response with `ok=false` is a failed gate; do not infer a
successful lookup, preview, or write from an HTTP 200 response.

### Tool/UI map

| Purpose | Tool(s) | UI resource |
| --- | --- | --- |
| Route and read-only gates | `crm_message_route`, `customer_existence_check`, `organization_existence_check`, `geo_resolve`, all `*_precheck` | none |
| Create | `customer_prepare_create` → `customer_create_preview` | confirmation page only at preview |
| Update | `customer_prepare_update` → `customer_update_preview` | confirmation page only at preview |
| Single-target merge/overwrite | `customer_prepare_merge` → `customer_merge_preview` | confirmation page only at preview |
| Save from a confirmation page | `customer_confirm_pending_operation` (preferred) or the matching `customer_confirm_*` fallback | none |
| Detail/list/recommendation/location results | `customer_get`, `customer_query`, `customer_recommend`, `customer_location_results` | detail, customers, or recommend |
| Position list/detail | `position_query`, `position_get` | position-search |
| Originals/evidence | `customer_record_communication`, `customer_field_evidence`, `customer_evidence_get` | none |
| Explicit note/interest | `customer_update_precheck` → `customer_add_note` | none |
| Company directory | `company_query` | company list |
| Company customers | `company_customer_query` | company customer list |
| Company positions | `company_position_query` | company position list |

The confirmation UI currently tries `customer_confirm_pending_operation` first
and falls back to `customer_confirm_create`, `customer_confirm_update`, or
`customer_confirm_merge`. For a UI save, pass the current `confirmationId`,
`confirmationSource="UI"`, `confirmed=true`, the current editable
`finalPayload`, and (when present) `expectedRevision`. A successful save must
return the persisted `customerId` (for create/update/merge) or a persisted
`operationId`/record status; otherwise report failure and never say “saved”.

### Company lookup routing

“Tenarai 有哪些岗位” is an explicit position lookup, not an ambiguous company
lookup. Call `organization_existence_check` with `organization={"name":"Tenarai"}`
without UI, then pass a unique returned `organizationId` to
`company_position_query`. Never call `company_query` just to obtain a company ID.
For multiple matches ask the user to choose from the returned candidates; for
no match report that the company was not found, without creating it. The same
UI-less company resolution applies to an explicit company-customer lookup.
Preserve the user's locale in the check and final query.

Company directory, company-associated customers, and company-associated
positions are three separate capabilities. Use `company_query` only for a
Vendor/Client company list (name, domain, alias, or company type). Use
`company_customer_query` only for active customers associated with a selected
company. Use `company_position_query` only for that company's active positions.
If the user asks only to “查询这家公司” without specifying company,
customers, or positions, ask which capability they want before calling a tool.
Do not guess from the company name. Deleted records are excluded; positions
are limited to `ACTIVE`. Company cards show ID, name, domain, Vendor/Client
labels, and active customer/position counts. Position cards show title, Vendor,
Client, and a collapsed JD. Preserve the selected company ID for related-list
queries.

## 1. Route every CRM-relevant message

Call `crm_message_route` first for:

- a person introduction, meeting/visit report, or customer fact;
- a business-context note that contains a person's name plus company/vendor,
  role, relationship, meeting, or customer context, even when no action verb is used
  (for example, “Basheer 说大部分 vendor 是 Accenture、Cognizant；Intuit 的
  campus 很深”);
- a request to create, update, merge, remove, restore, or view a customer;
- a reminder request;
- a recommendation request;
- a customer search or location search;
- a position or job-opening search;
- a message containing more than one CRM operation.

For a business-context note, default behavior is to route through CRM because
the user connected this plugin for that purpose. This does not mean silent
database mutation: existence checks and prechecks are read-only, previews do
not save, and customer/organization field writes always require explicit
post-preview confirmation. An unchanged existing-customer note may be stored
as the supplied original communication without an operation log, as defined
by the product contract. Skip CRM when the user explicitly says things
such as “只总结，不要录入”, “不要保存到 CRM”, “just summarize”, or “do not
record this”. Ordinary non-business social chat is not routed to CRM.

Infer the conversation locale before routing and pass it to every tool as
`locale="en-US"` for English or `locale="zh-CN"` for Chinese. Do not rely on
the server's default locale, because it is Chinese when `locale` is omitted.

If the route returns `COMPOSITE`, extract the operations and call
`composite_prepare`; do not silently drop one operation. The current
composite executor supports `CREATE_CUSTOMER` and `CREATE_REMINDER` only. If
the message combines an update/merge/remove/recommendation with a reminder,
the precheck will report `UNSUPPORTED_COMPOSITE_OPERATION`; preserve the
unsupported operation in the response and run its normal flow separately
only when the user can review and confirm it. Composite operations are not a
transaction and may succeed independently.

`crm_message_route` uses this deterministic precedence: explicit CRM opt-out →
recommendation → explicit list/search → reminder-only → customer+reminder
composite → customer message → generic CRM review. The route returns
`NOOP`/`UNKNOWN` only when it cannot proceed and should ask the user. A
specific-person request such as “查看 Provine” or “look up Provine” is a
customer identity flow. Pass `mode="view"` to the route for that request so
the returned `nextTool` is `customer_existence_check`; then use `customer_get`
for one match or a selectable list for multiple matches. Pass `mode="search"`
for an explicit list/search request (for example “查询纽约 Google 的客户” or
“search customers at Google”) and reserve `customer_query` for that list flow.
Do not reinterpret a route result silently; when an auto-routed request is
ambiguous, rerun `crm_message_route` with the explicit mode that matches the
user's intent.

### Notes versus ordinary conversation

Do not turn a whole meeting report into GENERAL notes. Preserve the complete
message separately as `sourceText`. General notes still require explicit note
intent, but stated hobbies/preferences are structured INTEREST facts: extract
them automatically without asking the user to say "record/save this interest".
For example, “他喜欢钓鱼 唱歌 他的电话是7778888999” produces
`interests: ["钓鱼", "唱歌"]`; the phone is not part of an interest label.
Do not infer hobbies from “we discussed fishing”, negation, uncertain statements,
or another person's preferences. Put each person's hobbies on that person's
primary draft or nested relation, and deduplicate individual tags.

Include interests in create/merge drafts and update `addInterests`, show them
in the preview, and persist them with the confirmed customer change. Never say
that identified hobbies are retained only in the original text. Preserve the
existing precheck → preview → explicit save flow for customer-field changes.
For an existing customer with only interest additions or explicitly requested
notes, follow `customer_update_precheck` → `DIRECT_NOTE` → `customer_add_note`;
this appends tags, original communication and audit evidence without a preview.
If there are no structured changes, use `customer_record_communication`.

## 2. Extract the complete draft before calling tools

Preserve the user's complete original message as `sourceText`. Extract all facts into the draft instead of putting structured facts into a general note:

- primary customer: name, phone, email, gender and business signals;
- every third person: spouse, child, parent, colleague, boss, friend, or other named person;
- each person's phone/email, organization, job title, address, age and important dates;
- work and residence addresses separately;
- organizations and job titles;
- explicitly requested general notes and automatically identified interests;
- birthdays, anniversaries, holidays, and other important dates.

Treat explicit business language in the original narrative as a business
signal, even when it is not phrased as a CRM command. For example, “我们跟他
已经合作很多年了” / “we have worked together for many years” means
`hasBusiness=YES`; keep `isConnected` and `hasReferral` as `UNKNOWN` unless
the message explicitly states those facts. Preserve the sentence in
`sourceText`/notes as evidence, but do not let it remain note-only while the
classification is calculated.

“My wife”, “my boss”, or “their child” is a relation to extract, not a reason to ignore the person. If a relation person has no real name/contact, use the pending identity form (primary name + relation label) and preserve the relation description. Unambiguous kinship words must be normalized automatically (`老婆/妻子/wife` → `FAMILY` + `WIFE`, child/parent/spouse likewise); missing real names alone do not require confirmation. A generated label such as “Sunny 的老婆” is not a real identity search key and must not be matched by name to another customer's generated relation row. Only a real name/contact or an explicit `relatedCustomerId` participates in relation-person matching; one real candidate resolves automatically, while multiple candidates require user selection.

`customer_existence_check` is exclusively the primary-customer identity gate.
Never pass `includeRelatedPersons=true` for the primary person, even when the
draft contains spouse/child/colleague relations. Relation-person matching is
performed inside the create/update/merge prechecks with the related-person
scope; any relation match or conflict must still be resolved before the
primary customer's preview is shown.

### Normalization contract (send only persistable draft fields)

Use the field names accepted by `CustomerDraft`: `displayName`,
`firstName`, `lastName`, `gender`, `phones`, `emails`, `hasBusiness`,
`isConnected`, `hasReferral`, `employments`, `locations`, `relations`,
`notes`, `interests`, and `importantDates`. Preserve all supplied phone/email
values; multiple values are supported. Let the service normalize them. Keep
returned IDs as opaque strings, including numeric-looking CRM IDs. Preserve
existing fact IDs when editing; omission alone is not a deletion request.
Do not require users to provide database normalization fields.

Use only `YES`, `NO`, or `UNKNOWN` for the three business signals. Missing
knowledge is `UNKNOWN`, not `NO`; the server derives A/B/C/D. For dates use
`BIRTHDAY`, `ANNIVERSARY`, `FAMILY_BIRTHDAY`, `HOLIDAY`, or `OTHER`; a meeting
date is evidence in the original text, not an important-date row. For
relations use `COLLEAGUE`, `FRIEND`, `FAMILY`, `CAN_INTRODUCE`, `KNOWS`, or
`OTHER`, and preserve the relationship role (for example `WIFE`, `BOSS`,
`CHILD`) for confirmation.

For every normalized value preserve the user's original wording in
`sourceText`, `raw`/`raw_location_text`, or the relation description. Use
`null` for unknown facts and `UNKNOWN` only for the three business signals;
do not substitute empty strings or invented values.

For every address, always classify the address before calling a precheck. Use
the canonical location field `type` with one of `RESIDENCE`, `WORK`, or
`OTHER`; `RESIDENCE` covers Chinese phrases such as “住在”“他家在”“家庭住址”
and English phrases such as “lives in”“home is in”“based in” when they refer
to the person's home. `WORK` covers “工作地址”“办公地址” and “works in/at”.
The service also accepts the compatibility keys `location_type`,
`locationType`, and `addressType`, but the Agent should prefer `type`. Never
write a home/residence address as `OTHER` merely because the model omitted the
type: derive it from the original `sourceText`; if the wording is genuinely
ambiguous, ask the user to confirm the address type before previewing.

## 3. Customer create/update/merge routing

All checks below are UI-less. Do not open a page until the relevant precheck has passed.

### New or introduced customer

1. Call `customer_existence_check` with the normalized draft and the complete original `sourceText`. Name, phone, or email must provide at least one identity value. If it returns `RETRY_EXTRACTION`, copy the exact phone/email from `sourceCandidates` and retry without asking the user; never continue with a contact value that differs from the original message.
2. For `NOT_FOUND`, normalize and validate addresses/organizations, call `customer_create_precheck`, then `customer_prepare_create`. If the precheck itself returns `CONFLICT`, stop the create flow and follow its `targetCustomerId`/candidate-selection route into merge.
3. Only a result ready for preview may call `customer_create_preview`.
4. The preview is a draft only. It must not have saved the customer or created an operation log.
5. Save only after explicit intent such as “保存这个客户”, “创建并保存”, “save this customer”, or “create and save”. A standalone “确认/yes/confirm/好的” is not enough.
6. Call `customer_confirm_create` with the confirmation ID and explicit confirmation text.

### Existing customer

1. If exactly one customer is found in the default create/merge flow, call `customer_merge_precheck` → `customer_prepare_merge` → `customer_merge_preview`. The merge preview must show current values versus proposed values and offers both “confirm and save” and “create as a new customer”; do not open the update flow for this default merge case.
2. If several primary-customer candidates are found, or phone and email hit different primary customers, call `customer_query` with the check response's `queryHint`, `selectionMode="MERGE_TARGET"`, `selectionDraft`, `candidateIds`, and `sourceText` unchanged. Never add related-person IDs to this list. The list UI buttons then run the merge/create precheck and preview directly; do not send a synthetic instruction back to the chat. The list must show IDs and enough distinguishing fields (name, level, phone, email, company/title, address and match explanation). Ask the user to select a target, choose a new customer, or decline to merge; do not stop at a plain-text question when the list UI is available. Even if the filtered list contains one result, `MERGE_TARGET` must remain on the candidate/merge path and must not auto-open read-only detail.
3. After a target is selected, use the merge preview flow. The existing values are read-only; only proposed values may be edited.
4. Confirm only with explicit merge language, then call `customer_confirm_merge`.
5. If the user chooses a new customer from the merge preview or candidate list, restart the create precheck/prepare/preview flow with `allowNewCustomer=true`. Never save from the candidate list.

The single-target merge preview exposes two separate actions: “确认并保存”
commits the reviewed overwrite only after explicit save intent; “创建为新客户”
abandons the merge path and must restart `customer_create_precheck` with
`allowNewCustomer=true`, followed by the normal create prepare/preview flow.
The create-new action must never call `customer_confirm_merge` or write any
customer data by itself.

For a single exact or single fuzzy candidate, go directly to the before/after
merge preview; the preview itself provides the create-new alternative. For
multiple candidates, return every candidate's ID and summary and open the
customer-list UI so the user can choose a target, choose “create new”, or
decline. A phone hit and an email hit on different customers is always a
conflict; never auto-merge them.

### Explicit customer change

For a request that clearly targets one existing customer and changes persisted data, call
`customer_update_precheck` → `customer_prepare_update` → `customer_update_preview` →
`customer_confirm_update`. Show the current value and proposed value for every changed field;
do not let the user edit the historical/current side directly. Deleting a customer uses
`customer_prepare_remove` → `customer_remove_preview` → `customer_confirm_remove` and always
requires explicit confirmation. Restoring uses `customer_restore` only when the user explicitly
requests restoration; never infer it from a generic confirmation.

### Existing customer with no persistent change

If the message describes or discusses an existing customer but does not change any persisted CRM field, do not open a create or update page and do not create an operation log. Call `customer_record_communication` with the original text. The original record is shown from communications; field evidence remains based on operation logs.

## 4. Address and organization normalization

### Addresses

1. Normalize the user's location to the schema of `geo_locations` and call `geo_resolve` with the raw location string. Do not invent a `geoLocationId` or a new geo row.
2. A city-only address is allowed. The precheck enriches new or edited addresses through Google before preview; do not invent coordinates or bypass an enrichment error. Keep detailed street text in `addressLine` and preserve the returned Google snapshot/proof unchanged. Editing address text or components requires another precheck.
3. If `geo_resolve` returns `ok=false` with `ADDRESS_NOT_FOUND`, or a non-exact result, return the bilingual correction request and wait for a concrete address. Do not preview or save an unresolved location. The current service may return this as an error envelope rather than a normal `matchStatus` object; both forms mean “blocked”.
4. Use `type=WORK`, `type=RESIDENCE`, or `type=OTHER`. The service maps residence to CRM HOME. All customer addresses are displayed; there is no primary-address requirement or employment linkage. Repeated addresses are deduplicated. Do not replace an existing address solely because a new one has the same type; identify the selected address when editing or deleting.
5. Show the normalized display as one readable line, for example `US · New York · New York City`, while preserving the user's raw wording for evidence.

### Organizations

1. Standardize the company name and supply a top-level organization object using the MCP contract: `name`, `normalized_name`/`normalizedName`, `domain`, `aliases`, `description`, `industry`, `phone`, and `email`. Enrich these only when supported by evidence; optional company details must not block an otherwise valid customer.
2. Call `organization_existence_check` before the customer preview.
3. If found, reference the returned company ID. If not found, retain the standardized company and aliases in the draft; the service writes CRM `companies`/`company_aliases` only at confirmed customer save.
4. Use `domain`, not `website`. Do not require removed organization-only fields such as `registered_name`, `organization_type`, `parent_organization_id`, or company geographic fields. Customer address normalization is separate from company enrichment.

## 5. Precheck, preview, and confirmation invariants

- `customer_existence_check`, `organization_existence_check`, `geo_resolve`, and all `*_precheck` tools do not create UI resources or persist business data.
- `*_prepare_*` creates a confirmation draft only. It must not create a customer, organization, address, relation, note, or operation log.
- `*_preview` only renders the prepared draft.
- The confirmation page may attempt `customer_preview_sync` while the user edits
  fields. This is draft synchronization only (and may be unavailable); it is
  never a database commit. The only commit boundary remains a confirm tool.
- Only an explicit user save/create/update/merge/delete/restore instruction may call a confirm tool.
- If a precheck returns `NEED_MORE_INPUT`, `NEED_USER_CONFIRMATION`, `CONFLICT`, or `BLOCKED`, explain the exact issue in the user's language, ask only for the missing choice/value, then rerun the appropriate check.
- Never tell the user that data was saved merely because a preview or precheck succeeded.
- `customer_confirm_pending_operation` is the stable confirmation-page entry point. It dispatches CREATE, UPDATE, MERGE, REMOVE, and COMPOSITE using the preparation task; it still requires an explicit post-preview save/submit instruction (the UI uses `confirmationSource="UI"` and `confirmed=true`).

The MCP App keeps preview edits, sync revisions, and commit results inside the
page. Do not expect or request synthetic `beaconfire.crm` JSON events in the
conversation, and do not treat any page-generated context as a new user
instruction on the next turn. Continue from the actual tool result and only
send a chat message when the workflow explicitly requires a user choice or a
next MCP tool call.

## 6. Query, detail, recommendation, and location search

### Customer detail

For “查看/显示某客户”:

1. Call `customer_existence_check` first.
2. One unambiguous match → call `customer_get`; show the detail resource.
3. Multiple matches → show a candidate/list resource and ask the user to choose; do not expand a partial row as a substitute for detail.

### Explicit list query

Use `customer_query` only when the user explicitly asks to search/list customers. It supports name, phone, email, company, job title, address, level, business signals, interests and relations. One result should navigate to detail; multiple results remain a selectable list.

`customer_query` has a `customers` UI resource even when it returns one row. In
that one-row case, immediately follow `resolvedCustomerId`/`nextAction` with
`customer_get`; do not present the row as an inline partial-detail substitute.
Clicking any list card likewise calls `customer_get`.

### Position query

Use `position_query` for user-initiated position or job-opening searches that
are not scoped to one company. It applies content fuzzy matching (a `%q%`
contains match, not a prefix match) across the position title and the vendor,
client, and billing-vendor company names. `exPositionId` is an exact match on
the external sheet-sync ID and ignores `query`; combine it with `importSource`
when the same external ID can exist under several import sources. A
position-keyword message with an explicit search intent routes here; a position
request scoped to one specific company stays on the company-scoped tool.
`position_query` has a `position-search` UI resource; one result follows
`resolvedPositionId`/`nextAction` with `position_get`, and multiple results
remain a selectable list. Clicking any list card calls `position_get`.
Position tools are read-only; position create/update stays in the CRM
application.

### Recommendations and location search

- Use `customer_recommend` once to validate the conditions, query the ranked
  customers, and open the recommendation card UI. Do not call
  `customer_get` or `customer_recommend_view` before the cards are shown.
  `customer_recommend_view` is retained only as a compatibility alias for a
  server that explicitly returns it as `nextAction`; it is not part of the
  normal sequence.
- Conditions are ANDed: location, company, job title, level, business, connected, referral, and interest.
- Default recommendation count is 3; use the user's requested count when supplied.
- Use `customer_location_search` or `customer_location_results` for a normalized location and include matches from both customer addresses and relation-person addresses.
- `customer_location_search` is the UI-less gate. Only after an exact match
  call `customer_location_results`; an unknown location is a correction prompt,
  not an empty result page.
- Cards should show name, level, phone, address, work organization/job title, and a concise explanation of what matched. Clicking a card goes to `customer_get` detail.

## 7. Relationships, notes, level, and reminders

- Use the shared `contacts` table for the primary customer and relation people, distinguished by `customer_kind`.
- Persist both directions of a confirmed customer relationship.
- Write only explicit notes or identified interests to `contact_notes`; use `GENERAL` or `INTEREST`. Do not put employment, meeting facts, age, education, or address facts in notes.
- Customer level is calculated from `has_business`, `is_connected`, and `has_referral`. All unknown defaults to `D`; business only is `B`, connected only is `C`, and stronger combinations follow the server classification rules. Do not let the user directly edit the level.
- Reminders have two independent outputs. First extract a concrete future
  date/time from the user's request and send it as `remindAt` (ISO-8601 with
  an explicit offset) plus `timezone` (IANA, for example `Asia/Shanghai` or
  `America/New_York`). For example, with the current date 2026-08-28,
  “明天下午五点提醒我联系 Provine” becomes
  `2026-08-29T17:00:00+08:00`. Pass the complete original sentence as
  `sourceText` too. If the user does not specify a time, or only says “明天”
  / “下午” without a clock time, stop at `reminder_precheck` and ask for the
  exact time; never silently use the current time. Then use `reminder_create`
  to persist the CRM reminder; the reminder owner is the authenticated user
  when unspecified. After the MCP result returns `status=COMMITTED`, you MUST
  immediately create the corresponding one-time notification with the host
  Claude/native notification, calendar, automation, or scheduled-task
  capability. This is a second required action, not an optional suggestion
  and not a follow-up to skip on mobile. Use the exact
  `hostNotification.scheduleAt`, timezone, reminder content, CRM reminder ID,
  and customer name when available. Do not end the turn after
  `reminder_create` and do not claim the reminder is fully set until the host
  notification call has succeeded. Report the CRM reminder ID and host
  notification result separately. A successful CRM
  insert is not a delivered notification, and a failed host notification does
  not undo the CRM record. If the host has no notification capability, report
  it as unavailable instead of claiming success.

  A mobile/voice shortcut uses the same UI-less sequence: route the natural
  language request, fill defaults, call `reminder_precheck`, ask only for
  missing or ambiguous values, then call `reminder_create` and the host
  notification capability. No confirmation page is required for this simple
  reminder record; do not bypass the precheck or invent a delivery time.
  For host-specific scheduling and duplicate-recovery rules, read
  [references/host-reminders.md](references/host-reminders.md) after the CRM
  reminder has been committed.

`customer_remove` is a legacy direct-delete tool and must not be used for a
normal chat request. Use `customer_prepare_remove` →
`customer_remove_preview` → `customer_confirm_remove`. `customer_restore` is a
direct restore operation and is valid only when the user explicitly asks to
restore a soft-deleted record. `task_cancel` only cancels an unfinished
preview and never writes customer data.

## 8. Evidence, originals, and language

- Preserve the complete original user text and its line breaks.
- Field evidence comes from the latest matching `operation_log_items` row, then the related task's `task_evidence_items` ordered newest first. A missing before/after value is displayed as `-`, not “not recorded”.
- Original records come from `contact_communications` and show only original text plus time.
- Use English UI labels and messages when the user's input is English; use Chinese for Chinese input. Never mix Chinese button labels into an English flow.
- Do not expose OAuth tokens, secrets, Authorization headers, internal database credentials, or fabricated operation IDs.

## 9. Intent examples

| User message | Required first route and continuation |
| --- | --- |
| “今天见了张三，他是 Google 的 CTO。” | `crm_message_route` → `customer_existence_check` → create or single/multiple-target merge flow |
| “查看 Provine 的客户资料。” | `crm_message_route` → `customer_existence_check` → one: `customer_get`; many: candidate selection |
| “列出纽约 Google 的客户。” | `crm_message_route` → `customer_query` → one: `customer_get`; many: selectable list |
| “查一下 Intuit 在招的职位。” | `crm_message_route` → `position_query` → one: `position_get`; many: selectable list |
| “推荐 5 个纽约、已建联的客户。” | `crm_message_route` → `customer_recommend` → cards; click a card → `customer_get` |
| “提醒我明天联系 Provine。” | `crm_message_route` → `reminder_precheck` → `reminder_create` |
| “创建 Provine 客户，并创建一个提醒。” | `crm_message_route` → `composite_prepare` → `composite_preview` → explicit confirmation → `composite_confirm`/pending-operation |
| “只总结这段会谈，不要录入 CRM。” | `crm_message_route` → `skipCrm=true`; do not call CRM write/read tools |
