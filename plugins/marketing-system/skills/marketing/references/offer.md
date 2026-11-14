# Formal Offers: lookup, creation and editing

Formal Offers are independent records (`OFR-…`), not a submission's Offered label. Multiple offers per submission are supported and each is independent. Vendor scope follows the source position; missing and inaccessible records both return Not found. No implicit default position is supplied.

**The status is derived, never written.** `status` is Offered, On Project, Off Project or Canceled, computed from the facts on the offer: Canceled if withdrawn; Off Project the day **after** the actual last day; On Project from the actual start date (business days, US Eastern); otherwise Offered. Actual dates may be in the future, can be changed and can be cleared. Expected dates never change the status. See [offer lifecycle](offer-lifecycle.md) for the date actions and cancellation.

## Lookup and history

Call `marketing_list_offers(query={q, status, page, page_size})` with optional fields (q defaults empty, page 1, size 25, max 100); `status` is an array of the four derived statuses. Resolve the specific code, then `marketing_get_offer(code)` (fields, derived status, version, history). Read actual history with `marketing_get_offer_history(code)`; never synthesize events from dates or neighboring offers. `marketing_offer_options()` returns statuses, withdraw parties, PO companies, states, offboarding reasons and next steps. History masks sensitive changes (addresses, marketing email, rate, BGC contact, notes) as `changed`.

## Create after interview review

Precondition: one existing visible submission and explicit intent to record a formal offer. The service does not require a Passed interview or an Offered submission; do not invent such gates or create an offer automatically from L2 Passed.

1. `marketing_search_offer_submissions(query={q, page, page_size})` resolves the exact submission (page 1, size 25, max 100). Repeated pairs remain separate.
2. `marketing_preview_offer_submission(code)` returns that submission with **all linked interviews** and offers. Show rounds, results and dates, including a missing interview set, and any existing offers.
3. Collect the fields and confirm: **`po_company` is required** (`marketing_offer_options`: Invct, BSS, BFS; never guess it). `offer_date`, `onboarding_tentative_start_date` and `work_location` are optional; blank dates stay null (no today default, no inheritance). Ask the user to explicitly confirm that the full interview set was reviewed and that a new independent offer is intended.
4. Call `marketing_create_offer(request={request_id, submission_code, interviews_confirmed:true, po_company, offer_date?, onboarding_tentative_start_date?, work_location?})`. `request_id` is a fresh UUID for this creation attempt; keep it with the exact payload for outcome verification.
5. Read the returned code with `marketing_get_offer`. Verify the submission, status Offered, PO Company, dates and version. Creation does not mark the submission Offered. The candidate's marketing status becomes `Offer` automatically; report it if it changed.

### Creation recovery

`confirmation_required`: review all interviews and obtain explicit consent, not merely flip the flag. `not_found`: stop for scope/source resolution. Unknown outcome: first inspect list/detail and the source preview; **never generate a new UUID to retry the same attempt**. If still uncertain, explain and obtain consent to replay the exact same request/UUID solely to verify that attempt (the service returns the existing offer for an identical payload). `request_conflict` means the UUID was used for different values: stop and inspect the original attempt. A genuinely separate offer needs new explicit consent and a new UUID.

## Edit offer details

Read offer → `marketing_offer_options` and, if needed, `marketing_search_offer_po_vendors(query={q, page, page_size})` → confirm changed fields → `marketing_update_offer(code, request={version, ...changed_fields})` → exact readback. PO Vendor must be an existing company flagged `is_po_vendor`; it is not the PO Company dropdown. If missing, use the separately confirmed [company workflow](company.md).

Editable fields include:
- Dates: `offer_date`, `onboarding_tentative_start_date`, `onboarding_actual_start_date`, `offboarding_tentative_last_day`, `offboarding_last_day` (actual), `onboarding_bgc_form_sent_date`, `onboarding_bgc_completed_date` (a completion date marks BGC completed).
- `po_company`, `po_vendor_code`, `onboarding_marketing_email`, `onboarding_bgc_poc`, `onboarding_am_notes`, `work_location`, `rate`.
- `onboarding_po_signed`, `onboarding_bgc_completed`, `onboarding_professional_talk`, `onboarding_email` (boolean or null).
- The offboarding business fields (`offboarding_current_status`, `offboarding_reason`, `offboarding_next_step`, `offboarding_notes`) and the HR / checklist / shipping fields in [offer lifecycle](offer-lifecycle.md).

Omitted fields are preserved; null clears optional fields subject to merged validation. Rate is finite nonnegative USD/hour, not salary. Code, source submission, status and related entity codes are not editable. A canceled offer cannot be edited until the cancellation is undone.

Addresses use `{line1, line2, city, state, zipcode}`. Components cannot contain commas; state must be one of the 50 US codes (not DC). An address object replaces the stored address, not a nested dirty patch: retain wanted components explicitly and confirm cleared components. Shipping is independent of work location and must be wholly empty or include line1/city/state/zipcode. Preserve raw historical addresses and `legacy_check_values` unless the user explicitly corrects them. Checkboxes accept booleans/null, not legacy Y/N strings.

Two server rules on dates: an actual last day needs an actual start date, and it cannot be earlier than the actual start date. Setting an actual start date needs `po_company` and a work location `state` on the offer (supplied in the same call if missing).

## Update recovery

Version conflict: re-read and reconfirm. Invalid PO Vendor/options/address/date: refresh choices and ask for correction; never coerce unknown legacy values. Unknown `offer_operation_failed`: get exact code/history and verify changed fields before retrying; do not assume a no-op added an audit event. There is no delete tool: a wrong or ended offer is canceled (see [offer lifecycle](offer-lifecycle.md)).
