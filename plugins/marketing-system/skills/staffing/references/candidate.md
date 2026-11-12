# Add and update candidate information

Tools: `marketing_search_candidates`, `marketing_get_candidate_detail`, `marketing_get_candidate`, `marketing_list_options`, `marketing_add_candidate`, `marketing_search_addable_people`, `marketing_update_candidate`, `marketing_update_candidate_submission`.

A candidate's data is in two places, and each has its own update tool:

| Data | Tool to change it |
| --- | --- |
| **The person**: names, years of experience, visa type and its start / expiry dates, email, phone, address, date of birth, gender, LinkedIn, Facebook, phone and laptop preference, candidate type, C2C employer, marketing status, HR record (W-2 start date, recruiter, WeCom ID, company) | `marketing_update_candidate` |
| **The submission** (the candidate on one position): pay rate, availability, same client history, the C2C employer written in that submission | `marketing_update_submission` (see `references/submission.md`) |
| **Level, lead, Status Override, updated rate, rate deduction, OSHA, splicing, other emails, city / state, SSN last 4 and the rest of the onboarding profile** | `marketing_update_candidate_submission` (see "Other fields" below) |

Read a candidate with **`marketing_get_candidate_detail`** (by person ID, no position needed): it returns the whole profile, the submissions, interviews and offers on your vendors' positions, every event about the candidate, and the `version` that every update needs. `marketing_get_candidate` is the older read by the current position; use it only when the request is about `include_profile` fields it alone returns (SSN last 4).

## Find candidates (`marketing_search_candidates`)

One tool for searching by name, email or ID (`query` alone) and for listing with filters; the Web list and the sheet menu take the very same filters. Filters (all optional, combinable): `vendor`, `client`, `position` (company / position codes), `candidate_type` (a category or a full value or `Not set`), `marketing_status` (one or more: In Preparation, In Marketing, On Hold, Offer, On Project, Remap, Quit, Fired), `current_status` (interview progress such as `L2 Passed`), `lead`, `yoe_min` / `yoe_max` (years of experience, inclusive; people without years are left out), `page`, `page_size`.

- **Marketing status and Current Status are different things.** Marketing status is the person's marketing state (On Project, Remap, …). Current Status is worked out from one submission's interviews (L2 Scheduled, L2 Passed, …) and is not stored.
- **`current_status` needs a position** (`position`, or the only one you can see); otherwise the call is rejected with `current_status needs a position`.
- With no filter the list is everything you can see, not just one position. To find a person by name, send `query` only; do not add filters.

## Add a candidate (`marketing_add_candidate`)

One action with two sources. **A person already in the system** (for example someone who finished a batch): find them with `marketing_search_addable_people` (name, email or person ID; it lists people who are not candidates yet and have batch information), confirm the one person, then call `marketing_add_candidate` with `candidate.person_code` and, only if asked, `position` and `level`; **nothing else is accepted** for an existing person (change their data with the update afterwards). **A new person**: leave `person_code` out and follow the steps below. Either way the candidate starts as `In Preparation`.

### New person

Required: `candidate_type`, `first_name`, `last_name`, `email`. Everything else is optional: `middle_name`, `preferred_name`, `yoe` (0 to 40), `work_authorization` with `work_authorization_start_date` and `work_authorization_expires`, `phone`, address (`address_street`, `address_city`, `address_state` two-letter, `address_postal_code`), `date_of_birth` (`mm-dd-yyyy`), `gender`, `linkedin_url`, `facebook_url`, `phone_preference` (`iOS` or `Android`), `laptop_preference` (`Windows` or `Mac`), and for `Staffing - C2C` the `employer_name`.

1. **Candidate type**: `Skip Training`, `Staffing - W-2`, `Staffing - C2C` or `Staffing - 1099` for a new person. **Bench is not created as a new person**: add them from the existing people (above). If the user does not say the type, ask; never guess.
2. **Do not ask for optional fields the user did not mention**; send only what was given. Split a full name into first / middle / last yourself and show the split; split an address into its four parts.
3. **Check for duplicates**: the email or phone must not belong to another candidate (the error names the existing ID, report it and do not retry with another value). A candidate with the same name but another email is created with a warning; tell the user.
4. **Confirm** the fields as a short table, then call `marketing_add_candidate` (the fields go inside `candidate`). Give `position` (a `POS-…` of your own vendor) only when the user asked to submit the candidate to a position as well; the submission is a separate step, and you can set its details in the same call with `marketing_submit_candidate_to_position` (see `references/submission.md`).
5. **Report** the new Candidate ID, the type, and the warnings.

