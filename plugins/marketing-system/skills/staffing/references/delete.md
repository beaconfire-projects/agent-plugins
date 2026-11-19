# Delete an interview

Tools: `marketing_search_candidates`, `marketing_get_candidate`, `marketing_list_interviews`, `marketing_delete_interview`.

Deleting is **permanent**. Use it only for a record that was created from wrong data (a wrong email, a wrong legacy row, a person created twice). It is not the way to record that something did not happen: for an interview that did not take place set the result (Canceled, No-show, Need to Reschedule) instead, and for a candidate who dropped out set the status override (see `references/candidate.md`), and for an offer that was canceled (declined or rescinded) use the cancel workflow (see `references/offer.md`); offers cannot be deleted. If the user's wording could mean either ("remove", "get rid of"), ask which they mean before going further.

## Steps

1. **Resolve to exactly one record** (rules in `SKILL.md`) and read it to get its `version`.
2. **Work out what depends on it** and tell the user:
   - **Interview**: the candidate's Current Status is recomputed from the remaining interviews. A later invitation email for the same calendar event does not bring it back (it is reported to Feishu instead). If the interview came from the legacy tabs (source `backfill`), a rebuild from the legacy tabs would create it again.
   - **Offer**: there is no delete tool. A wrong or ended offer is canceled with `marketing_cancel_offer` (see `references/offer.md`).
   - **Candidate**: there is no tool for it. A candidate is deleted by an Admin in the web back office (Candidate detail page); say so and stop.
3. **Confirm**: name the record (ID, person, round or dates), say what it affects and that it cannot be undone, and wait for a clear yes. When the user asked to remove a candidate together with their interviews, show the whole chain (every ID that will go, in the order above) in one table and take one yes for it. Never extend the list on your own.
4. Call the delete tool with the `code` and the `version` you just read. A stale version means someone changed the record: read it again, say what changed, and ask again.
5. **Report** what was deleted (IDs) and show any `warnings` from the response. State that the deletion stays in the change history and the ID is never reused.

## Do not

- Do not delete to "fix" a result, a date or a status; update the record instead.
- Do not delete several unrelated records from one confirmation; confirm each record or each explicit chain separately.
- Do not delete anything the user did not name.
