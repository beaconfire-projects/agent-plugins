# Interview slots

Tools: `staffing_list_slots`, `staffing_create_slots`, `staffing_hold_slot`, `staffing_release_slot`, `staffing_cancel_slots`, plus `staffing_search_candidates`, `staffing_get_candidate`, `staffing_list_options`.

A **slot** is a time a recruiter is free to interview, for one round (L1 or L2). It is not an interview: holding a slot reserves it for a candidate, and the interview only exists once the recruiter's calendar invitation email arrives (the system creates it from the email). Never create an interview to "finish" a held slot.

Slot `state` as returned by `staffing_list_slots`:

| state | meaning |
| --- | --- |
| `available` | free; the only state a candidate can be put on |
| `held` | a candidate holds it and no interview exists yet; `warnings` appear within 90 minutes of the start |
| `scheduled` | the holding candidate's interview exists (`interview_code`); it is the interview now, not a slot |
| `taken` | the recruiter already has another interview at that time; not free |

A candidate's status while holding a slot is `L1 Slot Held` or `L2 Slot Held`. It becomes `L1 Scheduled` / `L2 Scheduled` only when the interview exists.

## A. Create slots from pasted text

The user pastes a day, a round and, for each recruiter, a list of times. Brackets, commas and spacing are inconsistent; read the meaning and do not ask the user to reformat.

1. Extract the **date**, the **round** (L1 or L2) and each **recruiter name with its times**. If the date, round or a recruiter is missing, ask. Never guess them.
2. Write times as `10:00 AM`. Allowed times are 15-minute steps from 6:00 AM to 10:00 PM. If AM or PM is missing and cannot be told from context, ask. The time zone is `EST` unless the user names `CST`, `MST` or `PST`. Resolve relative dates against today and show the exact date.
3. Show what you read as a table (date, round, time zone, and each recruiter with its times) and wait for a clear yes. A misread date, AM/PM or a missing recruiter is the main risk, and the user can spot it here.
4. After a clear yes, call `staffing_create_slots` once and report `created` and `skipped` (already exist, or the recruiter already has an interview then). There is no preview mode; if something was wrong, `staffing_cancel_slots` voids the slots.
5. A recruiter name that is not in the recruiter list rejects the whole batch. Show the names from `staffing_list_options` and ask; never create a recruiter. Recruiters are managed on the Recruiters page of the web app, so tell the user to add the missing one there.
6. The call can be repeated safely; after a failure just run it again.

## B. Put a candidate on a slot

1. Resolve the candidate to exactly one record (see the rules in `SKILL.md`).
2. `staffing_list_slots` for the day (and recruiter or round if given) and choose among `available` slots only.
3. Confirm: candidate, slot ID, recruiter, round, date and time. Then call `staffing_hold_slot` with the `version` you just read.
4. Show every item in the response `warnings` (for example "No L1 interview on record for this candidate"), and report the candidate's new status (`L1 Slot Held` or `L2 Slot Held`).
5. **An L2 slot must be with the same recruiter as the candidate's L1.** If the call is refused for that reason, say which recruiter the L1 was with and offer that recruiter's L2 slots. The recruiter of an L1 that ended as `Need to Reschedule` is not counted; the L1 that follows it decides.
6. Tell the user the candidate is not scheduled yet: once the invitation email arrives the interview appears and the status changes. If a held slot is close to its start with no interview, `staffing_list_slots` shows a warning; suggest checking whether the invitation was sent.

## C. Need to Reschedule

The interview did not pass or did not happen, but the candidate is still good and can be tried again.

- Set the interview result to `Need to Reschedule` with `staffing_update_interview` (see `references/interview.md`). It is a final result like Passed and Failed, and the candidate's status becomes `Need to Reschedule`.
- To try again, **create a new interview or hold a new slot for the same round**; the old interview does not block it. Do not edit the old interview back to Scheduled.
- A retried **L1** may use a different recruiter. A retried **L2** keeps the L1's recruiter (the interviewer may change, the recruiter does not).

## D. Release or cancel

- Wrong candidate or the candidate backed out: `staffing_release_slot` (back to `available`), with the `version` read from the slot.
- The recruiter is no longer free: `staffing_cancel_slots` with the slot IDs. A held slot frees its candidate. One unknown ID cancels nothing.
- State exactly what will change (IDs, people, times) and wait for a clear yes before each of these.
