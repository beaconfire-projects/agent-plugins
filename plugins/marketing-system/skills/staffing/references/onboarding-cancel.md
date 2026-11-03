# Cancel an offer, or undo a cancellation

Tools: `staffing_search_candidates`, `staffing_list_onboardings`, `staffing_get_onboarding`, `staffing_cancel_onboarding`, `staffing_undo_cancel_onboarding`.

An offer can be canceled after the onboarding record exists. The record **stays** (it is not deleted), and the candidate's status follows:

| Who ended it | `type` | The candidate becomes |
| --- | --- | --- |
| The candidate turned the offer down | `candidate_declined` | Candidate Withdrew |
| The company withdrew the offer | `company_rescinded` | Company Dropped, with `Offer rescinded: <note>` as the reason |

The candidate's Offer Status and Start Date are cleared (the record keeps its start date, so an undo can restore it). In the customer's Onboarding Info Sheet the row is struck through; an undo removes the strikethrough. Do this with these tools, not with delete (`references/delete.md` is for records created from wrong data) and not by setting Status Override on the candidate (that is refused while the offer is canceled).

## Cancel

1. **Find the onboarding record.** Onboarding ID: `staffing_get_onboarding`. Name or Candidate ID: resolve the candidate, then `staffing_list_onboardings` with `candidate_code` (it includes canceled records). No record: say so; there is no offer to cancel.
2. **Check the state.** If `canceled_at` is already set, tell the user (when, by whom, type, note) and offer an undo instead. Never cancel twice.
3. **Get the type.** It must come from the user's words. "Turned it down", "declined", "doesn't want the job", "withdrew" = `candidate_declined`. "The client pulled the offer", "the project was canceled", "we rescinded" = `company_rescinded`. If it is not clear who ended it, ask; do not guess. Ask for a short note only if the user did not give a reason; the note is optional.
4. **Confirm** with a short table: the record (`ONB-… Name`), the type, the note, the candidate's status `old → new` (Candidate Withdrew or Company Dropped, with the reason text for Company Dropped), and that Offer Status and Start Date are cleared and the sheet row is struck through. Wait for a clear yes.
5. Call `staffing_cancel_onboarding` with `code` and `data` (`version`, `type`, `note`). A stale version means someone changed the record: read it again, say what changed, and ask again.
6. **Report** the saved record (status is empty, `canceled_at` set) and the candidate's new status. Say the sheet row is struck through on the next sheet update (within a few minutes).

## Undo a cancellation

Use it when the candidate has the offer again (the user says "the offer is back on", "they changed their mind", "the cancellation was a mistake").

1. Find the record as above. If `canceled_at` is empty, there is nothing to undo; say so.
2. **Confirm**: the candidate goes back to Offered, or Onboarding Scheduled when the record has a start date; Status Override and its reason are cleared; the strikethrough is removed. Wait for a clear yes.
3. Call `staffing_undo_cancel_onboarding` with `code` and `data` (`version`).
4. **Report** the restored status.

## What a canceled onboarding blocks

- A canceled record cannot be edited (offer date, start date): undo first, then change it.
- The candidate's Status Override and its reason cannot be changed directly while the offer is canceled: undo first.
- `staffing_list_onboardings` without a candidate leaves canceled records out; pass `include_canceled` to see them.

## Do not

- Do not use Status Override or delete to record a canceled offer.
- Do not cancel for a candidate who has no onboarding record.
- Do not guess the type.
