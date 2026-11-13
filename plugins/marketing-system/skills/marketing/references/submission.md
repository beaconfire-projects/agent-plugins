# Submissions

These are workspace submissions, not the staffing-only submission tools. They use vendor-scoped positions. Candidate search uses everyone=True semantics: candidate flag plus consultant-info row, and either no open offer with marketing status `In Preparation`, `In Marketing` or `Remap`, or an open offer in scope. The current eligibility test defines open as no withdrawal and no offboarding last day; do not infer eligibility solely from offer status. Ordinary imported people are not automatically candidates.

## Lookup and review

`marketing_submission_options()` returns visible Vendor/Client/Position and stored status filter values. `marketing_list_submissions(q?, vendor?, client?, position?, status?, page?, page_size?)` accepts arrays of codes/exact statuses; values in a filter are OR, filters combine. Page starts at 1, size defaults 25 and max 100; respect total/pagination. Resolve one code then `marketing_get_workspace_submission(code)`. Interviews, offers and history are linked to that exact submission, never inferred from candidate-position similarity. Stored legacy/blank statuses are not normalized.

## Create or repeat a submission

1. `marketing_search_submission_candidates(q, page, page_size)` resolves an eligible person (no target-position filter); `marketing_search_submission_positions(q, page, page_size)` resolves an existing scoped position and its allowed levels. These selectors use page 1, size 25 by default, max 100. If candidate/position is missing, stop for manual readiness/position setup; see [candidate gap](create-candidate.md).
2. If an employer is needed, `marketing_search_submission_employers(q, page, page_size)` finds an existing shared company. It does not create one; use a separately confirmed [company workflow](company.md) if needed.
3. `marketing_check_submission(request={candidate_code, position_code})` returns all existing submissions for the pair. Show their codes/statuses/timestamps. Ask whether to reuse a specific existing record or create a separate one.
4. Confirm candidate, position, new `Active` record and editable details. Call `marketing_create_submission(request)` with required `candidate_code`, `position_code`, and optional fields below. Set `create_separate=true` **only** after explicit duplicate/separate-record confirmation when any record exists. There is no request UUID or idempotency guarantee.
5. Read returned code with `marketing_get_workspace_submission`; report saved data/version. Creation does not change the person or create a formal offer. Do not claim `submitted_at` defaults to now.

## Edit details

Read → resolve changed employer/position-level choices if needed → confirm diff → `marketing_update_workspace_submission(code, request={version, ...changed_fields})` → read back. Candidate, position, `status`, `customer_rate`, lead marker and closure fields are not writable through this patch. Editable details remain editable even on Rejected or legacy records; that does not reopen them.

Allowed optional fields:
- `submitted_at` (timezone-aware timestamp); `am_notes`.
- `level`: configured position level or empty; if no levels, leave empty. Existing lead submissions must retain Senior when level is edited.
- `submitted_rate`: USD/hour 0–500; `rate_type`: W2, C2C or 1099.
- `open_to_relocate`, `travel_availability`, `start_availability`, `interview_availability`, `same_client_history`: text, not invented dropdown values.
- `employer_code` (existing company), `contact_name`, `contact_email`, `contact_phone`.

Omitted fields stay unchanged; explicit null/blank clears optional fields subject to validation. Contact email/phone history only says `changed`; never reconstruct hidden history.

## Offered or rejected

Read exact submission/version and confirm each action separately:
- Active → Offered: `marketing_mark_submission_offered(code, request={version})`. **Does not create/modify a formal Offer.** Use [offer](offer.md) only on separate explicit intent.
- Active or Offered → Rejected: `marketing_reject_submission(code, request={version, reason})`; reason must be nonblank, max 4000 characters. Explain Rejected is terminal for status actions.

Read back status, reason and version. No reopening, deletion or automatic status inference from linked interviews/offers. Legacy/blank states cannot use these transitions.

## Recovery

On `confirmation_required`, rerun pair check and obtain separate-record consent. On `not_found`, stop: eligibility or scope may have changed. For `invalid_level`, `level_not_used`, `lead_level_required` or `employer_not_found`, refresh selectors and correct only with confirmation. For `invalid_transition`, read current status; do not force it via PATCH. On `version_conflict`, read and reconfirm. On unknown `submission_operation_failed`, list/check the pair and inspect exact records before considering retry: a create may already have committed. Sync wakeup failure is not rollback. Never duplicate a submission to repair sheet lag.
