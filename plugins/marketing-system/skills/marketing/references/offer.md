# Formal Offers: lookup, creation and editing

Formal Offers are independent records (`OFR-…`), not a submission's Offered label or the staffing onboarding workflow. Multiple offers per submission are supported. Vendor scope follows the source position; missing/inaccessible records both return Not found. No implicit default position is supplied.

## Lookup and history

Call `marketing_list_offers(query={q, status, page, page_size})` with optional fields (q defaults empty, page 1, size 25, max 100); status is an array of exact stored values. Resolve the specific code, then `marketing_get_offer(code)`. Read actual history with `marketing_get_offer_history(code)`; never synthesize events from dates or neighboring offers. `marketing_offer_options()` returns statuses, PO companies, states, offboarding reasons and next steps. History masks sensitive address/marketing-email changes.

## Create after interview review

Precondition: one existing visible submission and explicit intent to record a formal offer. There is no requirement in the current service that a submission already be Offered or have a Passed interview; do not invent such gates or infer an offer automatically from L2 Passed.

1. `marketing_search_offer_submissions(query={q, page, page_size})` resolves the exact submission (page 1, size 25, max 100). Repeated pairs remain separate.
2. `marketing_preview_offer_submission(code)` returns that submission and **all strictly linked interviews** and offers. Show rounds/results/dates, including missing/no interviews, and any existing offers. Read-only review does not permit interview editing.
3. Ask the user to explicitly confirm that the full interview set was reviewed and that a new independent offer is intended. Confirm `offer_date` and `onboarding_tentative_start_date`, each optional and defaulting to null—no today/default/inheritance from earlier offers. Do not invent an interview to fill a gap.
4. Call `marketing_create_offer(request={request_id, submission_code, interviews_confirmed:true, offer_date?, onboarding_tentative_start_date?})`. `request_id` is a fresh UUID for this distinct creation attempt, not an invented business record ID. Retain it with the exact payload for outcome verification. Creation accepts no extra pay/HR/status fields.
5. Read returned code with `marketing_get_offer`. Verify source submission, `In Progress`/`created` stage, dates and version. Creation does not mark the submission Offered, start employment or update person marketing status. Further changes require their own confirmation.

### Creation recovery

`confirmation_required`: review all interviews and obtain explicit consent, not merely flip the flag. `not_found`: stop for scope/source resolution. Unknown outcome: first inspect list/detail and source preview; **never generate a new UUID to retry the same attempt**. If still uncertain, explain and obtain consent to replay the exact same request/UUID solely to verify that attempt; the service returns the existing offer for an identical fingerprint. `request_conflict` means the UUID was used for different payload values: stop, inspect the original attempt; do not overwrite or treat it as authorization for a new offer. A genuinely separate offer requires new explicit consent and a new UUID.

## Edit offer details without changing lifecycle

Read offer → `marketing_offer_options` and, if needed, `marketing_search_offer_po_vendors(query={q, page, page_size})` → confirm changed fields → `marketing_update_offer(code, request={version, ...changed_fields})` → exact readback. PO Vendor must be an existing company flagged `is_po_vendor`; it is not the PO Company dropdown. If missing, use the separately confirmed [company workflow](company.md).

Editable fields include:
- `offer_date`, `onboarding_tentative_start_date`, `onboarding_actual_start_date`, `onboarding_bgc_form_sent_date`, `onboarding_bgc_completed_date`.
- `po_company`, `po_vendor_code`, `onboarding_marketing_email`, `onboarding_bgc_poc`, `onboarding_am_notes`, `work_location`, `rate`.
- `onboarding_po_signed`, `onboarding_bgc_completed`, `onboarding_professional_talk`, `onboarding_email` (boolean or null).
- The five offboarding business fields and HR/checklist/shipping fields in [offer lifecycle](offer-lifecycle.md).

Omitted fields are preserved; null clears optional fields subject to merged validation. Rate is finite nonnegative USD/hour, not salary; it has no submission-style 500 cap. Do not copy submission rate by default. Code, source submission, lifecycle status/stage and related entity codes are not editable.

Addresses use `{line1, line2, city, state, zipcode}`. Components cannot contain commas; state must be one of the 50 US codes (not DC). An address object replaces the stored address, not a nested dirty patch: retain wanted components explicitly and confirm cleared components. Shipping is independent of work location and must be wholly empty or include line1/city/state/zipcode. Preserve raw historical addresses and `legacy_check_values` unless the user explicitly corrects them. Checkboxes accept booleans/null, not legacy Y/N strings.

Editing actual start/last day alone does **not** onboard/offboard. Last day cannot precede actual start. For onboarded/offboarded offers, changing any of actual start, PO Company or work location revalidates all three together; unrelated HR corrections may proceed despite legacy missing required data. Unknown/withdrawn legacy stages cannot be forced through lifecycle actions, though field editing is supported subject to validation.

## Update recovery

Version conflict: re-read and reconfirm. Invalid PO Vendor/options/address/date: refresh choices and ask for correction; never coerce unknown legacy values. Unknown `offer_operation_failed`: get exact code/history and verify changed fields before retrying. Do not replay status actions or assume a no-op added an audit event. There is no permitted delete, withdrawal, cancellation, undo or automatic marketing-status transition tool.
