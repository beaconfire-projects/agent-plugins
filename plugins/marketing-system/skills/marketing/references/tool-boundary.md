# Verified tool boundary

This inventory was checked against current backend MCP decorators, not prefixes or directory names: **39 tools** (companies 6, positions/vendors 7, submissions 11, offers 11, people 4). Allow only tools whose actual decorator tags include `marketing`. The connected deployment must expose the matching schema; stop on missing tools, unverified tags or incompatible schemas. This list does not authorize future tools solely because their names look similar.

Source paths below are code provenance under `backend/app/`, not runtime calls or relative file links.

## Companies (6)

Source: `modules/marketing/mcp/tools.py`. Tags: `marketing`, `companies`.

- `marketing_check_company`
- `marketing_company_capabilities`
- `marketing_create_company`
- `marketing_get_company`
- `marketing_list_companies`
- `marketing_update_company`

## Submissions (11)

Source: `modules/marketing/mcp/submissions.py`. Tags: `marketing`, `submissions`.

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

Source: `modules/marketing/mcp/offers.py`. Tags: `marketing`, `offers`.

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

## People (4)

Source: `modules/staffing/mcp/tools.py`. Tags: `marketing`, `people`.

- `marketing_get_person`
- `marketing_import_people`
- `marketing_list_people`
- `marketing_update_person`

## Positions and Vendor selection (7)

Source: `modules/marketing/mcp/position_tools.py`. Position tags: `marketing`, `positions`; Vendor list tags: `marketing`, `vendors`.

- `marketing_list_vendors`
- `marketing_list_position_clients`
- `marketing_list_positions`
- `marketing_get_position`
- `marketing_create_position`
- `marketing_update_position`
- `marketing_parse_position_jd`

These names previously belonged to Staffing; require the deployed Marketing tags before using them. Vendor queries now have independent Marketing service/repository ownership.

## Explicit exclusions

The staffing options, candidate create/update/search, interview/slot, staffing onboarding/offboarding, old submission, history and ingest tools do not qualify merely because they have a marketing-prefixed name. Insights/statistics tools are also outside this boundary. Never use them as callable steps or load the staffing skill to bypass a missing marketing capability. The four people tools above are allowed despite living in the staffing module, because their decorators explicitly carry the marketing tag.

Read-only interview context is available only through the allowed exact workspace-submission detail or offer-submission preview. No generic person creation tool, candidate conversion tool, interview write tool, offer cancel/undo tool or batch-management tool is present in this inventory.
