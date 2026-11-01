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

The user pastes a day, a round and, for each recruiter, a list of times (`X 10AM, 12PM; Y 10AM, 2:30PM`). One request covers one day, one round and one time zone; for several days or rounds make one call (and one confirmation) per day and round. Brackets, commas and spacing are inconsistent; read the meaning and do not ask the user to reformat.

1. Extract the **date**, the **round** (L1 or L2) and each **recruiter name with its times**. If the date, round or a recruiter is missing, ask. Never guess them.
2. Write times as `10:00 AM`. Allowed times are 15-minute steps from 6:00 AM to 10:00 PM. If AM or PM is missing and cannot be told from context, ask. The time zone is `EST` unless the user names `CST`, `MST` or `PST`. Resolve relative dates against today and show the exact date.
3. Show what you read as a table (date, round, time zone, and each recruiter with its times). Because every call adds slots (see 4), also read that day and round with `staffing_list_slots` and mark the times that already have a slot; if the user only wanted the missing ones, leave those times out of the request. Wait for a clear yes. A misread date, AM/PM or a missing recruiter is the main risk, and the user can spot it here.
4. After a clear yes, call `staffing_create_slots` **once** and report `created` and `skipped` (overlaps another slot, or the recruiter already has interviews that use up every slot then). **Every call adds slots on top of the existing ones** (each time gets `count` new slots, default 1). There is no preview mode; if something was wrong, `staffing_cancel_slots` voids the slots.
5. A recruiter name that is not in the recruiter list rejects the whole batch. Show the names from `staffing_list_options` and ask; never create a recruiter. Recruiters are managed on the Recruiters page of the web app, so tell the user to add the missing one there.
6. **Never run the same call again after it succeeded**: that creates duplicates. If you are not sure it went through (a timeout, a lost reply), check with `staffing_list_slots` first. A call that failed creates nothing, so after fixing the cause (for example the recruiter name) it can be sent again.

## B. Put a candidate on a slot

1. Resolve the candidate to exactly one record (see the rules in `SKILL.md`).
2. `staffing_list_slots` for the day (and recruiter or round if given) and choose among `available` slots only.
3. Confirm: candidate, slot ID, recruiter, round, date and time. Then call `staffing_hold_slot` with the `version` you just read.
4. Show every item in the response `warnings` (for example "No L1 interview on record for this candidate"), and report the candidate's new status (`L1 Slot Held` or `L2 Slot Held`).
5. **An L2 slot must be with the same recruiter as the candidate's L1.** If the call is refused for that reason, say which recruiter the L1 was with and offer that recruiter's L2 slots. The recruiter of an L1 that ended as `Need to Reschedule` is not counted; the L1 that follows it decides.
6. Tell the user the candidate is not scheduled yet: once the invitation email arrives the interview appears and the status changes. If a held slot is close to its start with no interview, `staffing_list_slots` shows a warning; suggest checking whether the invitation was sent.

## B2. Put several candidates on slots (batch)

The user pastes a list like `CAN-00012 10AM, CAN-00020 10AM` or `Alex Morgan 10:00 AM; Sam Rivera 2:30 PM`, usually for one day and one round. Read the meaning; do not ask the user to reformat.

1. Extract the **date**, the **round** (L1 or L2) and, for each line, the **candidate** and the **time** (and the recruiter if the user wrote one). If the date or round is missing, ask once for both. Never guess them. If AM or PM is missing and cannot be told from context, ask (`12AM` is midnight: confirm whether noon was meant).
2. Resolve **each candidate to exactly one record** (rules in `SKILL.md`). If some names are ambiguous, ask about those only; the rest wait in the list.
3. Call `staffing_list_slots` **once** for the day and round and keep only `available` slots. For each candidate pick the slot at the requested time:
   - exactly one available slot at that time: use it;
   - several recruiters have a slot at that time: for an **L2**, take the recruiter of the candidate's L1 (read it with `staffing_get_candidate`); for an **L1**, or when the L1's recruiter has no slot then, list the recruiters and ask the user to choose;
   - no available slot at that time: mark the row "no free slot" and show the nearest available times of that round.
   - Two candidates must never be given the same slot. If two ask for a time that has only one slot, mark the second one as a conflict and ask.
4. Show **one confirmation table** with a row per candidate: candidate (ID, name), round, date and time, recruiter, slot ID, and any problem. Rows with a problem are not part of the batch until the user settles them. Wait for a clear yes for the whole table.
5. Hold the slots **one by one** with `staffing_hold_slot` (`candidate_code` and the slot's `version`). A refusal or error on one row does not stop the others. If a call is rejected as stale, read that slot again; if it is still available, retry once, otherwise report it.
6. **Report a result table**: for every row, held or not (with the reason in the tool's message), the candidate's new status (`L1 Slot Held` or `L2 Slot Held`) and every item in `warnings`. Say plainly which candidates are still not on a slot. Then remind the user that nobody is scheduled yet: the interview appears when the invitation email arrives.
7. An L2 slot must be with the L1's recruiter (see B.5); say so for any row refused for that reason and offer that recruiter's other L2 slots.

## C. Need to Reschedule

The interview did not pass or did not happen, but the candidate is still good and can be tried again.

- Set the interview result to `Need to Reschedule` with `staffing_update_interview` (see `references/interview.md`). It is a final result like Passed and Failed, and the candidate's status becomes `Need to Reschedule`.
- To try again, **create a new interview or hold a new slot for the same round**; the old interview does not block it. Do not edit the old interview back to Scheduled.
- A retried **L1** may use a different recruiter. A retried **L2** keeps the L1's recruiter (the interviewer may change, the recruiter does not).

## D. Release or cancel

- Wrong candidate or the candidate backed out: `staffing_release_slot` (back to `available`), with the `version` read from the slot.
- The recruiter is no longer free: `staffing_cancel_slots` with the slot IDs. A held slot frees its candidate. One unknown ID cancels nothing.
- State exactly what will change (IDs, people, times) and wait for a clear yes before each of these.
