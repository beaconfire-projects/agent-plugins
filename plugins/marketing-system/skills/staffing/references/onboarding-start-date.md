# Set, change or clear the start date

Tools: `staffing_search_candidates`, `staffing_list_onboardings`, `staffing_get_onboarding`, `staffing_update_onboarding`.

## Steps

1. **Find the onboarding record.**
   - Onboarding ID given: `staffing_get_onboarding`.
   - Name or Candidate ID given: resolve the candidate, then `staffing_list_onboardings` with `candidate_code`.
   - If both a candidate and an Onboarding ID are given, check they belong together; if not, say so and ask.
   - If the candidate has no onboarding record, offer to create one first (see `onboarding-create.md`); do not set a start date elsewhere.
2. **Work out the change.** `start_date` is the confirmed first day. `offer_date` can be corrected in the same call if the user asks.
   - Setting a start date moves the candidate to **Onboarding Scheduled**.
   - Clearing it (`null`) moves the candidate back to **Offered**. Only clear when the user asks for it explicitly.
   - Show the exact date. If the start date is before the offer date, point it out and ask before continuing.
3. **Confirm** with `field: old → new` and the resulting status, then call `staffing_update_onboarding` with `code` and `changes` (`version` plus only the changed fields).
4. **Report** the saved record and the candidate's status.

## Do not

- Do not edit `start_date` through the candidate; it is not an editable candidate field.
