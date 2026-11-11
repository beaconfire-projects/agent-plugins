# Create and update candidate information

Tools: `staffing_search_candidates`, `staffing_get_candidate_detail`, `staffing_get_candidate`, `staffing_list_options`, `staffing_create_candidate`, `staffing_search_bench_pool`, `staffing_convert_person_to_candidate`, `staffing_update_person`, `staffing_update_candidate`.

A candidate's data is in two places, and each has its own update tool:

| Data | Tool to change it |
| --- | --- |
| **The person**: names, years of experience, visa type and its start / expiry dates, email, phone, address, date of birth, gender, LinkedIn, Facebook, phone and laptop preference, candidate type, C2C employer, marketing status, HR record (W-2 start date, recruiter, WeCom ID, company) | `staffing_update_person` |
| **The submission** (the candidate on one position): pay rate, availability, same client history, the C2C employer written in that submission | `staffing_update_submission` (see `references/submission.md`) |
| **Level, lead, Status Override, updated rate, rate deduction, OSHA, splicing, other emails, city / state, SSN last 4 and the rest of the onboarding profile** | `staffing_update_candidate` (see "Other fields" below) |

Read a candidate with **`staffing_get_candidate_detail`** (by person ID, no position needed): it returns the whole profile, the submissions, interviews and offers on your vendors' positions, every event about the candidate, and the `version` that every update needs. `staffing_get_candidate` is the older read by the current position; use it only when the request is about `include_profile` fields it alone returns (SSN last 4).

## Create a candidate

Required: `candidate_type`, `first_name`, `last_name`, `email`. Everything else is optional: `middle_name`, `preferred_name`, `yoe` (0 to 40), `work_authorization` with `work_authorization_start_date` and `work_authorization_expires`, `phone`, address (`address_street`, `address_city`, `address_state` two-letter, `address_postal_code`), `date_of_birth` (`mm-dd-yyyy`), `gender`, `linkedin_url`, `facebook_url`, `phone_preference` (`iOS` or `Android`), `laptop_preference` (`Windows` or `Mac`), and for `Staffing - C2C` the `employer_name`.

1. **Candidate type**: `Skip Training`, `Staffing - W-2`, `Staffing - C2C` or `Staffing - 1099` for a new person. **Bench is not created**: search the person with `staffing_search_bench_pool` (someone with batch information who is not a candidate yet), then `staffing_convert_person_to_candidate`. If the user does not say the type, ask; never guess.
2. **Do not ask for optional fields the user did not mention**; send only what was given. Split a full name into first / middle / last yourself and show the split; split an address into its four parts.
3. **Check for duplicates**: the email or phone must not belong to another candidate (the error names the existing ID, report it and do not retry with another value). A candidate with the same name but another email is created with a warning; tell the user.
4. **Confirm** the fields as a short table, then call `staffing_create_candidate`. Give `position` (a `POS-…` of your own vendor) only when the user asked to submit the candidate to a position as well; the submission is a separate step, and you can set its details in the same call with `staffing_submit_candidate_to_position` (see `references/submission.md`).
5. **Report** the new Candidate ID, the type, and the warnings.

## Update the person (`staffing_update_person`)

1. **Resolve the candidate** to exactly one person and read them with `staffing_get_candidate_detail` (current values and `version`).
2. **Map the request to fields**; send only the fields that change, with `changes.version`. `null` or empty text clears a field (first name, last name and email cannot be cleared). Check choice fields against `staffing_list_options` (state, work authorization).
3. **Special cases:**
   - **Candidate type is required to edit.** A candidate without a type needs `candidate_type` in the same call; ask which one. `Bench` needs batch information on the person. A C2C employer only goes with `Staffing - C2C`; the W-2 start date only with `Bench` or `Staffing - W-2`; `company` (`BSS`, `BFS`, `INVIC`) only with `Bench` and needs the W-2 start date.
   - **Email and phone** must not belong to another candidate (the error names the existing ID); the old value is kept as history. Phone needs at least 10 digits.
   - **Name**: change the parts (`first_name`, `middle_name`, `last_name`, `preferred_name`); there is no `name` field. A part you do not send keeps its value, so send `middle_name: null` when the new name has no middle name. When the user gives only a full name, split it (first word = First, last word = Last, the rest = Middle; a suffix such as Jr. stays in Last) and show the split.
   - **Visa**: `work_authorization` is the type; the start and expiry dates are `work_authorization_start_date` and `work_authorization_expires` (`YYYY-MM-DD`; the expiry cannot be before the start).
   - **Address** is saved as four parts; changing it keeps the old address as history. **Date of birth** is `mm-dd-yyyy` and is open to everyone who can see the candidate. The change history shows address and date of birth as `changed`, without values.
   - **Marketing status** can be set by hand only between `In Preparation` and `In Marketing` (a candidate coming back from `Remap` goes to one of them). `On Project`, `Off Project` and `Remap` follow the offer and cannot be set.
4. **Confirm** with `field: old → new`, then call `staffing_update_person` with `code` and `changes`.
5. **Report** what was saved from the response (name, type, marketing status, new version) and any warning.

## Other fields (`staffing_update_candidate`)

For the fields `staffing_update_person` does not take. `changes.version` is the candidate's version (read with `staffing_get_candidate`).

| Group | Fields |
| --- | --- |
| Contact | `other_emails` (list, each unique across all candidates) |
| Location | `city`, `state` (two-letter code) |
| Position-related | `level`, `is_lead`, `osha_certification`, `splicing_experience` |
| Pay | `updated_rate` (USD per hour), `rate_deduction` (USD, may be negative) |
| Status | `status_override`: Candidate Withdrew or Company Dropped (wins over every other status) |
| Onboarding profile | `profile`: `ssn_last4`, `work_authorization_detail`, `phone_preference`, `laptop_preference`, `splicing_certification`, `fb_url` (the address, phone, date of birth and gender are also accepted there, but change them with `staffing_update_person`) |

Not editable anywhere on a candidate: Offer Status, Start Date and Current Status. They come from the onboarding record and the interviews (see the onboarding workflows).

- `other_emails` **replaces** the whole list. To add one address, send the existing list plus the new one; to remove one, send the list without it. Show the final list in the confirmation.
- `status_override` set to Candidate Withdrew or Company Dropped overrides the interview status. "The candidate gave up / left" is **Candidate Withdrew**; "we dropped the candidate / ended the cooperation / company drop" is **Company Dropped**. If the user only says "drop" or "stop working with" and it is not clear who ended it, ask. Company Dropped needs a reason (`Candidate Issue`, `Duplicate` or the user's own text). Clear it with `null` only when asked. While the candidate's offer is canceled, the override and its reason are refused: undo the cancellation first (see `onboarding-cancel.md`).
- `ssn_last4` takes exactly 4 digits: a full 9-digit SSN is saved as its last 4 (say so), anything else is rejected.
- A candidate who is `In Preparation` or `In Marketing` from another vendor is visible to you in the pool but a candidate on another vendor's project is not (`Not found`).

## Do not

- Do not send unknown fields; the tools reject them.
- Do not bulk-edit several candidates from one confirmation; confirm each candidate separately.
- To remove a candidate created from wrong data, use `references/delete.md`, not an edit.
