# Shared Person / HR: lookup, edit, single deletion and audit

All eight Person tools require Admin/Manager-style all-vendor access. They use no `position`. Ordinary AM denial must not be bypassed through candidate tools.

## Find the person

Use `marketing_list_people(query?, page=1, page_size=50)` (max 500). Search supports legal/preferred name, PER ID, primary/alternate email, phone and WeCom ID; words narrow the results. Paginate, then show code, name and a minimal contact to distinguish people. A match is not permission to modify every result. Read one selected `marketing_get_person(code)` for version, common fields, HR, contacts, current/historical authorization, current batch and read-only consultant information. No SSN/address fields are exposed.

For a person who needs an interview, search actual submissions with the [Interview selector](interview.md); a Person match alone does not establish submission eligibility. For creating a Person use [Create person](create-person.md); for candidate conversion use [Create candidate](create-candidate.md).

## Edit

1. Read the exact person and identify requested changes. No fields beyond `version` are universally required for a patch. When changing legal names, first and last must remain nonblank. Obtain missing information together rather than issuing one question per field.
2. For batch or visa changes, call `marketing_get_person_options()` for current batch IDs/names/category/track, allowed authorization values and existing HR Recruiters. Resolve ambiguous batch names with the user; do not invent an ID or create a batch through this tool.
3. Show only proposed old → new values, explicit clears, contact replacements and current batch changes. Obtain confirmation, then call `marketing_update_person(code, changes={version,...})` once. Omitted top-level and nested HR fields are preserved. A true no-op does not advance the version.
4. Read back the exact person and verify the saved fields/version. `marketing_get_person_history(code)` exposes actual field changes, actor, channel and time, including new HR imports and existing candidate/profile audit entries. A missing historic log is not proof no past modification occurred. This reader filters `module=staffing`; it does not expose the independent Marketing candidate create/conversion or creator-assignment audits (`module=marketing`) and cannot verify those attempts.

## Delete one Person

Use only `marketing_delete_person(code, version)` for an explicit request to delete **one selected Person**. First read `marketing_get_person(code)` and its current `version` and `submission_count`. Any existing Submission blocks deletion. This is the only business-reference blocker; do not invent additional Interview, Offer, candidate-flag or role checks. Admin/Manager-style access and optimistic version checks still apply.

Show the exact PER code, name and minimal identifying contact, and explain that this permanently removes the Person and owned profile/contact/role records while retaining the operation audit. Obtain explicit confirmation for that record, then call once. Never delete a linked Submission to bypass the blocker, offer a cascade, or expand a search result into bulk deletion. There is no bulk-delete tool.

A successful response returns the deleted code. Check that the exact record is no longer available and report success from the delete response; a subsequent not-found by itself is insufficient evidence. On a stale version, reread and reconfirm; on an unknown outcome, inspect the exact record before any retry. The same-transaction deletion audit includes actor, channel, time and before-values with sensitive fields redacted; deletion rolls back if audit fails. Audit history remains stored even though the deleted Person detail/history endpoint may no longer be available.

## Fields and meanings

| Group | Fields / behavior |
| --- | --- |
| Identity | `first_name`, `middle_name`, `last_name`, `preferred_name`, `birth_date`, `gender`. Use legal names as separate parts; preferred name is not the legal first name. Birth date changes are redacted in audit. |
| Contact | `email`, `phone`, `additional_emails`, `additional_phones`. Primary email cannot clear and is normalized/lowercased; ownership conflicts reject without merge. Changing primary preserves other current alternate contacts. Additional lists replace the complete current **additional** set; `[]` clears that set. Historical contacts remain. A phone's lookup key is its last 10 digits. |
| Professional / preferences | `years_of_experience` (0–80), `linkedin_url`, `facebook_url` (complete http/https), `phone_preference`, `laptop_preference`, `visible_to_team`, `is_internal`, `data_note`. Do not infer visibility/internal status from job title. |
| HR recruiter | Choose an option returned by `marketing_get_person_options().recruiters`: it provides Person code, source HR Sheet `recruiter_id`, name and email. Supply `hr_info.recruiter_id`; the server fills `recruiter_name`. Null clears both. A standalone name edit is rejected. Recruiter roles are created by exact import references, with no role-directory create/edit tool. These HR Persons are distinct from Interview company-contact recruiters. |
| HR | Partial `hr_info` object: payroll company, job position, employment/previous status; W2/entry/last-ADP dates; recruiter ID/name and POCs; batch notes; I9/E-Verify; warning/risk/visa follow-up; ADP/Dropbox/reporting/system/checklist flags; termination reason/notes; HR notes; WeCom ID. Use the deployed schema names and types. These store facts; checking a box does not run an external HR operation. `hr_info=null` does not delete the profile; nullable nested fields may clear. |
| Authorization | `work_authorization_type`, `work_authorization_detail`, `work_authorization_start_date`, `work_authorization_expiration_date` modify the latest current record. Type is necessary for dates/details without an existing authorization. Expiration must not precede start. Explicitly clearing type deactivates the current authorization, retaining history. Confirm this effect. |
| Batch | `batch_id` sets the current batch; null clears current membership. Use returned options. It does not create a training batch or change consultant eligibility. |

`is_consultant`, consultant-only attributes, source, IDs, version timestamps and identity-verification timestamps are not writable here. Do not send candidate conversion, marketing-status, SSN, address, submission rate/availability, or interview fields to a Person patch. Employment-status text is HR data, not the candidate's computed marketing stage.

## Recovery and audit

On stale version, reread and reconfirm the new diff. A duplicate identity/contact needs ownership review, never an overwrite or merge. Unknown outcome: inspect the person and history before retrying. New manual changes mark the applicable master/HR/authorization columns in `manual_fields` and write a same-transaction audit; contacts/batch associations have no `manual_fields` column and are represented by actual contact/membership state and audit. Do not claim all historical operations were backfilled with logs. Sheet updates are asynchronous projections, not evidence that an email, payroll or other task ran.
