# Offers: create, read, change dates, cancel

Tools: `marketing_search_offer_submissions`, `marketing_preview_offer_submission`, `marketing_create_offer`, `marketing_list_offers`, `marketing_get_offer`, `marketing_get_offer_history`, `marketing_update_offer`, `marketing_cancel_offer`, `marketing_undo_cancel_offer`, `marketing_offer_options`, `marketing_search_offer_po_vendors`.

An **Offer** (`OFR-nnnnnn`) belongs to one submission (one candidate and one position). The same submission can have several offers; each is independent. There is no separate onboarding or offboarding record: onboarding and offboarding are field groups of the offer, and nothing here deletes an offer (use cancel).

## The status is derived, never set

The status (`status` in every response) comes from the facts on the offer. You cannot write it.

| Status | When |
|---|---|
| Canceled | the offer was canceled (any stage) |
| Off Project | today is after the **actual last day** |
| On Project | today is on or after the **actual start date** |
| Offered | everything else |

Dates are business days in US Eastern. The actual last day is the last working day, so the offer ends the **day after** it. An actual date may be in the future ("starts on ..." / "ends after ..." in the response), it can be changed and it can be cleared (`null`). **Expected** dates (`onboarding_tentative_start_date`, `offboarding_tentative_last_day`) are only informational and never change the status.

Two rules the server enforces, so check them before asking for confirmation: an actual last day needs an actual start date, and it must not be earlier than the actual start date. An actual start date can only be cleared once the actual last day is cleared.

The candidate's marketing status follows the offers automatically (any On Project offer: On Project; otherwise any Offered: Offer; otherwise the last outcome Quit / Fired / Remap; all canceled: In Marketing), once at the moment the status changes, so a status an AM sets by hand is not overwritten the next day. Mention the candidate's new status in the report when a write changed it.

## Find an offer

- `marketing_list_offers` with `query` (`q` matches offer, submission, candidate, position and vendor; `status` filters by the four statuses; `page`, `page_size`). It lists every offer, including several for the same submission.
- `marketing_get_offer` with the `OFR-` code returns all fields, the `version` and the history. `marketing_get_offer_history` returns only the change history.
- An offer outside the user's vendors is `Not found`.

## Create an offer

1. **Find the submission**: from `marketing_get_candidate_detail` (`submissions`), a `SUB-` code from the user, or `marketing_search_offer_submissions`. Resolve to exactly one.
2. **Review the interviews**: `marketing_preview_offer_submission` returns the submission with all its interviews. Show them (round, date, result). An offer does not need a passed interview; the user decides. Creating requires the user to have seen them (`interviews_confirmed: true`).
3. **Collect the fields**. Required: `po_company` (`marketing_offer_options`: Invct, BSS, BFS). Never guess it; ask. Optional: `offer_date`, `onboarding_tentative_start_date`, `work_location` (`line1`, `line2`, `city`, `state`, `zipcode`; no commas). Blank dates stay empty; do not default them to today.
4. **Confirm** with a short table (candidate, position, PO Company, dates) and wait for a clear yes.
5. Call `marketing_create_offer` with a fresh UUID in `request_id`. Reuse a `request_id` only to check the same attempt after an unknown result (read first; never blindly retry a write). A second offer for the same submission needs a new UUID.
6. **Report** the `OFR-` code, the status (Offered) and the candidate's resulting marketing status.

### After an L2 pass

An interview write that sets L2 to Passed can return `onboarding_suggestion` (the field keeps its name). **Do not create the offer silently**: an offer needs a PO Company and the user must review the interviews. Say in the same reply that the candidate is ready for an offer, and ask for the PO Company and any dates; then follow the steps above (find the candidate's submission with `marketing_get_candidate_detail`). For several candidates, list them in one table and ask once for the PO Company of each.

## Change fields, dates and checklists

`marketing_update_offer` with `code` and `request` (`version` plus only the fields to change; `null` clears an optional field). Read the offer first for the `version`. A stale version means someone changed it: read again, say what changed, ask again.

- **Confirm the start** ("they started today", "first day was ..."): set `onboarding_actual_start_date`. It needs `po_company` and a work location `state` on the offer; if either is missing the server says so: ask the user and send them in the same call.
- **Confirm the end** ("last day was ...", "they leave on ..."): set `offboarding_last_day` (actual), and, when the user gives them, `offboarding_current_status` (`Remap`, `Quit`, `Fired`), `offboarding_reason`, `offboarding_next_step`, `offboarding_notes`. Expected last day goes to `offboarding_tentative_last_day`.
- **Correct a date**, or clear it: show `old -> new` and the resulting status (for example Offered -> On Project once the date arrives).
- **Never confirm from an expected date**. If the user gives only a planned date, set the expected field.
- Other fields: `offer_date`, `po_vendor_code` (existing PO Vendor company, `marketing_search_offer_po_vendors`), `rate` (USD per hour, not negative), `work_location`, Marketing Email, BGC fields (`onboarding_bgc_poc`, form sent and completed dates; a completion date marks BGC completed), checklist values (`true` / `false` / `null`: PO signed, BGC completed, professional talk, onboarding email, I-9, E-Verify, TS setup, equipment returned, ADP updated, final paycheck, HR admin complete), shipping address, notes. These never change the status.
- `reason` choices: Vendor FT Conversion, Client FT Conversion, Project ended, Visa issue, Released by client: Performance issue, Released by client: Budget issue, Other. `next_step`: Back to Marketing, FT, MIA, Return to Training, Other. Use only these.
- A canceled offer cannot be edited; undo the cancellation first.
- Address, rate, contact email and notes appear in the history as `changed` only.

## Cancel an offer, or undo it

Cancel when the candidate turned the offer down or the company rescinded it. It works at any stage, even after the actual start date (the offer simply stops counting).

1. Find the offer and read its `version`. If its status is already Canceled, offer an undo instead.
2. **Get the party from the user's words**: `Candidate` ("turned it down", "declined", "withdrew") or `Company` ("the client pulled it", "we rescinded"). If it is unclear who ended it, ask; never guess. A short `reason` is optional.
3. **Confirm**: the offer (`OFR-... Name`), the party, the reason, the status `old -> Canceled`, and that the candidate's marketing status is recalculated. Wait for a clear yes.
4. Call `marketing_cancel_offer` with `code` and `request` (`version`, `party`, `reason`).
5. To undo ("the offer is back on"), call `marketing_undo_cancel_offer` with `code` and `request` (`version`) after the same kind of confirmation; the status is derived again from the dates.

Cancelling does not change the submission.

## Do not

- Do not set the status or the candidate's marketing status through the offer; both come from the dates and cancellation.
- Do not create an offer without the user's PO Company, and do not reuse an old `request_id` for a new offer.
- Do not record a canceled offer by deleting anything or by editing the candidate.
