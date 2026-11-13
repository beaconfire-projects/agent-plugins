# Offer onboarding, offboarding and HR follow-up

This is the **formal Offer** lifecycle, keyed by `OFR-…`, not staffing onboarding/offboarding keyed by other record codes. Always use returned `stage` rather than inferring it from a start date. Current mapping: In Progress → created; Active → onboarded; Offboarded/Remap/Quit/Fired → offboarded; withdrawn or other statuses → legacy. No lifecycle action is available for legacy, and no undo is exposed.

## Confirm actual start

Scenario: the person actually started, not merely accepted an offer or received a tentative date.

1. `marketing_get_offer(code)`; require stage `created`. `marketing_offer_options()` supplies PO companies and work states; `marketing_search_offer_po_vendors(query)` resolves any optional PO Vendor.
2. Review actual-start evidence and merged required fields: `onboarding_actual_start_date`, `po_company` (currently Invct/BSS/BFS), and `work_location.state` (50 US states, no DC). Values may already be saved or be supplied in this action. Work address components cannot contain commas; preserve intended components when replacing the object. Validate any existing last day is not before actual start.
3. Show current → proposed fields and lifecycle `In Progress → Active`, explain this confirms actual employment, and wait for explicit consent.
4. `marketing_onboard_offer(code, request={version, ...changed_onboarding_fields})`. It accepts onboarding fields listed in [offer](offer.md), not HR-only checklist/shipping or offboarding fields. It does not require all BGC/PO checklist boxes checked; do not invent that gate or auto-check them.
5. `marketing_get_offer(code)` and, if history is requested, `marketing_get_offer_history(code)`. Verify stage `onboarded`, status Active, actual date, PO Company, work state and new version. No claim of staffing or person-status changes.

## Confirm actual end

Scenario: actual offboarding of an `onboarded` offer, not offer rejection/cancellation or merely a future scheduled end.

1. Read exact offer/version and `marketing_offer_options()`.
2. Review the five optional business fields: `offboarding_last_day`, `offboarding_current_status`, `offboarding_reason`, `offboarding_next_step`, `offboarding_notes`. Current-status choices are `Remap`, `Quit`, `Fired` (not returned as a dedicated options list). Reasons and next steps must match options: reasons include Vendor/Client FT Conversion, Project ended, Visa issue, client release for Performance/Budget, Other; next steps include Back to Marketing, FT, MIA, Return to Training, Other. Use exact returned spelling.
3. Explain that **all five fields are optional: sending only `version` still ends the offer**. Missing last day does not block the action. If provided, last day cannot precede actual start. Show lifecycle Active → Offboarded and the merged fields; obtain explicit confirmation of actual end, even for an otherwise empty form.
4. `marketing_offboard_offer(code, request={version, ...changed_offboarding_fields})`.
5. Read exact offer again. Verify stage `offboarded`, status **Offboarded**, fields and version. `offboarding_current_status=Remap/Quit/Fired` is separate from offer status. `offboarding_next_step=Back to Marketing` records intent only: it does not change the person's candidate marketing status. If return-to-marketing is requested, stop for authorized manual completion, not a staffing call.

## HR checklist and shipping maintenance

Precondition: exact visible offer and verified completion/data, not a request to execute external HR operations. Read → confirm diff → `marketing_update_offer(code, request={version, ...changed_fields})` → readback. This is a data update, **not** an onboarding/offboarding action.

HR fields: `onboarding_i9_completed`, `onboarding_everify_completed`, `onboarding_ts_setup_done`, `offboarding_hr_email_sent`, `offboarding_equipment_returned`, `offboarding_adp_status_updated`, `offboarding_final_paycheck_processed`, `offboarding_hr_admin_complete` (boolean/null); `offboarding_hr_notified_date`, `offboarding_hr_notes`; `onboarding_shipping_address`. Shipping address is independent, wholly empty or with line1/city/state/zipcode, with optional line2. Do not copy the work address without consent. There is no extra HR-only role gate in this offer service beyond the offer's vendor visibility; do not confuse it with restricted shared-person management.

Do not claim that saving these fields sends mail, runs E-Verify, completes I9, ships equipment or processes pay. No allowed tool executes those external steps.

## Recovery for each action

`invalid_transition`: re-read and explain current stage; do not retry via a different workflow or PATCH status. `version_conflict`: get latest values and reconfirm. Missing required onboarding values or invalid options/date/address: ask for real values and confirm corrected payload. Unknown outcome: get exact offer/history before retry; an action may have committed. If already in target stage, report verified state rather than executing again. Stop for inaccessible records or unsupported cancellation/undo. Success means verified database state, not external HR completion or immediate sheet sync.
