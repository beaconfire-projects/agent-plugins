# Create a Marketing candidate

Use for a candidate goal or a missing candidate dependency of Submission/Offer. Follow [Create orchestration](create-orchestration.md): search/reuse first, ask for missing/ambiguous information together, then create without routine per-dependency confirmation. Ordinary Person creation/import does not establish candidate readiness.

## Tools and scope

One create tool: **`marketing_add_candidate(candidate={...})`**. Its decorator tags are `staffing`, `marketing`, `candidates` (verified on the deployed backend, image 0.1.0-169). The same four-tool set is used for create and readback:

| Need | Tool |
|---|---|
| Find an existing candidate by code, email or name | `marketing_search_candidates(query=...)` |
| Find an existing Person who can become a candidate (the Bench list: has batch information) | `marketing_search_addable_people(query=...)` |
| Create / convert | `marketing_add_candidate(candidate={...})` |
| Read back | `marketing_get_candidate_detail(code)` |

Every `marketing_*` business tool also accepts an optional `position` argument added by the server; creating a candidate does not depend on a position, so never send it. Creation is available to Admin/Manager and to AMs. When an **AM** creates a candidate, that AM is assigned as the responsible AM after the create has committed; this second step is best-effort, so report any warning and never recreate to repair the assignment. Admin/Manager are not auto-assigned. This tool creates no Submission, Interview or Offer.

Do not use REST, SQL, scripts, or candidate **update / AM-assignment / note** tools from this workflow: they are outside this skill.

## Search and choose a path

1. Call `marketing_search_candidates(query=…)` with the supplied code, email or name and compare exact identity. Reuse an unambiguous existing candidate instead of creating another. The search lists only what the caller is allowed to see, so an empty result does not prove the person is absent.
2. To convert an existing Person, call `marketing_search_addable_people(query=…)`. Without a query it lists only people who are not candidates yet; with a query it also lists people who already are (`is_candidate` true: they cannot be added again, reuse them). Take the exact `person_code` from this result.
3. If neither finds the person and the request has complete identity for a genuinely new person, create a new one and rely on the server duplicate checks; do not claim comprehensive absence, and do not use create to probe for identities.
4. Admin/Manager may additionally inspect Person records with `marketing_list_people` / `marketing_get_person` (`marketing,people`). AMs cannot; do not bypass the denial.

### Existing Person → Bench

Call **`marketing_add_candidate(candidate={person_code: "PER-…"})` only**. Do not send any other key, even null/default values. The Person must exist, must not already be a candidate, and must have batch information; the result is a Bench candidate that starts at marketing status `In Preparation`. A missing batch means stop for a genuine readiness correction; never manufacture HR/batch data to force conversion. Other candidate types are not supported by this path. Read the result back and report the returned `marketing_status` instead of promising what happens to an existing status.

### New Person + candidate, one call

Do **not** create a standalone Person first. Send required `candidate_type`, `first_name`, `last_name`, `email`. Types: `Skip Training`, `Staffing - W-2`, `Staffing - C2C`, `Staffing - 1099`. `Bench` is not a new-person type (a Bench candidate is created only by converting an existing Person). Ask for the type and legal names when missing. The new candidate starts at `In Preparation`.

Optional fields, only when supplied (formats come from the tool schema; the server validates and reports the field on error, so correct that field instead of guessing):
- `middle_name`, `preferred_name`, `phone`, `yoe` (integer 0–40), `gender`, `linkedin_url` and `facebook_url` (each at most 300 characters), `phone_preference` (iOS/Android), `laptop_preference` (Windows/Mac).
- `work_authorization`, `work_authorization_start_date`, `work_authorization_expires`: use only values the tool schema allows; dates are ISO.
- `address_street`, `address_city`, `address_state` (two-letter US state), `address_postal_code` (`12345` or `12345-6789`). `date_of_birth` is `mm-dd-yyyy`, unlike the ISO dates. Minimize sensitive data in replies; there is no SSN field.
- `work_arrangement_preference` (Remote/On-site/Hybrid/Open), `relocation_willingness` (Open/Conditional/Not open), `preferred_time_zones` (Eastern/Central/Mountain/Pacific), `location_note` (at most 2000 characters, required when relocation is Conditional). Do not infer restrictions from time-zone preferences.
- `employer_name`, only for `Staffing - C2C`, optional; see below.

Unknown fields are rejected: no `position`, `level`, `auto_submit`, batch, candidate status or responsible-AM list.

## C2C employer is a name-based special case

Before supplying `employer_name`, search `marketing_list_companies(q)` and inspect exact names with `marketing_get_company`. Resolve ambiguous names with the user. The server matches the display name case-insensitively after trimming, reuses the first exact match, or creates a new company flagged as C2C. It does not accept an employer code, company roles or flags, and does not return the company code. If duplicate exact names cannot be told apart through this name-only contract, stop that association rather than let it pick an unintended company. Do not invent Vendor/Client roles for it. A Submission's `employer_code` is a separate optional association: resolve it through the submission employer selector and do not assume it is copied from the candidate.

## Readback, errors and unknown outcomes

- Success returns only `code`, `name`, `candidate_type`, `warnings`. Record that success immediately, then read the candidate back with `marketing_get_candidate_detail(code)` (profile, `version`, `marketing_status`, `assigned_ams`). Before Submission, also confirm eligibility with `marketing_search_submission_candidates(q=returned_code)`; that selector is the Submission eligibility gate. A missing selector result does not undo a successful create: report the saved ID and the blocked eligibility, and do not recreate or change the status automatically.
- Duplicate email or phone: the request is rejected and the error names the existing person ID. If that person is not a candidate yet, convert it with `person_code`; if already a candidate, reuse it. Never change contact data to evade the duplicate. A person with the same name but a different email is created with a nonblocking warning; it is not proof that the identities are distinct or permission to merge them.
- Already a candidate: do not convert again; verify identity and reuse. Invalid type/batch/field: correct the real issue, not a fabricated default. Forbidden / not found: stop within the authorized scope.
- Audit: candidate create/convert is recorded under `module=staffing`, `entity=candidate`, and can be read with `marketing_get_history(code)`.
- Unknown or transport failure: no idempotency key exists. First search by the known code, otherwise the supplied email or name, and read the detail; presence proves the current state, not every requested field or that this attempt created it. If identity, candidacy or outcome remains uncertain, **stop and report a verification gap**, keep the payload and known IDs, and ask for manual verification; never resend the create/conversion to test whether it committed.

Preserve all successful dependencies and resume only from verified state; never automatically delete, reimport or recreate any Person, candidate or company.
