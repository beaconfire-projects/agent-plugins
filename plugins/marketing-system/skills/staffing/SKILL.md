---
name: staffing
description: Use the user-connected Beaconfireinc Marketing System MCP (`staffing_*` tools) to change staffing data for a candidate (学员) by name, Candidate ID (CAN-xxxxx), Interview ID (INT-xxxx) or Onboarding ID (ONB-xxxx). Covers four requests - (1) change an interview's time or result (改面试时间/面试结果), (2) create an onboarding record when a candidate got an offer (创建 onboarding), (3) set or change the onboarding start date (改入职时间), (4) update candidate information such as name, email, location, work authorization, level, years of experience or rate (修改学员信息). Always resolve to exactly one record, show the before and after values, and wait for explicit confirmation before any write.
---

# Staffing changes

Use only the `staffing_*` tools of the connected `marketing-system` MCP server. Do not call the REST API, SQL, scripts or another plugin, and never invent IDs, versions or option values. If the tools are not visible, report a connection problem instead of guessing.

## Pick the workflow

| The user wants | Read this reference |
| --- | --- |
| Change an interview's date, time, time zone, result, link, recruiter or notes | `references/interview.md` |
| Record that a candidate got an offer | `references/onboarding-create.md` |
| Set, change or clear the start date | `references/onboarding-start-date.md` |
| Change candidate information | `references/candidate.md` |

One message may contain several requests; handle them one at a time, each with its own confirmation.

## Rules for every workflow

1. **Resolve to exactly one record first.**
   - A Candidate ID (`CAN-…`) goes straight to `staffing_get_candidate`.
   - A name goes to `staffing_search_candidates` (words in any order, case and single letters ignored). If more than one candidate matches, or the match is not clearly the person, list the candidates (ID, name, email, current status) and ask which one. Never pick for the user.
   - An Interview ID (`INT-…`) has no direct lookup: find it with `staffing_list_interviews` (add `candidate_code` when known, otherwise `limit=500` and match the code). If it is not found, ask for the candidate's name or ID.
   - An Onboarding ID (`ONB-…`) goes to `staffing_get_onboarding`.
2. **Read before writing.** Every update needs the current `version` from the record you just read. If a write is rejected as stale, read again, tell the user what changed, and ask again before retrying.
3. **Validate choices.** Call `staffing_list_options` once and only use its values for results, rounds, interview times, time zones, recruiters, states, work authorizations and levels. Interview times are fixed dropdown values (for example `5:15 PM`); if the user gives a time that is not in the list, show the nearest allowed values and ask.
4. **Confirm before every write.** Show a short table of `field: old → new` for the one record, say which tool will run, and wait for a clear yes. A question, a correction or silence is not a yes. Only send the fields being changed.
5. **Report the result honestly.** After the write, restate what was saved from the tool's response (IDs, new values, resulting status). If the tool returns an error, show the message and do not claim success or retry silently.
6. **Time and dates.** Interview times are business time (US Eastern, labelled `EST`) unless the user names another zone. Dates are `YYYY-MM-DD`; resolve relative dates ("next Monday") against today and show the exact date for confirmation.
7. **Sensitive data.** The onboarding profile (SSN last 4, date of birth, address, phone, gender) is only read or written when the user explicitly asks for it, and its values are not repeated in the reply or in later summaries.
8. **Derived fields.** Offer Status, Start Date and Current Status are computed from the onboarding record and the interviews. Never try to set them on the candidate or an interview; use the onboarding workflows.
9. **History.** Every write is recorded with who, when and what changed. When the user asks "who changed this" or "what changed", use `staffing_get_history`.
