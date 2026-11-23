# Add and update candidate information

Tools: `marketing_search_candidates`, `marketing_get_candidate_detail`, `marketing_get_candidate`, `marketing_list_candidate_options`, `marketing_add_candidate`, `marketing_search_addable_people`, `marketing_update_candidate`, the notes tools (`marketing_list_candidate_notes`, `marketing_add_candidate_note`, `marketing_update_candidate_note`, `marketing_delete_candidate_note`), the responsible-AM tools (`marketing_list_assignable_ams`, `marketing_assign_candidate_am`, `marketing_assign_candidates_am`, `marketing_unassign_candidate_am`) and `marketing_list_assignable_trainers`.

**Which of these tools you see depends on the token's permissions, not on a role name** (the backend checks `candidate::view`, `candidate::create`, `candidate::edit`, `candidate::note`, `candidate::delete`, `candidate::assign_am`): reading and searching, the options and the trainer list need `view`; `marketing_add_candidate`, `marketing_search_addable_people` need `create`; `marketing_update_candidate` needs `edit`; writing and changing notes needs `note`; deleting a note needs `delete`; the responsible-AM tools need `assign_am`. A tool that is not in the list means the user was not granted that permission: say so and stop; never try another tool, REST or a script to get around it. The vendor scope below still applies on top of the permissions. Granting or changing permissions is done in Authsome, and the user must sign in again for a change to take effect.

A candidate's data is in two places, and each has its own update tool:

| Data | Tool to change it |
| --- | --- |
| **The person**: names, years of experience, visa type and its start / expiry dates, email, phone, other emails, city / state (where the candidate lives for interviews), address, date of birth, gender, LinkedIn, Facebook, phone and laptop preference, SSN last 4, work authorization detail, splicing certification, candidate type, C2C employer, marketing status, consultant profile (tech stack, skillsets, year came to us, person origin, source vendor, Remap flag), HR record (W-2 start date, recruiter, WeCom ID, company) | `marketing_update_candidate` |
| **The submission** (the candidate on one position): level, lead, pay rate, updated rate, rate deduction, availability, same client history, the C2C employer written in that submission, rejecting and reopening | `marketing_update_workspace_submission`, `marketing_reject_submission`, `marketing_reopen_submission` (see `references/submission.md`) |

Read a candidate with **`marketing_get_candidate_detail`** (by person ID, no position needed): it returns the whole profile (including everything on the Consultant Details sheet: `marketing_phone` / `personal_phone`, `marketing_email` / `personal_email`, `ssn_last4`, `home_address` with `unit`, `emergency_contact`, `education` Bachelor / Master; the marketing mailbox password is never returned and not stored in the tool output), the submissions, interviews and offers on your vendors' positions, every event about the candidate, and the `version` that every update needs. `marketing_get_candidate` is the older read by the current position; use it only when the request needs the position-scoped view.

## Find candidates (`marketing_search_candidates`)

