# Interview slots

Tools: `marketing_list_slots`, `marketing_create_slots`, `marketing_hold_slot`, `marketing_hold_slots`, `marketing_release_slot`, `marketing_cancel_slots`, plus `marketing_search_candidates`, `marketing_get_candidate`, `marketing_list_options`.

A **slot** is a time a recruiter is free to interview, for one round (L1 or L2). It is not an interview: holding a slot reserves it for a candidate, and the interview only exists once the recruiter's calendar invitation email arrives (the system creates it from the email). Never create an interview to "finish" a held slot.

Slot `state` as returned by `marketing_list_slots`:

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
3. **Preview with the server.** Call `marketing_create_slots` with `dry_run: true` and the request you read. Nothing is written. Show the result: per recruiter, the slots that would be created, and the ones that would be skipped with the reason (overlaps another slot, or the recruiter's interviews already use up the time). An unknown recruiter or a time in the past is rejected here too, before anything is created.
   - **Every real call adds slots on top of the existing ones** (each time gets `count` new slots, default 1). So also read that day and round with `marketing_list_slots` and mark the times that already have a slot; if the user only wanted the missing ones, leave those times out of the request.
   - Wait for a clear yes. A misread date, AM/PM or a missing recruiter is the main risk, and the user can spot it in this table.
4. After a clear yes, send **the same request again without `dry_run`**, once. Report `created` and `skipped`. If something was wrong, `marketing_cancel_slots` voids the slots.
5. A recruiter name that is not in the recruiter list rejects the whole batch. Show the names from `marketing_list_options` and ask; never create a recruiter. Recruiters are managed on the Recruiters page of the web app, so tell the user to add the missing one there.
6. **Never run the real call again after it succeeded**: that creates duplicates. If you are not sure it went through (a timeout, a lost reply), check with `marketing_list_slots` first. A call that failed creates nothing, so after fixing the cause it can be sent again. A `dry_run` call can be repeated any time.

## B. Put a candidate on a slot

1. Resolve the candidate to exactly one record (see the rules in `SKILL.md`).
2. `marketing_list_slots` for the day (and recruiter or round if given) and choose among `available` slots only.
3. Confirm: candidate, slot ID, recruiter, round, date and time. Then call `marketing_hold_slot` with the `version` you just read.
4. Show every item in the response `warnings` (for example "No L1 interview on record for this candidate"), and report the candidate's new status (`L1 Slot Held` or `L2 Slot Held`).
5. **An L2 slot must be with the same recruiter as the candidate's L1.** If the call is refused for that reason, say which recruiter the L1 was with and offer that recruiter's L2 slots. The recruiter of an L1 that ended as `Need to Reschedule` is not counted; the L1 that follows it decides.
6. Tell the user the candidate is not scheduled yet: once the invitation email arrives the interview appears and the status changes. If a held slot is close to its start with no interview, `marketing_list_slots` shows a warning; suggest checking whether the invitation was sent.

## B2. Put several candidates on slots (batch)

The user pastes a list like `PER-010012 10AM, PER-010020 10AM` or `Alex Morgan 10:00 AM; Sam Rivera 2:30 PM`, usually for one day and one round. Read the meaning; do not ask the user to reformat.

1. Extract the **date**, the **round** (L1 or L2) and, for each line, the **candidate** and the **time** (and the recruiter if the user wrote one). If the date or round is missing, ask once for both. Never guess them. If AM or PM is missing and cannot be told from context, ask (`12AM` is midnight: confirm whether noon was meant).
2. Resolve **each candidate to exactly one record** (rules in `SKILL.md`). If some names are ambiguous, ask about those only; the rest wait in the list.
3. Call `marketing_list_slots` **once** for the day and round and keep only `available` slots. For each candidate pick the slot at the requested time:
   - exactly one available slot at that time: use it;
   - several recruiters have a slot at that time: for an **L2**, take the recruiter of the candidate's L1 (read it with `marketing_get_candidate`); for an **L1**, or when the L1's recruiter has no slot then, list the recruiters and ask the user to choose;
   - no available slot at that time: mark the row "no free slot" and show the nearest available times of that round.
   - Two candidates must never be given the same slot. If two ask for a time that has only one slot, mark the second one as a conflict and ask.
4. **Preview with the server.** Call `marketing_hold_slots` with `dry_run: true` and one entry per row (`slot_code`, `candidate_code` and the slot's `version` you just read). Nothing is written. Every row comes back `ok` or with the reason it would be refused (not available any more, the candidate already holds a slot of that round or already has that round's interview, an L2 slot with the wrong recruiter, the same slot asked for twice). A preview sees the effect of earlier rows on later ones.
5. Show **one confirmation table** with a row per candidate: candidate (ID, name), round, date and time, recruiter, slot ID, and the preview result (the reason and any `warnings` for rows that would fail or carry a warning). Take problem rows out of the batch, or fix them with the user, and preview again if you changed anything. Wait for a clear yes for the whole table.
6. Send **the same `holds` again without `dry_run`**, once. A refusal on one row does not stop the others. If a row is rejected as stale, read that slot again; if it is still available, retry that row once (it may be previewed again first), otherwise report it. Then **report a result table**: for every row, held or not (with the reason), the candidate's new status (`L1 Slot Held` or `L2 Slot Held`) and every item in `warnings`. Say plainly which candidates are still not on a slot, and remind the user that nobody is scheduled yet: the interview appears when the invitation email arrives.
7. An L2 slot must be with the L1's recruiter (see B.5); say so for any row refused for that reason and offer that recruiter's other L2 slots. Use `marketing_hold_slot` (single) only when the user asks for one candidate.

## C. Need to Reschedule

The interview did not pass or did not happen, but the candidate is still good and can be tried again.

- Set the interview result to `Need to Reschedule` with `marketing_update_interview` (see `references/interview.md`). It is a final result like Passed and Failed, and the candidate's status becomes `Need to Reschedule`.
- To try again, **create a new interview or hold a new slot for the same round**; the old interview does not block it. Do not edit the old interview back to Scheduled.
- A retried **L1** may use a different recruiter. A retried **L2** keeps the L1's recruiter (the interviewer may change, the recruiter does not).

## D. Release or cancel

- Wrong candidate or the candidate backed out: `marketing_release_slot` (back to `available`), with the `version` read from the slot.
- The recruiter is no longer free: `marketing_cancel_slots` with the slot IDs. A held slot frees its candidate. One unknown ID cancels nothing.
- State exactly what will change (IDs, people, times) and wait for a clear yes before each of these.
