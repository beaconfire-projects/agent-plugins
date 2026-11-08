# Update candidate information

Tools: `staffing_search_candidates`, `staffing_get_candidate`, `staffing_list_options`, `staffing_update_candidate`.

## Editable fields

| Group | Fields |
| --- | --- |
| Name | `first_name`, `middle_name`, `last_name` (the legal name as on the ID) and `preferred_name` (the name the candidate goes by, written as a full name). There is no `name` field on update: the full name is always First Middle Last and is built from the three parts |
| Contact | `email` (primary, unique), `other_emails` (list, each unique across all candidates) |
| Location | `city`, `state` (two-letter code) |
| Profile of the person | `work_authorization`, `level`, `yoe` (0 to 40), `osha_certification`, `splicing_experience` |
| Pay | `updated_rate` (USD per hour), `rate_deduction` (USD, may be negative) |
| Status | `status_override`: Candidate Withdrew or Company Dropped (wins over every other status) |
| Marketing status | `marketing_status`: `In Preparation` (the default for a new candidate) or `In Marketing`. Candidates in these two are the marketing pool (meant to be shared by every AM; showing pool candidates of another vendor is not available yet). `On Project` (has an open offer) and `Off Project` (left the project: Quit or Fired) follow the offer by themselves and are refused if you send them |
| Onboarding profile | `profile`: `address_street`, `address_city`, `address_state`, `address_postal_code`, `phone`, `date_of_birth` (`mm-dd-yyyy`), `gender`, `ssn_last4`, `work_authorization_detail`, `work_authorization_expires`, `phone_preference`, `laptop_preference`, `splicing_certification`, `fb_url` |

Not editable here: Offer Status, Start Date and Current Status (and the marketing status once it is On Project or Off Project). They come from the onboarding record and the interviews (see the onboarding workflows).

## Steps

1. **Resolve the candidate** to exactly one person and read them with `staffing_get_candidate` (add `include_profile=true` whenever the request is about profile fields, so the confirmation can show the current values).
2. **Map the request to fields.** Check choice fields against `staffing_list_options` (state, work authorization, level, OSHA, splicing). If the user's wording does not match an allowed value, show the allowed values and ask.
3. **Special cases:**
   - `other_emails` **replaces** the whole list. To add one address, send the existing list plus the new one; to remove one, send the list without it. Show the final list in the confirmation.
   - Changing the primary `email` fails when another candidate already uses it. Report that and do not retry with a different address on your own.
   - A name change: change the name parts (`first_name`, `middle_name`, `last_name`, `preferred_name`); `staffing_update_candidate` has no `name` field and the full name is rebuilt from the parts. When the user gives only a full name, split it yourself (first word = First, last word = Last, words in between = Middle; a suffix such as Jr. stays in Last) and show the split in the confirmation. A part you do not send keeps its value, so send `middle_name: null` when the new name has no middle name. Names are not part of `profile`: sending `profile.first_name`, `profile.last_name` or `profile.preferred_name` is rejected.
   - `marketing_status`: an AM moves a candidate from `In Preparation` to `In Marketing` when the candidate is ready to be submitted. Creating an offer makes the candidate `On Project`; a canceled or withdrawn offer, or a Remap, puts them back in `In Marketing`; Quit or Fired makes them `Off Project`. Do not try to set those by hand: the tool answers that the status follows the offer.
   - `status_override` set to Candidate Withdrew or Company Dropped overrides the interview status. "The candidate gave up / left" is **Candidate Withdrew**; "we dropped the candidate / ended the cooperation / company drop" is **Company Dropped**. If the user only says "drop" or "stop working with" and it is not clear who ended it, ask. Confirm the effect on Current Status. Clear it with `null` only when asked. While the candidate's offer is canceled (the onboarding record has `canceled_at`), the override and its reason are refused: undo the cancellation first (see `onboarding-cancel.md`).
   - Profile fields are changed like any other field, under `profile`; only the fields sent change. `ssn_last4` takes exactly 4 digits: a full 9-digit SSN is saved as its last 4 (say so), anything else is rejected. `date_of_birth` is `mm-dd-yyyy`. An address is saved as its four parts (`address_street`, `address_city`, `address_state` two-letter, `address_postal_code`); split what the user wrote and show the parts.
4. **Confirm** with `field: old → new` (profile fields too; for a name show First / Middle / Last), then call `staffing_update_candidate` with `code` and `changes` (`version` plus only the changed fields). Send `null` only to clear a field the user asked to clear.
5. **Report** what was saved and the candidate's current status.

## Do not

- Do not send unknown fields; the tool rejects them.
- Do not bulk-edit several candidates from one confirmation; confirm each candidate separately.
- To remove a candidate created from wrong data, use `references/delete.md`, not an edit.
