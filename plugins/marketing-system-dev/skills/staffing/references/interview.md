# Change an interview's time or result

Tools: `staffing_search_candidates`, `staffing_get_candidate`, `staffing_list_interviews`, `staffing_list_options`, `staffing_update_interview`, `staffing_create_interview`.

## Steps

1. **Find the interview.**
   - Interview ID given: locate it with `staffing_list_interviews`.
   - Name or Candidate ID given: `staffing_get_candidate` returns the candidate's interviews with their `version`. If the user names a round (L1 or L2), use it. If the candidate has several interviews and the request does not say which one, list them (ID, round, date and time, result, source) and ask.
   - Several interviews can share a round when earlier ones were canceled. "The L2" means the one that is not Canceled; if there is more than one that is not Canceled, ask.
2. **Work out the change.** Fields: `interview_date`, `interview_time`, `time_zone`, `result`, `meeting_link`, `recruiter`, `notes`.
   - Results: Scheduled, Pending Feedback, Passed, Failed, No-show, Canceled (use `staffing_list_options` for the exact list).
   - A time needs a date and a time zone to mean anything. If the user changes only the time, keep the existing date and zone and say so in the confirmation.
3. **Check the situation before confirming**:
   - The interview is **Canceled** and the user gives a new date or time: this is a reschedule, which is a **new interview**. Do not edit the canceled one. Create one with `staffing_create_interview` (`candidate_code`, `round`, date, time, zone, `result` Scheduled) and tell the user the canceled one stays as history.
   - The interview already has an outcome (Passed, Failed, No-show) and the user changes the time: ask whether they mean to correct the record; do not change the result silently.
   - A result of Passed or Failed moves the candidate's status (for example L2 Passed). Mention the resulting status in the confirmation.
   - A **Canceled** result set by hand means the interview did not happen; if it will be rescheduled, offer to create the new interview too.
   - If the interview source is `email` (it came from a calendar invitation), say so: a later invitation update can change the time again.
4. **Confirm** with `field: old → new`, then call `staffing_update_interview` with `code` and `changes` (`version` plus only the changed fields). Clear a field only when asked, by sending `null`.
5. **Report** the saved interview and the candidate's current status.

## Do not

- Do not create a second live interview for the same round; the system rejects it. Cancel or update the existing one.
- Do not change the round of an existing interview unless the user says it was recorded in the wrong round.
