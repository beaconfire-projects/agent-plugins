# Change an interview's time or result

Tools: `staffing_search_candidates`, `staffing_get_candidate`, `staffing_list_interviews`, `staffing_list_options`, `staffing_update_interview`, `staffing_create_interview`. For slots (a recruiter's free times) use `references/slots.md`.

## Looking up interviews (read only)

To answer "who is interviewing today", "tomorrow's L1s" or "this week's L2 results", call `staffing_list_interviews` with the filters instead of reading candidates one by one:

- `round`: `L1` or `L2`.
- `date_from` and `date_to`: the interview date as written on the interview. For "today" use today's date in **US Eastern time** for both. With `date_from` the list comes back in time order (a schedule, oldest first); without it the newest come first.
- `result` (for example `Scheduled`, `Need to Reschedule`) and `recruiter` (a name from `staffing_list_options`) narrow it further.
- Show a compact table (interview ID, candidate, round, date and time with zone, recruiter, result) and say how many there are. Do not change anything from a lookup.

## Steps

1. **Find the interview.**
   - Interview ID given: locate it with `staffing_list_interviews`.
   - Name or Candidate ID given: `staffing_get_candidate` returns the candidate's interviews with their `version`. If the user names a round (L1 or L2), use it. If the candidate has several interviews and the request does not say which one, list them (ID, round, date and time, result, source) and ask.
   - Several interviews can share a round when earlier ones were canceled or ended as Need to Reschedule. "The L2" means the latest one that is neither Canceled nor Need to Reschedule; if more than one qualifies, ask.
2. **Work out the change.** Fields: `interview_date`, `interview_time`, `time_zone`, `result`, `meeting_link`, `recruiter`, `notes`.
   - Results: Scheduled, Pending Feedback, Passed, Failed, No-show, Need to Reschedule, Canceled (use `staffing_list_options` for the exact list).
   - **Need to Reschedule** is a final result like Passed and Failed: the interview did not pass or did not happen, but the candidate is still good and can be tried again. The candidate's status becomes `Need to Reschedule`.
   - A time needs a date and a time zone to mean anything. If the user changes only the time, keep the existing date and zone and say so in the confirmation.
3. **Check the situation before confirming**:
   - The interview is **Canceled** and the user gives a new date or time: this is a reschedule, which is a **new interview**. Do not edit the canceled one. Create one with `staffing_create_interview` (`candidate_code`, `round`, date, time, zone, `result` Scheduled) and tell the user the canceled one stays as history.
   - The interview already has an outcome (Passed, Failed, No-show) and the user changes the time: ask whether they mean to correct the record; do not change the result silently.
   - A result of Passed or Failed moves the candidate's status (for example L2 Passed). Mention the resulting status in the confirmation.
   - The interview is **Need to Reschedule** and the user gives a new date or time: this is a retry, which is a **new interview** (same as a canceled one). Create it with `staffing_create_interview`; the old one stays as history. A retried L1 may use another recruiter; a retried L2 must keep the L1's recruiter.
   - A **Canceled** result set by hand means the interview did not happen; if it will be rescheduled, offer to create the new interview too.
   - If the interview source is `email` (it came from a calendar invitation), say so: a later invitation update can change the time again.
4. **Confirm** with `field: old → new`, then call `staffing_update_interview` with `code` and `changes` (`version` plus only the changed fields). Clear a field only when asked, by sending `null`.
5. **Report** the saved interview and the candidate's current status.

## Do not

- Do not create a second live interview for the same round; the system rejects it. Cancel or update the existing one. (An interview that is Canceled or Need to Reschedule does not count as live.)
- Do not change the round of an existing interview unless the user says it was recorded in the wrong round.