## Update the person (`marketing_update_candidate`)

1. **Resolve the candidate** to exactly one person and read them with `marketing_get_candidate_detail` (current values and `version`).
2. **Map the request to fields**; send only the fields that change, with `changes.version`. `null` or empty text clears a field (first name, last name and email cannot be cleared). Check choice fields against `marketing_list_options` (state, work authorization).
3. **Special cases:**
   - **Candidate type is required to edit.** A candidate without a type needs `candidate_type` in the same call; ask which one. `Bench` needs batch information on the person. A C2C employer only goes with `Staffing - C2C`; the W-2 start date only with `Bench` or `Staffing - W-2`; `company` (`BSS`, `BFS`, `INVIC`) only with `Bench` and needs the W-2 start date.
   - **Email and phone** must not belong to another candidate (the error names the existing ID); the old value is kept as history. Phone needs at least 10 digits.
   - **Name**: change the parts (`first_name`, `middle_name`, `last_name`, `preferred_name`); there is no `name` field. A part you do not send keeps its value, so send `middle_name: null` when the new name has no middle name. When the user gives only a full name, split it (first word = First, last word = Last, the rest = Middle; a suffix such as Jr. stays in Last) and show the split.
   - **Visa**: `work_authorization` is the type; the start and expiry dates are `work_authorization_start_date` and `work_authorization_expires` (`YYYY-MM-DD`; the expiry cannot be before the start).
   - **Address** is saved as four parts; changing it keeps the old address as history. **Date of birth** is `mm-dd-yyyy` and is open to everyone who can see the candidate. The change history shows address and date of birth as `changed`, without values.
   - **Marketing status** can be set by hand to `In Preparation`, `In Marketing`, `On Hold`, `Offer`, `On Project`, `Remap`, `Quit` or `Fired` (the legacy values `Off Project`, `Pause` and `Withdrawn / MIA` can exist but cannot be chosen). There is no automation yet except the existing rule that follows offers (an active offer sets `On Project`; an ended one sets `Quit`, `Fired` or `Remap`). `In Preparation`, `In Marketing` and `Remap` are visible to every AM; the other states only to the vendors the candidate was submitted to or has an offer with.
4. **Confirm** with `field: old → new`, then call `marketing_update_candidate` with `code` and `changes`.
5. **Report** what was saved from the response (name, type, marketing status, new version) and any warning.

## Other fields (`marketing_update_candidate_submission`)

For the fields `marketing_update_candidate` does not take. `changes.version` is the candidate's version (read with `marketing_get_candidate`).

| Group | Fields |
| --- | --- |
| Contact | `other_emails` (list, each unique across all candidates) |
| Location | `city`, `state` (two-letter code) |
| Position-related | `level`, `is_lead`, `osha_certification`, `splicing_experience` |
| Pay | `updated_rate` (USD per hour), `rate_deduction` (USD, may be negative) |
| Status | `status_override`: Candidate Withdrew or Company Dropped (wins over every other status) |
| Onboarding profile | `profile`: `ssn_last4`, `work_authorization_detail`, `phone_preference`, `laptop_preference`, `splicing_certification`, `fb_url` (the address, phone, date of birth and gender are also accepted there, but change them with `marketing_update_candidate`) |

Not editable anywhere on a candidate: Offer Status, Start Date and Current Status. They come from the onboarding record and the interviews (see the onboarding workflows).

- `other_emails` **replaces** the whole list. To add one address, send the existing list plus the new one; to remove one, send the list without it. Show the final list in the confirmation.
- `status_override` set to Candidate Withdrew or Company Dropped overrides the interview status. "The candidate gave up / left" is **Candidate Withdrew**; "we dropped the candidate / ended the cooperation / company drop" is **Company Dropped**. If the user only says "drop" or "stop working with" and it is not clear who ended it, ask. Company Dropped needs a reason (`Candidate Issue`, `Duplicate` or the user's own text). Clear it with `null` only when asked. While the candidate's offer is canceled, the override and its reason are refused: undo the cancellation first (see `onboarding-cancel.md`).
- `ssn_last4` takes exactly 4 digits: a full 9-digit SSN is saved as its last 4 (say so), anything else is rejected.
- A candidate who is `In Preparation` or `In Marketing` from another vendor is visible to you in the pool but a candidate on another vendor's project is not (`Not found`).

## Do not

- Do not send unknown fields; the tools reject them.
- Do not bulk-edit several candidates from one confirmation; confirm each candidate separately.
- Deleting a candidate is not available here: it is done by an Admin in the web back office only. For an interview or onboarding record created from wrong data use `references/delete.md`.
