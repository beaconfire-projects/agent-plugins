# Change an interview's time, result or score

Tools: `marketing_search_candidates`, `marketing_get_candidate`, `marketing_get_interview`, `marketing_list_interviews`, `marketing_list_options`, `marketing_update_interview`, `marketing_create_interview`. For slots (a recruiter's free times) use `references/slots.md`; to delete an interview created from wrong data use `references/delete.md`.

## Looking up interviews (read only)

### One candidate's interviews ("how many interviews does A have, and how did they go")

1. Resolve the candidate as in the SKILL rules: a Candidate ID goes to `marketing_get_candidate`; a name goes to `marketing_search_candidates` first, and if several candidates match, list them (ID, name, email, current status) and ask which one. Never merge the interviews of two people with the same name.
2. `marketing_get_candidate` returns all of the candidate's interviews. Reply with:
   - one line: the candidate (ID, name), the current status, and the count, for example "3 interviews: L1 Passed, L2 Canceled, L2 Scheduled";
   - a table, oldest first: interview ID, round, date and time with zone, recruiter, interviewer, result, score. Empty values show as `-`.
   - Canceled and Need to Reschedule interviews are history, not the current attempt: keep them in the table and count, and say which interview is the live one for each round.
3. If the user asked only about one round or one result, answer that and leave the rest out of the table.

### One interview by ID

`marketing_get_interview` with the `INT-…` code returns the interview with its candidate, result, score and version. If the code is not found, say so and ask for the candidate's name or ID.

### Schedules by round and date

To answer "who is interviewing today", "tomorrow's L1s" or "this week's L2 results", call `marketing_list_interviews` with the filters instead of reading candidates one by one:

- `round`: `L1` or `L2`.
- `date_from` and `date_to`: the interview date as written on the interview. For "today" use today's date in **US Eastern time** for both. With `date_from` the list comes back in time order (a schedule, oldest first); without it the newest come first.
- `result` (for example `Scheduled`, `Need to Reschedule`) and `recruiter` (a name from `marketing_list_options`) narrow it further.
- Show a compact table (interview ID, candidate, round, date and time with zone, recruiter, result) and say how many there are. Do not change anything from a lookup.

## Steps

1. **Find the interview.**
   - Interview ID given: read it with `marketing_get_interview`.
   - Name or Candidate ID given: `marketing_get_candidate` returns the candidate's interviews with their `version`. If the user names a round (L1 or L2), use it. If the candidate has several interviews and the request does not say which one, list them (ID, round, date and time, result, source) and ask.
   - Several interviews can share a round when earlier ones were canceled or ended as Need to Reschedule. "The L2" means the latest one that is neither Canceled nor Need to Reschedule; if more than one qualifies, ask.
2. **Work out the change.** Fields: `interview_date`, `interview_time`, `time_zone`, `result`, `score`, `meeting_link`, `recruiter`, `interviewer`, `notes`.
   - **Interviewer** is the client's evaluator (the Evaluator named in the client chat feedback). The system fills it from the chat feedback when it is empty and never replaces one set by hand, so set it yourself only when the user gives a name, and do not confuse it with the recruiter (the person whose invitation created the interview).
   - Results: Scheduled, Pending Feedback, Passed, Failed, No-show, Need to Reschedule, Canceled (use `marketing_list_options` for the exact list).
   - **Need to Reschedule** is a final result like Passed and Failed: the interview did not pass or did not happen, but the candidate is still good and can be tried again. The candidate's status becomes `Need to Reschedule`.
   - **Score** is `score/maximum`, for example `9/10`, `7.5/10`, `12/12` (the maximum is not always 10). It is optional, but **whenever you record a final result (Passed, Failed, No-show, Need to Reschedule) and the interview has no score and the user did not give one, ask for it before you write**: "What was the interview score (like 9/10)? Reply "none" if there isn't one." Ask once, together with anything else you still need. If the user says there is no score, leave it out and do not ask again. If the user gives a score without a result, write the score only; do not invent a result. A saved reply that carries a "No score is recorded" warning means you skipped this question: ask now and update the interview.
   - A time needs a date and a time zone to mean anything. If the user changes only the time, keep the existing date and zone and say so in the confirmation.
3. **Check the situation before confirming**:
   - The interview is **Canceled** and the user gives a new date or time: this is a reschedule, which is a **new interview**. Do not edit the canceled one. Create one with `marketing_create_interview` (`candidate_code`, `round`, date, time, zone, `result` Scheduled) and tell the user the canceled one stays as history.
   - The interview already has an outcome (Passed, Failed, No-show) and the user changes the time: ask whether they mean to correct the record; do not change the result silently.
   - A result of Passed or Failed moves the candidate's status (for example L2 Passed). Mention the resulting status in the confirmation.
   - The interview is **Need to Reschedule** and the user gives a new date or time: this is a retry, which is a **new interview** (same as a canceled one). Create it with `marketing_create_interview`; the old one stays as history. A retried L1 may use another recruiter; a retried L2 must keep the L1's recruiter.
   - A **Canceled** result set by hand means the interview did not happen; if it will be rescheduled, offer to create the new interview too.
   - If the interview source is `email` (it came from a calendar invitation), say so: a later invitation update can change the time again.
4. **Confirm** with `field: old → new` (include the score when one is given or changes), then call `marketing_update_interview` with `code` and `changes` (`version` plus only the changed fields). Clear a field only when asked, by sending `null`.
5. **Report** the saved interview and the candidate's current status. If the reply has `onboarding_suggestion` (the candidate just passed L2 and has no onboarding record), do not ask: call `marketing_create_onboarding` right away with the suggested offer date (see `references/onboarding-create.md`) and report the new Onboarding ID together with the interview.

## Several interviews at once

When the user gives results for several interviews in one message (for example "these four passed L2"), resolve each one, show one confirmation table with a row per interview (interview ID, candidate, round, `result: old → new`, score), ask for any missing scores once, and after the yes update them one by one. Then report one table of what was saved. **Every reply that carried `onboarding_suggestion` gets its onboarding record created right away, without a follow-up question**: one `marketing_create_onboarding` per candidate with the suggested offer date, one at a time. Add the Onboarding ID and offer date to the report table (or the error, if one failed; keep going with the others).

## Do not

- Do not create a second live interview for the same round; the system rejects it. Cancel or update the existing one. (An interview that is Canceled or Need to Reschedule does not count as live.)
- Do not guess a score, and do not turn a note like "strong performance" into one. Only write a score the user states.
- Do not change the round of an existing interview unless the user says it was recorded in the wrong round.
