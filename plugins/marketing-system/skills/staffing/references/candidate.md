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
| Onboarding profile | `profile` (SSN last 4, date of birth, address, phone and so on; sensitive) |

Not editable here: Offer Status, Start Date and Current Status. They come from the onboarding record and the interviews (see the onboarding workflows).

## Steps

1. **Resolve the candidate** to exactly one person and read them with `staffing_get_candidate` (add `include_profile=true` only when the request is about profile fields).
2. **Map the request to fields.** Check choice fields against `staffing_list_options` (state, work authorization, level, OSHA, splicing). If the user's wording does not match an allowed value, show the allowed values and ask.
3. **Special cases:**
   - `other_emails` **replaces** the whole list. To add one address, send the existing list plus the new one; to remove one, send the list without it. Show the final list in the confirmation.
   - Changing the primary `email` fails when another candidate already uses it. Report that and do not retry with a different address on your own.
   - A name change: use the name parts when the user gives them, otherwise `name`. The name is recomputed from the parts.
   - `status_override` set to Candidate Withdrew or Company Dropped overrides the interview status. Confirm the effect on Current Status. Clear it with `null` only when asked.
   - Profile fields: only when the user explicitly asks. Do not repeat SSN, date of birth or address in your reply; say which fields were changed.
4. **Confirm** with `field: old → new` (for sensitive profile fields show only the field names and "changed"), then call `staffing_update_candidate` with `code` and `changes` (`version` plus only the changed fields). Send `null` only to clear a field the user asked to clear.
5. **Report** what was saved and the candidate's current status.

## Do not

- Do not send unknown fields; the tool rejects them.
- Do not bulk-edit several candidates from one confirmation; confirm each candidate separately.
