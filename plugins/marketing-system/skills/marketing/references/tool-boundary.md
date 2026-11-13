# Verified tool boundary

The combined capability contract lists **49 tools** (companies 6, positions/vendors 7, submissions 11, offers 11, people 7, interviews 7). This change verifies the 14 Person/Interview decorators against the current development checkout. The other 35 entries retain the previously reviewed marketing skill contract; their implementations are not in this development checkout and must not be described as newly reverified. Allow only tools whose actual decorator tags include `marketing`. The connected deployment must expose the matching schema; stop on missing tools, unverified tags or incompatible schemas. This list does not authorize future tools solely because their names look similar.

Source paths below are code provenance under `backend/app/`, not runtime calls or relative file links.

## Companies (6)

Existing marketing contract (retained): tags `marketing`, `companies`. Verify the connected deployment before use.

- `marketing_check_company`
- `marketing_company_capabilities`
- `marketing_create_company`
- `marketing_get_company`
- `marketing_list_companies`
- `marketing_update_company`

## Submissions (11)

Existing marketing contract (retained): tags `marketing`, `submissions`. Verify the connected deployment before use.

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

Existing marketing contract (retained): tags `marketing`, `offers`. Verify the connected deployment before use.

- `marketing_create_offer`
- `marketing_get_offer`
- `marketing_get_offer_history`
- `marketing_list_offers`
- `marketing_offboard_offer`
- `marketing_offer_options`
- `marketing_onboard_offer`
- `marketing_preview_offer_submission`
- `marketing_search_offer_po_vendors`
- `marketing_search_offer_submissions`
- `marketing_update_offer`

## People (7)

Source: `modules/staffing/mcp/tools.py`. Tags: `marketing`, `people`.

- `marketing_create_person`
- `marketing_get_person_options`
- `marketing_get_person_history`
- `marketing_get_person`
- `marketing_import_people`
- `marketing_list_people`
- `marketing_update_person`

## Interviews (7)

Source: `modules/staffing/mcp/tools.py`. Tags contain `marketing`, `interviews`; existing shared list/get/create/update also retain `staffing` for compatibility.

- `marketing_search_interview_submissions`
- `marketing_get_interview_submission`
- `marketing_list_interviews`
- `marketing_get_interview`
- `marketing_get_interview_history`
- `marketing_create_interview`
- `marketing_update_interview`

Use the submission selector/context for per-position choices. No staffing `marketing_list_options` fallback is needed. A shared tool's tags do not import staffing's workflow/automatic ONB rules into marketing.

## Positions and Vendor selection (7)

Existing marketing contract (retained). Position tags: `marketing`, `positions`; Vendor list tags: `marketing`, `vendors`.

- `marketing_list_vendors`
- `marketing_list_position_clients`
- `marketing_list_positions`
- `marketing_get_position`
- `marketing_create_position`
- `marketing_update_position`
- `marketing_parse_position_jd`

These names previously belonged to Staffing; require the deployed Marketing tags before using them. Vendor queries now have independent Marketing service/repository ownership.

## Explicit exclusions

Staffing options, candidate create/update/search, Slot, legacy ONB/offboarding, old submission, generic history, ingest, delete and staffing-only position-management tools do not qualify merely because their names begin `marketing_`. Insights/statistics are outside this boundary. Do not load staffing or call REST/SQL/scripts to bypass a missing marketing capability. Person and Interview tools listed above qualify because their decorators explicitly include `marketing`, despite their source module name.

There is no candidate-conversion, interview delete, offer cancel/undo or batch-create tool in this inventory. Independent formal OFR actions and legacy ONB actions are distinct. See [Interview](interview.md), [Person](person.md), and [Offer](offer.md) for each workflow's explicit confirmation and field requirements.
