# Update candidate information

Tools: `staffing_search_candidates`, `staffing_get_candidate`, `staffing_list_options`, `staffing_update_candidate`.

## Editable fields

| Group | Fields |
| --- | --- |
| Name | `first_name`, `middle_name`, `last_name`, `preferred_name` (or `name` for the full name) |
| Contact | `email` (primary, unique), `other_emails` (list, each unique across all candidates) |
| Location | `city`, `state` (two-letter code) |
| Profile of the person | `work_authorization`, `level`, `yoe` (0 to 40), `osha_certification`, `splicing_experience` |
| Pay | `updated_rate` (USD per hour), `rate_deduction` (USD, may be negative) |
| Status | `status_override`: Candidate Withdrew or Company Dropped (wins over every other status) |
| Onboarding profile | `profile`: `first_name`, `last_name`, `preferred_name` (as on ID), `address_street`, `address_city`, `address_state`, `address_postal_code`, `phone`, `date_of_birth` (`mm-dd-yyyy`), `gender`, `ssn_last4`, `work_authorization_detail`, `work_authorization_expires`, `phone_preference`, `laptop_preference`, `splicing_certification`, `fb_url` |

Not editable here: Offer Status, Start Date and Current Status. They come from the onboarding record and the interviews (see the onboarding workflows).

## Steps

1. **Resolve the candidate** to exactly one person and read them with `staffing_get_candidate` (add `include_profile=true` whenever the request is about profile fields, so the confirmation can show the current values).
2. **Map the request to fields.** Check choice fields against `staffing_list_options` (state, work authorization, level, OSHA, splicing). If the user's wording does not match an allowed value, show the allowed values and ask.
3. **Special cases:**
   - `other_emails` **replaces** the whole list. To add one address, send the existing list plus the new one; to remove one, send the list without it. Show the final list in the confirmation.
   - Changing the primary `email` fails when another candidate already uses it. Report that and do not retry with a different address on your own.
   - A name change: use the name parts when the user gives them, otherwise `name`. The name is recomputed from the parts.
   - `status_override` set to Candidate Withdrew or Company Dropped overrides the interview status. "The candidate gave up / left" is **Candidate Withdrew**; "we dropped the candidate / ended the cooperation / company drop" is **Company Dropped**. If the user only says "drop" or "stop working with" and it is not clear who ended it, ask. Confirm the effect on Current Status. Clear it with `null` only when asked.
   - Profile fields are changed like any other field, under `profile`; only the fields sent change. `ssn_last4` takes exactly 4 digits: a full 9-digit SSN is saved as its last 4 (say so), anything else is rejected. `date_of_birth` is `mm-dd-yyyy`. An address is saved as its four parts (`address_street`, `address_city`, `address_state` two-letter, `address_postal_code`); split what the user wrote and show the parts.
4. **Confirm** with `field: old → new` (profile fields too), then call `staffing_update_candidate` with `code` and `changes` (`version` plus only the changed fields). Send `null` only to clear a field the user asked to clear.
5. **Report** what was saved and the candidate's current status.

## Do not

- Do not send unknown fields; the tool rejects them.
- Do not bulk-edit several candidates from one confirmation; confirm each candidate separately.
- To remove a candidate created from wrong data, use `references/delete.md`, not an edit.
