---
name: staffing
description: Use the user-connected Beaconfireinc Marketing System MCP (`staffing_*` tools) to look up or change staffing data for a candidate (学员) by name, Candidate ID (CAN-xxxxx), Interview ID (INT-xxxx) or Onboarding ID (ONB-xxxx). Covers eight requests - (0) look up a candidate's interviews, how many there are and their results and scores, or one interview by its ID (查询面试/面试结果/某人有几个面试), read only, (1) change an interview's time, result or score, including Need to Reschedule (改面试时间/面试结果/面试评分), (2) create an onboarding record when a candidate got an offer, including right after one or several L2 interviews are set to Passed, and find candidates who passed L2 without one (创建 onboarding/L2 通过建 onboarding), (3) set or change the onboarding start date (改入职时间), (4) update candidate information such as name, email, location, work authorization, level, years of experience or rate, and the onboarding profile including SSN last 4, date of birth and address (修改学员信息/SSN/生日/地址), (5) create interview slots in bulk, put one or several candidates on slots in one go, release or cancel slots (批量创建/批量占用/释放面试 Slot), (6) permanently delete a candidate, interview or onboarding record that was created from wrong data (删除候选人/面试/Onboarding), (7) process the mailbox or read the client chat group right now, after a preview (立即处理邮件/读取客户群消息). Always resolve to exactly one record; for a write, show the before and after values and wait for explicit confirmation.
---

# Staffing lookups and changes

Use only the `staffing_*` tools of the connected `marketing-system` MCP server. Do not call the REST API, SQL, scripts or another plugin, and never invent IDs, versions or option values. If the tools are not visible, report a connection problem instead of guessing.

## Pick the workflow

| The user wants | Read this reference |
| --- | --- |
| Look up interviews: one candidate's interviews and results, one interview by ID, or a schedule by round and date (read only) | `references/interview.md` (Looking up interviews) |
| Change an interview's date, time, time zone, result, score, link, recruiter, interviewer or notes | `references/interview.md` |
| Record that a candidate got an offer, or find candidates who passed L2 and have no onboarding record yet | `references/onboarding-create.md` |
| Set, change or clear the start date | `references/onboarding-start-date.md` |
| Change candidate information | `references/candidate.md` |
| Create interview slots, put one or several candidates on slots, release or cancel slots, or reschedule after Need to Reschedule | `references/slots.md` |
| Delete a candidate, an interview or an onboarding record created from wrong data | `references/delete.md` |
| Process the mailbox or read the client chat group now | `references/ingest.md` |

One message may contain several requests; handle them one at a time, each with its own confirmation. **The exception is a batch of the same slot action** (creating slots for several recruiters, or putting several candidates on slots): that gets one confirmation table for the whole batch, as described in `references/slots.md`.

## Rules for every workflow

1. **Resolve to exactly one record first.**
   - A Candidate ID (`CAN-…`) goes straight to `staffing_get_candidate`.
   - A name goes to `staffing_search_candidates` (words in any order, case and single letters ignored). If more than one candidate matches, or the match is not clearly the person, list the candidates (ID, name, email, current status) and ask which one. Never pick for the user.
   - An Interview ID (`INT-…`) goes to `staffing_get_interview`. If it is not found, ask for the candidate's name or ID. If the server does not offer `staffing_get_interview` yet, find the code with `staffing_list_interviews` (`limit=500`).
   - An Onboarding ID (`ONB-…`) goes to `staffing_get_onboarding`.
2. **Read before writing.** Every update needs the current `version` from the record you just read. If a write is rejected as stale, read again, tell the user what changed, and ask again before retrying.
3. **Validate choices.** Call `staffing_list_options` once and only use its values for results, rounds, interview times, time zones, recruiters, states, work authorizations and levels. Interview times are fixed dropdown values (for example `5:15 PM`); if the user gives a time that is not in the list, show the nearest allowed values and ask.
4. **Confirm before every write.** When a tool has a `dry_run` (creating slots, holding slots), use it to build the confirmation table from what the server says it will do, then send the same request without `dry_run` after the yes. Show a short table of `field: old → new` for the one record (a batch of slot actions: one table with a row per item), say which tool will run, and wait for a clear yes. A question, a correction or silence is not a yes. Only send the fields being changed.
5. **Report the result honestly.** After the write, restate what was saved from the tool's response (IDs, new values, resulting status). If the tool returns an error, show the message and do not claim success or retry silently.
6. **Time and dates.** Interview times are business time (US Eastern, labelled `EST`) unless the user names another zone. Dates are `YYYY-MM-DD`; resolve relative dates ("next Monday") against today and show the exact date for confirmation.
7. **Onboarding profile.** Name as on ID, address, phone, date of birth, gender, SSN last 4 and the rest of the profile are read and changed like any other field: read them with `staffing_get_candidate` and `include_profile=true` whenever the request is about them (always before changing them), and show `old → new` values in the confirmation. Only the last 4 digits of the SSN are stored: if the user gives a full SSN, say that only the last 4 will be saved. The change history shows these fields as `changed`, without values.
8. **Derived fields.** Offer Status, Start Date and Current Status are computed from the onboarding record, the interviews and held slots (`L1 Slot Held` / `L2 Slot Held` while a candidate holds a slot with no interview yet). Never try to set them on the candidate or an interview; use the onboarding workflows.
9. **History.** Every write is recorded with who, when and what changed. When the user asks "who changed this" or "what changed", use `staffing_get_history`.
10. **L2 Passed means an offer is next.** Whenever an interview write (`staffing_update_interview` or `staffing_create_interview`) returns `onboarding_suggestion`, do not end with the interview: in the same reply ask whether to create the onboarding record, with the suggested offer date, and follow `references/onboarding-create.md` on a yes. In a batch, collect the suggestions of every interview and ask once with one row per candidate. Candidates who passed L2 earlier and still have no onboarding record are found with `staffing_search_candidates` and `status` `L2 Passed`.
