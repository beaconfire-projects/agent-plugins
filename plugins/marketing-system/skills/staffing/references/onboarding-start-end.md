# Confirm the start, offboarding and the end

Tools: `staffing_search_candidates`, `staffing_get_onboarding`, `staffing_list_onboardings`, `staffing_confirm_onboarding_start`, `staffing_create_offboarding`, `staffing_update_offboarding`, `staffing_cancel_offboarding`, `staffing_confirm_offboarding`.

An offer moves through these stages, and **only these actions change its status** (never edit the status directly):

| Status | How it gets there |
|---|---|
| Offered | the onboarding record exists (no start date yet) |
| Onboarding Scheduled | the planned start date is set (`staffing_update_onboarding`, see `onboarding-start-date.md`) |
| **Active** | `staffing_confirm_onboarding_start`: the business confirms the first day the person actually worked |
| still Active, with an offboarding | `staffing_create_offboarding`: the person is leaving; nothing is final yet |
| **Remap / Quit / Fired** | `staffing_confirm_offboarding`: the business confirms the person actually left; the status is the outcome |

Remap means the person is not leaving the company: they go back into marketing and will get new submissions and interviews later.

## Steps

1. **Find the onboarding record** (`staffing_get_onboarding`, or resolve the candidate and use `staffing_list_onboardings`). Read its `version`, `status`, `actual_start_date` and `offboarding_*` fields.
   - Canceled (`canceled_at` set) or already ended (`offboarding_last_day` set): it cannot be changed. For a canceled offer offer to undo the cancellation first (`onboarding-cancel.md`); for an ended one, a new offer for the same position is created with `staffing_create_onboarding` (the old record stays as history).
2. **Pick the action** and check the rule:
   - **Confirm start**: needs the exact first day (`actual_start_date`). Confirming the same day again changes nothing; a different day is a correction. A started offer can no longer be canceled: use an offboarding to end it.
   - **Create offboarding**: only for an Active record. Every field is optional (`planned_last_day`, `current_status` = `Remap` / `Quit` / `Fired`, `reason`, `next_step`, `notes`); blank fields stay blank.
   - **Update offboarding**: only non-blank values are merged; an omitted or blank field keeps the saved value. To start over, cancel the offboarding.
   - **Cancel offboarding**: the person is staying; the whole offboarding section is cleared and the status is Active again. Confirm with the user first.
   - **Confirm the end**: needs the actual last day (not before the actual start date) and the outcome. The submission is closed and the record can no longer be changed. Confirm the day and outcome with the user first.
3. **Use only the form's values.** `reason`: Vendor FT Conversion, Client FT Conversion, Project ended, Visa issue, Released by client: Performance issue, Released by client: Budget issue, Other. `next_step`: Back to Marketing, FT, MIA, Return to Training, Other. Anything else is rejected.
4. **Confirm** with `field: old → new` and the resulting status, then call the tool with `code` and the body (`version` plus the fields).
5. **Report** the saved record: status, OFB- ID if there is one, and the dates.

## Do not

- Do not confirm a start or an end from a planned date; ask for the confirmed one.
- Do not use cancel-offer for someone who already started.
