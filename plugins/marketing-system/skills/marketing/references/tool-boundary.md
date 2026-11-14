# Verified tool boundary

The combined capability contract lists **55 tools** (companies 6, candidates 4, positions/vendors 7, submissions 11, offers 11, people 8, interviews 8). The 52 entries that existed before the candidate change were individually rechecked against their actual decorators in the local backend checkout for this documentation change. This is source-contract verification, not a claim that the connected deployment has these tools. The four candidate tools were checked against the deployed backend (image 0.1.0-169): their tags include `marketing`; local declarations alone do not establish deployed availability. Allow only tools whose actual decorator tags include `marketing`. The connected deployment must expose the matching schema; stop on missing tools, unverified tags or incompatible schemas. This list does not authorize future tools solely because their names look similar.

Source paths below are code provenance under `backend/app/`, not runtime calls or relative file links.

## Companies (6)

Source: `modules/marketing/mcp/tools.py`. Each listed decorator has tags `marketing`, `companies`.

- `marketing_check_company`
- `marketing_company_capabilities`
- `marketing_create_company`
- `marketing_get_company`
- `marketing_list_companies`
- `marketing_update_company`

## Candidates (4)

Source: `modules/staffing/mcp/tools.py`. Actual decorator tags: `staffing`, `marketing`, `candidates` (the `staffing` tag is kept for compatibility, like the shared interview tools).

- `marketing_add_candidate`
- `marketing_search_candidates`
- `marketing_search_addable_people`
- `marketing_get_candidate_detail`

`marketing_add_candidate(candidate={...})` takes new-intake fields, or only `person_code` for existing-Person Bench conversion. The other three find and read back candidates; see [Create candidate](create-candidate.md). The candidate update, responsible-AM assignment, note and history tools carry the same tags but have no workflow in this skill, so they are not authorized here.

## Submissions (11)

Source: `modules/marketing/mcp/submissions.py`. Each listed decorator has tags `marketing`, `submissions`.

- `marketing_check_submission`
- `marketing_create_submission`
- `marketing_get_workspace_submission`
- `marketing_list_submissions`
- `marketing_mark_submission_offered`
- `marketing_reject_submission`
- `marketing_search_submission_candidates`
- `marketing_search_submission_employers`
- `marketing_search_submission_positions`
- `marketing_submission_options`
- `marketing_update_workspace_submission`

## Offers (11)

Source: `modules/marketing/mcp/offers.py`. Each listed decorator has tags `marketing`, `offers`.

- `marketing_create_offer`
- `marketing_get_offer`
- `marketing_get_offer_history`
- `marketing_list_offers`
- `marketing_offer_options`
- `marketing_preview_offer_submission`
- `marketing_search_offer_po_vendors`
- `marketing_search_offer_submissions`
- `marketing_undo_cancel_offer`
- `marketing_update_offer`
- `marketing_cancel_offer`

## People (8)

Source: `modules/staffing/mcp/tools.py`. Tags: `marketing`, `people`.

- `marketing_create_person`
- `marketing_delete_person`
- `marketing_get_person_options`
- `marketing_get_person_history`
- `marketing_get_person`
- `marketing_import_people`
- `marketing_list_people`
- `marketing_update_person`

`marketing_get_person_history` reads Staffing-module audit records only; it cannot verify the Marketing-module candidate create/conversion or creator-assignment audit. See [Create candidate](create-candidate.md) for the resulting unknown-outcome limits.

## Interviews (8)

Source: `modules/staffing/mcp/tools.py`. Tags contain `marketing`, `interviews`; existing shared list/get/create/update/delete also retain `staffing` for compatibility.

- `marketing_search_interview_submissions`
- `marketing_get_interview_submission`
- `marketing_list_interviews`
- `marketing_get_interview`
- `marketing_get_interview_history`
- `marketing_create_interview`
- `marketing_delete_interview`
- `marketing_update_interview`

Use the submission selector/context for per-position choices. No staffing `marketing_list_options` fallback is needed. A shared tool's tags do not import staffing's workflow/automatic ONB rules into marketing.

## Positions and Vendor selection (7)

Source: `modules/marketing/mcp/position_tools.py`; each listed decorator checked. Position tags: `marketing`, `positions`; Vendor list tags: `marketing`, `vendors`.

- `marketing_list_vendors`
- `marketing_list_position_clients`
- `marketing_list_positions`
- `marketing_get_position`
- `marketing_create_position`
- `marketing_update_position`
- `marketing_parse_position_jd`

These names previously belonged to Staffing; require the deployed Marketing tags before using them. Vendor queries now have independent Marketing service/repository ownership.

## Explicit exclusions

Staffing options, candidate update / responsible-AM / note / history tools (not part of any workflow in this skill), Slot, legacy ONB/offboarding, old submission, generic history, ingest, other delete and staffing-only position-management tools do not qualify merely because their names begin `marketing_`. Insights/statistics are outside this boundary. Do not load staffing or call REST/SQL/scripts to bypass a missing marketing capability. Person and Interview tools listed above qualify because their decorators explicitly include `marketing`, despite their source module name.

Only single Person/Interview deletion is included. There is no bulk delete, candidate deletion, offer deletion or batch-create tool in this inventory. Dependency orchestration uses multiple existing calls, not a new nested/batch-create tool; see [Create orchestration](create-orchestration.md). The legacy staffing onboarding / offboarding tools were removed; formal OFR offers use the tools above. See [Interview](interview.md), [Person](person.md), and [Offer](offer.md) for each workflow's explicit confirmation and field requirements.
