# Create an onboarding record (the candidate got an offer)

Tools: `staffing_search_candidates`, `staffing_get_candidate`, `staffing_list_onboardings`, `staffing_create_onboarding`.

## After an L2 pass

An interview write that sets L2 to Passed returns `onboarding_suggestion` (candidate ID, name and a suggested offer date: today in US Eastern time). Ask whether to create the record with that offer date (the user may give another date); on a yes skip to step 5 below with the suggested or given date. For several candidates, confirm them in one table and create one record per candidate.

## Find candidates who passed L2 without an onboarding record

`staffing_search_candidates` with `status` `L2 Passed` lists them (once a record exists the status becomes Offered). Show the list (ID, name, the L2 interview date from `staffing_get_candidate`) and ask which ones got an offer and on what date.

## Steps

1. **Resolve the candidate** (name or Candidate ID) to exactly one person.
2. **Check for an existing record**: `staffing_list_onboardings` with `candidate_code`. If one exists, do not create another. Show it (ID, offer date, start date, status) and offer to change its dates instead (see `onboarding-start-date.md`).
3. **Look at the interviews** from `staffing_get_candidate`. An offer normally follows a passed L2. If the candidate has no Passed L2, tell the user what the interviews show and ask whether to continue anyway; the record can still be created.
4. **Get the offer date.** It is required. If the user did not give one, ask (after an L2 pass, offer the suggested date); do not assume one silently. Show the exact date.
5. **Confirm**: "Create onboarding for `CAN-… Name`, offer date `YYYY-MM-DD`. The candidate becomes Offered."
6. Call `staffing_create_onboarding` with `candidate_code` and `offer_date`.
7. **Report** the new Onboarding ID (`ONB-…`) and the candidate's resulting status. A start date is not part of creation; if the user also gave one, do the start-date workflow next as a separate confirmed step.

## Do not

- Do not set Offer Status or Start Date on the candidate; they are computed from this record.
