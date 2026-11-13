# Create a person: approved HR Sheet structured rows only

There is no general-purpose create-person MCP tool. The supported creation path is `marketing_import_people(request={rows, dry_run})`, requiring Admin/Manager-style all-vendor scope. The MCP server cannot open the caller's local file path; its input is **structured rows**, not a file path, workbook/base64 or free-form person object. Ask the user for approved HR Sheet-shaped rows if not available; do not invoke another tool or script to manufacture them.

## Preconditions and source contract

Use the approved WeCom HR export's **HR Sheet** data and exact, case-sensitive column names. The workbook background uses instruction row 1, headers row 2, data row 3 onward; the MCP numbers supplied rows starting at 3. Do not include header/instruction rows as data. Every row requires a real nonblank `wecom_id`, plus legal first and last name after parsing. Never invent a WeCom identity to enable creation.

Key mappings (input keys are not person-update field names):

| HR Sheet input | Stored meaning |
| --- | --- |
| `wecom_id` | HR import identity; existing value skips whole row |
| `legal_first_name`, `legal_middle_name`, `legal_last_name` | Person names; `Name` is fallback (`Last, First Middle` or space-separated) |
| `preferred_name`, `Work Email`, `Phone#`, `Birth date`, `Sex`, `Notes` | Preferred name, normalized primary email, phone, birth date/raw text, gender, person/HR notes |
| `person_id` | HR sheet person identifier, **not** chosen database Person code |
| `Current Visa Status`, `Visa Start Date`, `Visa Expiration Date` | Current authorization; no authorization created without a type |
| `Internal / Batch`, `batch_start`, `batch_track`, `Batch Type` | Batch resolution inputs, not arbitrary new-batch creation |
| `Payroll Company`, `w2_start_date`, `Recruiter`, `Employment Status`, `Previous Status`, `Last Day ADP`, `Position` | HR payroll/employment data |
| `Visa Status Reach Out`, `HR Reporting List`, `HR System`, `Batch Summary`, `Drop Box` | HR flags |
| `POC`, `MKT POC`, `Leave Request Form`, `Status Notice Call`, `US TEAM POC`, `Risk for Terminate @V` | HR contacts and flags |

This table lists selected English-named source columns, not every accepted column. Preserve any additional source headers exactly as supplied, including non-English headers; translated labels are not accepted aliases.

Missing values generally become null. Dates parse formats including `YYYY-MM-DD` and `MM/DD/YYYY`; an unparseable date becomes null (birth date also retains raw text). Checkbox parsing accepts true/yes/y/1/checked and false/no/n/0/unchecked plus supported checkbox glyphs; unrecognized values become null. Prefer unambiguous ISO dates and actual booleans. Unknown columns are not a way to set arbitrary person fields; do not promise their import.

Batch mapping first uses the server's upstream reviewed WeCom mapping when available, otherwise local active-batch matching. A populated `Internal / Batch` with no matching batch is an error; even same-month fallback can choose a batch, so verify current batch after import. Do not “fix” failure by deleting meaningful source batch data without explicit user review.

## Preview → confirmation → import → readback

1. Optionally use `marketing_list_people(query)`/`marketing_get_person(code)` to resolve known identities before import. Never turn import into an update of an existing person.
2. Call `marketing_import_people(request={rows: [...], dry_run: true})`. Report each row's number/name, create/skip/error and safe message. Preview `created` is only the number **planned**, not persisted.
3. Explain: existing `wecom_id` skips the entire row; duplicate new WeCom IDs in this batch error; an email already owned or repeated in this batch skips. No merging/upserting existing values. Phone uniqueness may still fail at commit. Present exact rows and the partial-success behavior for explicit confirmation. If rows change, preview again before consent.
4. After a clear yes send the identical rows with `dry_run:false`. Valid rows commit independently; errors do not imply rollback of earlier rows. Report actual created/skipped/error counts and every returned `person_code`.
5. Read each created code using `marketing_get_person`. Verify identity, shared/HR values, authorization and current batch; imported records have source `wecom_hr_import`, `is_consultant=false`, `visible_to_team=true`, `is_internal=false`. This does **not** establish candidate eligibility or create submissions/offers. Read [candidate gap](create-candidate.md) if promotion is requested.

## Failure and recovery

Missing name/WeCom ID or duplicate IDs: correct genuine source data, re-preview and reconfirm. Existing-row skips are not failures requiring new IDs; use a separately confirmed [person update](person.md) if edits are wanted. Batch failures require authorized upstream/master-data correction. Unique email/phone conflicts require ownership review. Upstream lookup/service errors may prevent preview entirely.

On unknown outcome, inspect known returned codes and search identities; a failure may follow partial commits or sync wakeup. Re-preview the original rows to see which now skip, review any unresolved outcomes, then obtain consent before retrying only intended work. Never change `wecom_id` to bypass deduplication. Sheet projection is asynchronous; do not reimport to fix sheet lag. No generic delete/rollback is available.
