# Shared person management

All four people tools require `current_scope().all_vendors` (Admin/Manager-style access), including get, update and import, not just list. No position parameter is used. Do not promise ordinary AM access or bypass denial through candidate tools.

## Lookup

Use `marketing_list_people(query?, page=1, page_size=50)` (max 500) to resolve name/email/Person ID. Ask if ambiguous; paginate rather than assuming the first page is complete. `marketing_get_person(code)` returns shared person, contacts, HR, work authorizations, consultant-info (read-only here), current batch and version. It intentionally excludes SSN last four and addresses. To find eligible submission candidates instead, use [submission selectors](submission.md), not broad person lookup as a scope workaround.

## Edit shared fields, HR, authorization or current batch

1. Read the exact `PER-…` record. Establish requested fields and authority; use minimal sensitive data in confirmation.
2. Prepare `changes={version, ...changed_fields}` for `marketing_update_person(code, changes)`. Show old → new, including any current contact replacement or batch clearing; wait for confirmation.
3. Write once, then `marketing_get_person(code)` and report saved fields/current records/version. This also marks the Person Master read-only sheet projection dirty; it does not guarantee immediate sheet delivery.

Writable top-level fields: `first_name`, `middle_name`, `last_name`, `preferred_name`, `email`, `phone`, `birth_date`, `gender`, `visible_to_team`, `is_internal`, `data_note`, `hr_info`, `work_authorization_type`, `work_authorization_start_date`, `work_authorization_expiration_date`, `batch_id`.

Constraints and distinctions:
- First and last names cannot become empty when names change. Email cannot be cleared; it is trimmed/lowercased and checked against other people's primary and alternate emails. Updating email replaces current contact entries; phone may clear, and a lookup entry is only produced for a number with at least ten digits (last ten form the key).
- Send `hr_info` as a **partial object** of schema fields; omitted nested fields stay. Explicit `hr_info=null` does not delete HR information. Nested nullable fields can be cleared. Fields include payroll/employment dates/status, recruiter ID/name, entry/batch notes, I9/E-Verify, warning/risk, visa reach-out, POCs, termination and ADP/checklist fields, notes and `wecom_id`; use only fields exposed in the current schema, not imported column headers. HR checkboxes record data; they do not perform HR tasks. Do not casually change the `wecom_id` import identity.
- Authorization updates affect the latest current authorization; merged expiration must not precede start. With no current record, a type is necessary to create one; dates alone will not create an authorization. Check readback rather than claiming success from submitted fields alone.
- Explicit `batch_id=null` clears the current batch. A nonempty ID must exist; there is no allowed batch-list/create tool. Use a verified ID supplied by an authorized operator or returned from an existing record; otherwise stop for manual lookup. Do not guess a batch from a name.
- Consultant-only data and candidate conversion/marketing status are not writable here. Readable years of experience, social URLs and device preferences are also not accepted by this update schema. No address or SSN edits.

## Recovery

Permission failure: stop for an authorized operator. Not found: do not probe other identities. Stale version: read and reconfirm. Duplicate email/phone conflict: ask the user to resolve ownership, never overwrite/merge people. Invalid dates/names or unknown batch ID: correct the proposed diff and reconfirm. Unknown error (including possible post-commit sync failure): read back before retrying. There is no person history/delete/rollback tool in this boundary. A valid no-op or ignored authorization-date-only update must not be reported as a saved requested value.

For new people read [create person](create-person.md); for candidates read [candidate gap](create-candidate.md).
