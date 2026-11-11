# Create and update a submission

Tools: `marketing_get_candidate_detail`, `marketing_get_submission`, `marketing_submit_candidate_to_position`, `marketing_update_submission`.

A **submission** is a candidate on one position of one vendor (`SUB-nnnnnn`). It holds what the recruiter's Submission email said about that submission: the pay rate, when the candidate can start, relocation and travel, when the candidate can interview, earlier work with the same client, and the C2C employer with its contact. These belong to the submission, not to the person, and differ from position to position. LinkedIn, Facebook, phone and laptop preference are the **person's**: change them with `marketing_update_person` (see `references/candidate.md`).

## Fields

| Field | Meaning |
| --- | --- |
| `submitted_rate` | Hourly rate in USD, 0 to 500 |
| `rate_type` | `W2`, `C2C` or `1099` |
| `start_availability` | When the candidate can start, as written (for example `Immediately`, `2 Weeks`) |
| `open_to_relocate`, `travel_availability` | As written (for example `Yes`, `He is local`) |
| `interview_availability` | The time slots the candidate can interview, as written |
| `same_client_history` | Earlier work with the same client, project and manager, as written |
| `employer_name`, `employer_contact_name`, `employer_contact_email`, `employer_contact_phone` | The C2C employer written in this submission and its contact |

The C2C employer here belongs to this submission only. It does not change the candidate's own employer (`marketing_update_person`), and the two do not sync. Level, lead and status are not changed here (`marketing_update_candidate`).

## Read a submission

Find the submission code in `marketing_get_candidate_detail` (`submissions`), or take a `SUB-…` code from the user, then call `marketing_get_submission`. It returns the vendor, client and position, level, status, the details above, which of them were edited by hand (`manual_fields`), the submission's interviews and offers, and the `version` an update needs. A submission on another vendor's position is `Not found`.

## Create a submission

Submitting a candidate to a position is `marketing_submit_candidate_to_position` with the candidate's code and `submit.position` (a `POS-…` of your own vendor; the candidate may be yours or anyone `In Preparation` / `In Marketing`). A candidate can be submitted to a position once.

1. **Resolve the candidate and the position** to exactly one each; never pick for the user.
2. **Level** is optional and must be one of the Levels that position uses; a position without Levels only takes an empty value.
3. **Details are optional and can be given in the same call**: `submitted_rate` with `rate_type`, `start_availability`, `open_to_relocate`, `travel_availability`, `interview_availability`, `same_client_history`, the employer fields. Send only what the user gave (for example "$38/hr C2C, can start immediately" is `submitted_rate: 38`, `rate_type: C2C`, `start_availability: Immediately`).
4. **Confirm** the candidate, the position and the fields in a short table, then call the tool once.
5. **Report** the new `SUB-…` code and the saved values.

## Change a submission

1. **Read** it with `marketing_get_submission` (current values and `version`).
2. **Send only the fields that change**, with `changes.version`. `null` or empty text clears a field. Fields changed here are kept when a later Submission email says something else, so tell the user when you overwrite something that came from an email.
3. **Confirm** with `field: old → new`, then call `marketing_update_submission` with `code` and `changes`.
4. **Report** what was saved from the response. The change history shows the employer contact's email and phone as `changed`, without values.

If the update is rejected as stale (`was changed by someone else`), read again, tell the user what changed, and ask again before retrying.

## Do not

- Do not put the submission's pay rate or availability on the candidate, and do not put the person's LinkedIn or Facebook on a submission.
- Do not change the level, lead flag or Status Override here; they are changed with `marketing_update_candidate`.
- Do not update several submissions from one confirmation.