One tool for searching by name, email or ID (`query` alone) and for listing with filters; the Web list and the sheet menu take the very same filters. Filters (all optional, combinable): `vendor`, `client`, `position` (company / position codes), `candidate_type` (a category or a full value or `Not set`), `marketing_status` (one or more: In Preparation, Pause Marketing, In Marketing, On Hold, Offer, On Project, Remap, Quit, Fired, and the legacy Off Project, Pause, Withdrawn / MIA), `batch` (current training batch IDs `BAT-nnnnnn`, from `batches` in `marketing_list_candidate_options`), `batch_stack` (the Batch Stack, i.e. the family of the person's current batch, for example a technology stack; values are `batch_stacks` in `marketing_list_candidate_options`, matched ignoring case, several allowed, `Not set` means no current batch or a batch without a stack), `marketability` (High, Mid, Low or None, several allowed; see below), `assigned_am` (login emails of the AMs responsible for the candidate, or `Unassigned`), `current_status` (interview progress such as `L2 Cleared`), `lead`, `yoe_min` / `yoe_max` (years of experience, inclusive; people without years are left out), `page`, `page_size`.

- **Marketability** is worked out from the two evaluation scores (`tech_score`, `comm_score`) and is not stored. Every search row and the candidate detail show it as `marketability`. Each score gets a level and the **lower of the two wins**: Tech 4.0 or more is High, 3.5 or more is Mid, below 3.5 is Low; Comm 3.3 or more is High, 3.0 or more is Mid, below 3.0 is Low. Scores between two levels (3.95, 3.25) count as the lower level, so Tech 4 with Comm 2 is Low. `None` means a score is missing (the value is the word `None`, not empty). It does not depend on the candidate type. To list, for example, the Bench people who can be marketed best, combine `marketability: ["High"]` with `candidate_type: ["Bench"]`; to find who still needs scores, filter `marketability: ["None"]`.
- **Marketing status and Current Status are different things.** Marketing status is the person's marketing state (On Project, Remap, …). Current Status is worked out from one submission's interviews (L2 Scheduled, L2 Cleared, …) and is not stored.
- **`current_status` needs a position** (pass at least one `position` filter); otherwise the call is rejected with `current_status needs a position`.
- With no filter the list is everything you can see, not just one position. To find a person by name, send `query` only; do not add filters.

## Add a candidate (`marketing_add_candidate`)

One action with two sources. **A person already in the system** (for example someone who finished a batch): find them with `marketing_search_addable_people` (name, email or person ID; it lists people who are not candidates yet and have batch information), confirm the one person, then call `marketing_add_candidate` with `candidate.person_code` and, only if asked, `position` and `level`; **nothing else is accepted** for an existing person (change their data with the update afterwards). **A new person**: leave `person_code` out and follow the steps below. Either way the candidate starts as `In Preparation`.

### New person

Required: `candidate_type`, `first_name`, `last_name`, `email`. Everything else is optional: `middle_name`, `preferred_name`, `yoe` (0 to 40), `work_authorization` with `work_authorization_start_date` and `work_authorization_expires`, `phone`, address (`address_street`, `address_city`, `address_state` two-letter, `address_postal_code`), `date_of_birth` (`mm-dd-yyyy`), `gender`, `linkedin_url`, `facebook_url`, `phone_preference` (`iOS` or `Android`), `laptop_preference` (`Windows` or `Mac`), and for `Staffing - C2C` the `employer_name`.

1. **Candidate type**: `Skip Training`, `Staffing - W-2`, `Staffing - C2C` or `Staffing - 1099` for a new person. **Bench is not created as a new person**: add them from the existing people (above). If the user does not say the type, ask; never guess.
2. **Do not ask for optional fields the user did not mention**; send only what was given. Split a full name into first / middle / last yourself and show the split; split an address into its four parts.
3. **Check for duplicates**: the email or phone must not belong to another candidate (the error names the existing ID, report it and do not retry with another value). A candidate with the same name but another email is created with a warning; tell the user.
4. **Confirm** the fields as a short table, then call `marketing_add_candidate` (the fields go inside `candidate`). Never send a position here; submitting the candidate to a position is a separate step: call `marketing_create_submission` afterwards (see `references/submission.md`).
5. **Report** the new Candidate ID, the type, and the warnings.

## Update the person (`marketing_update_candidate`)

1. **Resolve the candidate** to exactly one person and read them with `marketing_get_candidate_detail` (current values and `version`).
2. **Map the request to fields**; send only the fields that change, with `changes.version`. `null` or empty text clears a field (first name, last name and email cannot be cleared). Check choice fields against `marketing_list_candidate_options` (state, work authorization, Candidate Type).
3. **Special cases:**
   - **Candidate type is required to edit.** A candidate without a type needs `candidate_type` in the same call; ask which one. `Bench` needs batch information on the person. A C2C employer only goes with `Staffing - C2C`; the W-2 start date only with `Bench` or `Staffing - W-2`; `company` (`BSS`, `BFS`, `INVIC`) only with `Bench` and needs the W-2 start date.
   - **Email and phone** must not belong to another candidate (the error names the existing ID); the old value is kept as history. Phone needs at least 10 digits.
   - **Name**: change the parts (`first_name`, `middle_name`, `last_name`, `preferred_name`); there is no `name` field. A part you do not send keeps its value, so send `middle_name: null` when the new name has no middle name. When the user gives only a full name, split it (first word = First, last word = Last, the rest = Middle; a suffix such as Jr. stays in Last) and show the split.
   - **Visa**: `work_authorization` is the type; the start and expiry dates are `work_authorization_start_date` and `work_authorization_expires` (`YYYY-MM-DD`; the expiry cannot be before the start).
   - **Address** is saved as four parts; changing it keeps the old address as history. **Date of birth** is `mm-dd-yyyy` and is open to everyone who can see the candidate. The change history shows address and date of birth as `changed`, without values.
   - **Marketing status** can be set by hand to `In Preparation`, `Pause Marketing` (a stage before Marketing: marketing is paused), `In Marketing`, `On Hold`, `Offer`, `On Project`, `Remap`, `Quit` or `Fired` (the legacy values `Off Project`, `Pause` and `Withdrawn / MIA` can exist but cannot be chosen). Offers drive it automatically at the moment they change (an Offered offer sets `Offer`, an On Project offer `On Project`, an ended one `Quit`, `Fired` or `Remap`, all offers canceled `In Marketing`); a value set by hand is not overwritten until the person's next offer change, and the reply warns when the value you set is normally automatic. `In Preparation`, `Pause Marketing`, `In Marketing`, `On Hold` and `Remap` are visible to every AM; the other states only to the vendors the candidate was submitted to or has an offer with. A candidate who is `On Hold` can be seen but cannot be submitted or get an interview.
4. **Confirm** with `field: old → new`, then call `marketing_update_candidate` with `code` and `changes`.
5. **Report** what was saved from the response (name, type, marketing status, new version) and any warning.

## Notes on person fields (`marketing_update_candidate`)

`changes.version` is the candidate's version (read with `marketing_get_candidate_detail`). Updated rate and rate deduction belong to the submission: change them with `marketing_update_workspace_submission` (see `references/submission.md`).

Not editable anywhere on a candidate: offer status, start date and Current Status. They come from the offers (see `references/offer.md`) and the interviews.

- `other_emails` (list, each unique across all candidates) **replaces** the whole list. To add one address, send the existing list plus the new one; to remove one, send the list without it. Show the final list in the confirmation.
- Withdrawn or dropped is no longer set here: reject the submission with `marketing_reject_submission` and the rejecting party (`Candidate` withdrew, `Company` dropped). Cancelling an offer does not reject the submission; use the offer workflow (see `references/offer.md`).
- `city` / `state` (two-letter code) are where the candidate lives for interviews, not the onboarding address.
- Consultant profile fields (all in `marketing_get_candidate_detail`, editable through `marketing_update_candidate` except `drive_folder_id`): `additional_tech_stacks` (technology stack, free text; Candidate matching reads it and refreshes its index in the background), `skillsets` (free text), `year_came_to_us` (1900 to 2200), `person_origin` (free text), `is_remap` (true / false; null is treated as not sent) and `supplier_company_id` (source vendor company, an existing internal company id; shown with `supplier_company_name`). Empty text or null clears a text or year field; unsent fields stay. `drive_folder_id` is read only (managed by the consultant form flow): never send it, it is rejected. `supplier_company_id` cannot be sent together with `employer_name`, and not for `Staffing - C2C` (use `employer_name` there). Edited columns are protected from the next import (`manual_fields`).
- `ssn_last4` takes exactly 4 digits: a full 9-digit SSN is saved as its last 4 (say so), anything else is rejected.
- A candidate in the pool (`In Preparation`, `Pause Marketing`, `In Marketing`, `On Hold` or `Remap`) from another vendor is visible to you, but a candidate on another vendor's project is not (`Not found`).

## Responsible AM (`marketing_assign_candidate_am` and friends)

A candidate can have several **responsible AMs** (the logins that maintain the candidate before a project); they decide who may edit the candidate when there is no offer. The candidate detail and every search row show them as `assigned_ams`; filter with `assigned_am` (login emails, or `Unassigned` for people nobody is responsible for).

1. Needs `candidate::assign_am`. Read the choices with `marketing_list_assignable_ams` (active Authsome members; 503 means the list is unavailable, nothing else is affected). The email must be in that list.
2. One candidate: `marketing_assign_candidate_am(code, email)`; take one off with `marketing_unassign_candidate_am(code, email)` (works even when the person left Authsome). Assigning someone already assigned changes nothing.
3. Many candidates, one AM: `marketing_assign_candidates_am(codes, email)`, at most 500 IDs per call; IDs that do not exist, that you cannot see or that are not candidates are listed and skipped; repeating it is safe. To give every unassigned candidate an AM, search with `assigned_am: ["Unassigned"]`, show the count, confirm, then assign in batches.
4. Confirm the AM and the candidate(s) before writing; report the result's `assigned_ams` (or the skipped list).

## AM notes (`marketing_*_candidate_note`)

Notes are a comment record on the candidate. List them with `marketing_list_candidate_notes(code)` (needs `view`; newest first, with who wrote each and whether you may edit or delete it). Write one with `marketing_add_candidate_note(code, body)` (needs `note`, up to 4000 characters, you are the author). Change one with `marketing_update_candidate_note(code, note_id, body, version)` (needs `note`; only the author, imported notes without an author only an admin; a stale `version` is rejected: list again and retry). Delete one with `marketing_delete_candidate_note(code, note_id)` (needs `delete`, cannot be restored): confirm the exact note first. Notes may contain personal information: show only what the user asked for and do not copy them into other tools, emails or records.

## Evaluation trainers

`marketing_update_candidate` also edits the evaluation (`tech_score`, `comm_score`, `tech_trainer_emails`, `comm_trainer_emails`). Choose trainers from `marketing_list_assignable_trainers` (active Authsome members with the Trainer role; needs `view`; 503 when the list is unavailable). Scores are numbers from 1 to 5 with at most two decimals. Marketability is computed from the two scores, so changing them can change it.

## Do not

- Do not send unknown fields; the tools reject them.
- Do not bulk-edit several candidates from one confirmation; confirm each candidate separately.
- Deleting a candidate (or turning a Bench person back into a non-candidate) is not available here: it needs `candidate::delete` and is done in the web back office only. For an interview created from wrong data use `references/delete.md`; offers are canceled, not deleted (`references/offer.md`).
