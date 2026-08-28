---
name: crm-copilot-v3
description: Use the Beaconfireinc CRM Copilot V3 MCP for customer introductions, customer lookup, creation, updates, merges, relationships, address and organization normalization, recommendations, reminders, and evidence. Always follow the server-side check, preview, and explicit-confirmation workflow.
---

# CRM Copilot V3

Use the `crm-copilot` MCP server as the only source of truth for CRM work. Do not use direct REST calls, the admin API, SQL, shell scripts, invented customer IDs, or a different CRM plugin to complete a chat request.

The MCP server is authoritative for the database contract, but the Agent is
responsible for extracting intent and following the returned `nextAction`. The
tool names and UI boundaries below are the V3 QA contract (not hypothetical
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
| Originals/evidence | `customer_record_communication`, `customer_field_evidence`, `customer_evidence_get` | none |

The confirmation UI currently tries `customer_confirm_pending_operation` first
and falls back to `customer_confirm_create`, `customer_confirm_update`, or
`customer_confirm_merge`. For a UI save, pass the current `confirmationId`,
`confirmationSource="UI"`, `confirmed=true`, the current editable
`finalPayload`, and (when present) `expectedRevision`. A successful save must
return the persisted `customerId` (for create/update/merge) or a persisted
`operationId`/record status; otherwise report failure and never say “saved”.

## 1. Route every CRM-relevant message

Call `crm_message_route` first for:

- a person introduction, meeting/visit report, or customer fact;
- a request to create, update, merge, remove, restore, or view a customer;
- a reminder request;
- a recommendation request;
- a customer search or location search;
- a message containing more than one CRM operation.

Default behavior is CRM recording. Skip CRM only when the user explicitly says things such as “只总结，不要录入”, “不要保存到 CRM”, “just summarize”, or “do not record this”. A vague discussion, analysis request, or question about the system is not an opt-out.

Infer the conversation locale before routing and pass it to every tool as
`locale="en-US"` for English or `locale="zh-CN"` for Chinese. Do not rely on
the server's default locale, because it is Chinese when `locale` is omitted.

If the route returns `COMPOSITE`, extract the operations and call
`composite_prepare`; do not silently drop one operation. The current V3
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

## 2. Extract the complete draft before calling tools

Preserve the user's complete original message as `sourceText`. Extract all facts into the V3 draft instead of putting structured facts into a general note:

- primary customer: name, phone, email, gender and business signals;
- every third person: spouse, child, parent, colleague, boss, friend, or other named person;
- each person's phone/email, organization, job title, address, age and important dates;
- work and residence addresses separately;
- organizations and job titles;
- explicit notes and interests only;
- birthdays, anniversaries, holidays, and other important dates.

“My wife”, “my boss”, or “their child” is a relation to extract, not a reason to ignore the person. If a relation person has no name/contact, use the required pending identity form (primary name + relation label) and preserve the relation description for later confirmation.

When checking a relation person against existing records, call
`customer_existence_check` with `includeRelatedPersons=true`; the default
identity check searches primary customers only. A relation-person match or
conflict must be resolved before the primary customer's preview is shown.

### Normalization contract (send only persistable draft fields)

Use the V3 field names accepted by `CustomerDraft`: `displayName`,
`firstName`, `lastName`, `gender`, `phones`, `emails`, `hasBusiness`,
`isConnected`, `hasReferral`, `employments`, `locations`, `relations`,
`notes`, `interests`, and `importantDates`. A phone/email array must contain
at most one value at final save. Keep the readable `phone`/`email` and let the
server derive `phone_normalized`/`email_normalized`; likewise never ask the
user to edit `display_name_normalized`.

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

## 3. Customer create/update/merge routing

All checks below are UI-less. Do not open a page until the relevant precheck has passed.

### New or introduced customer

1. Call `customer_existence_check` with the normalized draft. Name, phone, or email must provide at least one identity value.
2. For `NOT_FOUND`, normalize and validate addresses/organizations, call `customer_create_precheck`, then `customer_prepare_create`. If the precheck itself returns `CONFLICT`, stop the create flow and follow its `targetCustomerId`/candidate-selection route into merge.
3. Only a result ready for preview may call `customer_create_preview`.
4. The preview is a draft only. It must not have saved the customer or created an operation log.
5. Save only after explicit intent such as “保存这个客户”, “创建并保存”, “save this customer”, or “create and save”. A standalone “确认/yes/confirm/好的” is not enough.
6. Call `customer_confirm_create` with the confirmation ID and explicit confirmation text.

### Existing customer

1. If exactly one customer is found, call `customer_merge_precheck` and `customer_prepare_merge` to show a field-level current value versus proposed value preview. Do not ask “same person or new?” again.
2. If several candidates are found, or phone and email hit different customers, show the candidate list with IDs and distinguishing fields. Ask the user to select a target, choose a new customer, or decline to merge.
3. After a target is selected, use the same merge preview flow. The existing values are read-only; only proposed values may be edited.
4. Confirm only with explicit merge/update language, then call `customer_confirm_merge`.
5. If the user chooses a new customer, restart the create precheck/prepare/preview flow. Never save from the candidate list.

The single-target merge preview exposes two separate actions: “确认并保存”
commits the reviewed overwrite only after explicit save intent; “创建为新客户”
abandons the merge path and must restart `customer_create_precheck` with
`allowNewCustomer=true`, followed by the normal create prepare/preview flow.
The create-new action must never call `customer_confirm_merge` or write any
customer data by itself.

For a single exact or single fuzzy candidate, the candidate list is not a
separate user-choice page: go directly to the before/after merge preview. For
multiple candidates, return every candidate's ID and summary and wait for the
user to choose a target, choose “create new”, or decline. A phone hit and an
email hit on different customers is always a conflict; never auto-merge them.

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
2. If the city-level location is found, a city-only address may be saved. If a street cannot be normalized, keep the complete confirmed street text in `address_line`.
3. If `geo_resolve` returns `ok=false` with `ADDRESS_NOT_FOUND`, or a non-exact result, return the bilingual correction request and wait for a concrete address. Do not preview or save an unresolved location. The current service may return this as an error envelope rather than a normal `matchStatus` object; both forms mean “blocked”.
4. Use `location_type=WORK` and `location_type=RESIDENCE` correctly. A customer has one current work address; a repeated address is deduplicated and a new work address replaces the old one.
5. Show the normalized display as one readable line, for example `US · New York · New York City`, while preserving the user's raw wording for evidence.

### Organizations

1. Produce a complete organization candidate matching the `organizations` table, including canonical name, normalized name, type, domain, country, state/province, city and address when known. Send these fields at the top level of the `organization` argument (`name`, `normalized_name`, `registered_name`, `organization_type`, `parent_organization_id`, `domain`, `country_code`, `state_or_province`, `district_or_county`, `city`, `address_line`, `geo_location_id`); do not wrap them only in a `normalized_candidate` object.
2. Call `organization_existence_check` before the customer preview.
3. If found, reference the existing organization. If not found, keep the normalized organization in the draft; the server creates it only during the final confirmed customer write.
4. Never send generic values such as `COMPANY` when the schema expects `HEADQUARTERS`, `SUBSIDIARY`, `BRANCH`, `OFFICE`, or `OTHER`.
5. Do not create or expect an `organization_relations` record. Organization
   hierarchy, when explicitly stated and confirmed, is represented only by
   `organization_type` and `parent_organization_id` on `organizations`.

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

### Recommendations and location search

- Use `customer_recommend` once to validate the conditions, query the ranked
  customers, and open the recommendation card UI. Do not call
  `customer_get` or `customer_recommend_view` before the cards are shown.
  `customer_recommend_view` is retained only as a compatibility alias for a
  server that explicitly returns it as `nextAction`; it is not part of the
  normal V3 sequence.
- Conditions are ANDed: location, company, job title, level, business, connected, referral, and interest.
- Default recommendation count is 3; use the user's requested count when supplied.
- Use `customer_location_search` or `customer_location_results` for a normalized location and include matches from both customer addresses and relation-person addresses.
- `customer_location_search` is the UI-less gate. Only after an exact match
  call `customer_location_results`; an unknown location is a correction prompt,
  not an empty result page.
- Cards should show name, level, phone, address, work organization/job title, and a concise explanation of what matched. Clicking a card goes to `customer_get` detail.

## 7. Relationships, notes, level, and reminders

- Use the shared `customers` table for the primary customer and relation people, distinguished by `customer_kind`.
- Persist both directions of a confirmed customer relationship.
- Write only explicit notes or identified interests to `customer_notes`; use `GENERAL` or `INTEREST`. Do not put employment, meeting facts, age, education, or address facts in notes.
- Customer level is calculated from `has_business`, `is_connected`, and `has_referral`. All unknown defaults to `D`; business only is `B`, connected only is `C`, and stronger combinations follow the server classification rules. Do not let the user directly edit the level.
- Reminders are database records only. Use `reminder_precheck` then `reminder_create`; default `remind_at` is the current time and the reminder owner is the authenticated user when unspecified. Do not claim a real notification was delivered.

`customer_remove` is a legacy direct-delete tool and must not be used for a
normal chat request. Use `customer_prepare_remove` →
`customer_remove_preview` → `customer_confirm_remove`. `customer_restore` is a
direct restore operation and is valid only when the user explicitly asks to
restore a soft-deleted record. `task_cancel` only cancels an unfinished
preview and never writes customer data.

## 8. Evidence, originals, and language

- Preserve the complete original user text and its line breaks.
- Field evidence comes from the latest matching `operation_log_items` row, then the related task's `task_evidence_items` ordered newest first. A missing before/after value is displayed as `-`, not “not recorded”.
- Original records come from `customer_communications` and show only original text plus time.
- Use English UI labels and messages when the user's input is English; use Chinese for Chinese input. Never mix Chinese button labels into an English flow.
- Do not expose OAuth tokens, secrets, Authorization headers, internal database credentials, or fabricated operation IDs.

## 9. Intent examples

| User message | Required first route and continuation |
| --- | --- |
| “今天见了张三，他是 Google 的 CTO。” | `crm_message_route` → `customer_existence_check` → create or single/multiple-target merge flow |
| “查看 Provine 的客户资料。” | `crm_message_route` → `customer_existence_check` → one: `customer_get`; many: candidate selection |
| “列出纽约 Google 的客户。” | `crm_message_route` → `customer_query` → one: `customer_get`; many: selectable list |
| “推荐 5 个纽约、已建联的客户。” | `crm_message_route` → `customer_recommend` → cards; click a card → `customer_get` |
| “提醒我明天联系 Provine。” | `crm_message_route` → `reminder_precheck` → `reminder_create` |
| “创建 Provine 客户，并创建一个提醒。” | `crm_message_route` → `composite_prepare` → `composite_preview` → explicit confirmation → `composite_confirm`/pending-operation |
| “只总结这段会谈，不要录入 CRM。” | `crm_message_route` → `skipCrm=true`; do not call CRM write/read tools |
