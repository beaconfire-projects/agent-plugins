# Offer dates, start and end, cancellation, HR follow-up

This is the **formal Offer** lifecycle, keyed by `OFR-…`. There are no onboard / offboard actions and no stage field: the status (Offered, On Project, Off Project, Canceled) is derived from the dates and from cancellation, so every change below is a `marketing_update_offer` call with the dates or a cancel call.

| Status | When (business days, US Eastern) |
|---|---|
| Canceled | the offer was canceled, at any stage |
| Off Project | today is after the **actual last day** (the offer ends the day after it) |
| On Project | today is on or after the **actual start date** |
| Offered | otherwise |

Expected dates (`onboarding_tentative_start_date`, `offboarding_tentative_last_day`) are informational and never change the status. Actual dates may be in the future (the response shows `start_scheduled` / `end_scheduled`), can be corrected and can be cleared with `null`. A daily job refreshes the status and the candidate's marketing status when a date arrives; a status an AM set by hand is not overwritten by it.

## Confirm actual start

Scenario: the person actually started (or has a confirmed start date), not merely accepted an offer or got an expected date.

1. `marketing_get_offer(code)`; read the version. `marketing_offer_options()` supplies PO companies and work states; `marketing_search_offer_po_vendors(query)` resolves an optional PO Vendor.
2. Collect `onboarding_actual_start_date`, `po_company` (Invct/BSS/BFS) and `work_location.state` (50 US states, no DC). Values may already be saved or be supplied in this call. Work address components cannot contain commas; preserve intended components when replacing the object. An existing actual last day must not be before the new start.
3. Show `old → new` fields and the resulting status (On Project now, or Offered until the future date arrives), and wait for explicit consent. It does not require the BGC / PO checklist to be complete; do not invent that gate or auto-check them.
4. `marketing_update_offer(code, request={version, ...changed_fields})`, then `marketing_get_offer(code)`: verify status, the actual date, PO Company, work state and the new version.

## Confirm actual end

Scenario: the person's last working day is confirmed. Requires an actual start date on the offer; the actual last day must not be before it.

1. Read the exact offer and `marketing_offer_options()`.
2. Collect `offboarding_last_day` (actual) and, when the user gives them, `offboarding_current_status` (`Remap`, `Quit`, `Fired`), `offboarding_reason`, `offboarding_next_step`, `offboarding_notes`. Reasons: Vendor FT Conversion, Client FT Conversion, Project ended, Visa issue, Released by client: Performance issue, Released by client: Budget issue, Other. Next steps: Back to Marketing, FT, MIA, Return to Training, Other. Use exact returned spelling. A planned date goes to `offboarding_tentative_last_day`, never to the actual field.
3. Show `old → new` and the resulting status (Off Project the day after the last day; until then still On Project), obtain explicit confirmation.
4. `marketing_update_offer(code, request={version, ...fields})`, then read the offer again and verify. The candidate's marketing status follows automatically once the offer ends (Quit / Fired / Remap by `offboarding_current_status`; no outcome falls back to In Marketing). `Back to Marketing` as next step is only a record; it does not change the status by itself.

## Correct or clear a date

Show `old → new` and the resulting status. An actual start cannot be cleared while an actual last day is set (clear the last day first); an actual last day cannot be set without an actual start or before it. The server rejects violations; ask the user for real values and reconfirm.

## Cancel an offer, or undo it

Cancel when the candidate turned the offer down or the company rescinded it. It is allowed at any stage, including after the actual start date. It does not change the submission.

1. Read the offer and its version; if it is already Canceled, offer an undo instead.
2. Get the party from the user's words: `Candidate` (turned it down, declined) or `Company` (rescinded, the client pulled it). If unclear, ask; never guess. A short `reason` is optional.
3. Confirm the offer, the party, the reason and `status → Canceled`, then call `marketing_withdraw_offer(code, request={version, party, reason?})`.
4. Undo ("the offer is back on"): `marketing_undo_withdraw_offer(code, request={version})` after confirmation; the status is derived again from the dates.

A canceled offer cannot be edited.

## HR checklist and shipping maintenance

Precondition: exact visible offer and verified completion/data, not a request to execute external HR operations. Read → confirm diff → `marketing_update_offer(code, request={version, ...changed_fields})` → readback. These are data updates and never change the status.

HR fields: `onboarding_i9_completed`, `onboarding_everify_completed`, `onboarding_ts_setup_done`, `offboarding_hr_email_sent`, `offboarding_equipment_returned`, `offboarding_adp_status_updated`, `offboarding_final_paycheck_processed`, `offboarding_hr_admin_complete` (boolean/null); `offboarding_hr_notified_date`, `offboarding_hr_notes`; `onboarding_shipping_address`. Shipping address is independent, wholly empty or with line1/city/state/zipcode, with optional line2. Do not copy the work address without consent. There is no extra HR-only role gate beyond the offer's vendor visibility.

Do not claim that saving these fields sends mail, runs E-Verify, completes I9, ships equipment or processes pay. No tool executes those external steps.

## Recovery

`version_conflict`: get the latest values and reconfirm. `invalid_transition` (cancel / undo on the wrong state) and `offer_canceled` (edit of a canceled offer): re-read, explain the current status, do not retry through another route. Missing required onboarding values or invalid options/dates/addresses: ask for real values and confirm the corrected payload. Unknown outcome: read the exact offer and its history before any retry; the action may have committed. Success means verified database state, not external HR completion or immediate sheet sync.
