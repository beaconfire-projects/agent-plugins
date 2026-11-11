# Statistics: counts, distributions and trends (read only)

Tools: `insights_list_metrics`, `insights_query`. To find the **people** behind a number use `marketing_search_candidates`, `marketing_list_interviews` or `marketing_list_onboardings`; to read one record use the lookup workflows.

**Scope.** The numbers only include the vendors you can see: an AM sees the vendors they are responsible for, a manager or admin sees all of them. If a number looks too small or an expected row is missing, say that the figures are limited to the user's vendors instead of treating it as a data problem. If the tools answer that statistics are not available, the user has no vendor assigned yet: they should ask an admin.

Use this workflow for "how many", "what share", "by level / visa / status / round", "per week / per month" and "compare". The numbers are computed by the metrics service (Cube), the single place where the counting rules live, and they match what the Staffing Dashboard shows. **Never count by paging through candidates or interviews yourself**: it is slow, it can miss rows, and it can drift from the Dashboard.

## Steps

1. **Load the vocabulary once per conversation.** Call `insights_list_metrics`. It returns the metrics (numbers you can ask for) and dimensions (ways to group or filter), each with its meaning. Use the names exactly as returned (for example `pipeline.candidates`, `pipeline.current_status`); never invent a name. If the user's question needs a number or a grouping that is not in the list, say so plainly and offer the closest one, or the people-level tools if a list of names would answer it.
2. **Turn the question into one query.**
   - `measures`: the numbers (one or several in the same query, as long as they come from the same group, i.e. all `pipeline.*`, all `interviews.*` or all `onboardings.*`).
   - `dimensions`: group by these (for example `pipeline.level`, `pipeline.work_authorization`, `interviews.round`).
   - `filters`: `{member, operator, values}`; values are text, dates are `YYYY-MM-DD`.
   - `time_dimensions`: trends or date ranges on a **time** dimension (`onboardings.offer_date`, `onboardings.start_date`, `pipeline.submitted_at`, `submissions.submitted_at`, `submissions.offer_date`) with `granularity` (day, week, month, quarter, year) and `date_range` `[start, end]` (both included).
   - `order` and `limit` (default 50, at most 200). If the result says `truncated: true`, say that more rows exist and narrow the query (add a filter, a smaller `limit` with `order`) instead of presenting a partial list as complete.
3. **Run `insights_query`.** Several independent questions can be separate calls in the same turn. Do not ask the user to confirm: it is read only.
4. **Answer in plain words first, then a small table.** State the number or the finding in one sentence, then a table with the rows. Say the date range, filters and the date you ran it ("as of today"). Compute shares, rates and differences yourself from the returned counts and show the numerator and denominator (for example "L2 pass rate 89 / 96 = 93%").
5. **Offer the next cut**, but do not run more queries than the question needs.

## Which metric to use (the traps)

| The user means | Use | Not |
| --- | --- | --- |
| People per Current Status ("how many are in each status") | `pipeline.candidates` grouped by `pipeline.current_status` | adding up several metrics by hand |
| First-time waiting for L1 (no interview yet) | `pipeline.l1_pending_schedule` (same people as the Dashboard's L1 to be scheduled column) | `pipeline.waiting_l1`, which also counts reschedules and no-shows |
| Waiting for L2 after passing L1 | `pipeline.l1_passed_pending_l2` | `pipeline.waiting_l2`, which also counts L2 reschedules and no-shows |
| Need a new slot after a reschedule or no-show | `pipeline.l1_reschedule`, `pipeline.l2_reschedule` | |
| Holding a slot, invite not received yet | `pipeline.l1_slot_held`, `pipeline.l2_slot_held` (not counted as waiting) | |
| "Everyone still waiting to be scheduled" | `pipeline.l1_pending_schedule` + `pipeline.l1_reschedule` (L1), `pipeline.l1_passed_pending_l2` + `pipeline.l2_reschedule` (L2); say which parts you added | |
| Offers | `onboardings.offers` (not canceled); `onboardings.offers_incl_canceled` only when asked to include cancellations | |
| Candidates with an offer now | `pipeline.offered` | `onboardings.offers` (that counts records, not candidates' current status) |
| Interviews on a day or in a period | `interviews.*` with a filter on `interviews.interview_day` (text `YYYY-MM-DD`; use `equals`, or `gte` and `lte` for a range) | `time_dimensions` (this dimension is text, not a time type) |
| Pass rate of a round | `interviews.passed`, `interviews.failed` by `interviews.round`; rate = passed / (passed + failed) | dividing by `interviews.total` (it includes scheduled, canceled and no-show) |

### Vendor and Client questions (positions, submissions, candidates, offers)

Only if `insights_list_metrics` shows `positions.*` and `submissions.*`; these are limited to Admin users, so for anyone else they are simply not in the list: say it is not available to them and do not try to work it out another way.

| The user asks | Use |
| --- | --- |
| How many positions does a Vendor or Client have | `positions.count`, filter on `positions.vendor_name` / `positions.client_name`, or group by them |
| How many submissions, candidates or offers for a Vendor or Client | `submissions.submissions`, `submissions.candidates` (distinct people), `submissions.offers`, with a filter on `submissions.vendor_name` / `submissions.client_name` |
| Which stages are candidates in, for a Vendor or Client | `submissions.submissions` grouped by `pipeline.current_status`, with the Vendor / Client filter |
| Submissions in a period | `submissions.submitted_at` as the `time_dimensions` entry (with `date_range`, and `granularity` for a trend). Offers in a period: `submissions.offer_date` |

- **Vendor means the Primary Vendor of the position** (the billing vendor is not included). Filter by `vendor_name` or `vendor_code`, not by the internal `vendor_id`. Company codes are temporary for now (for example `TMP-TENARAI`, `TMP-META`) and will change when the official data is imported, so never type a code from memory or guess one: take it from a query result. A filter value that matches nothing returns 0, not an error, so a wrong name looks like "no data". If the name is not exact, first query `submissions.submissions` (or `positions.count`) grouped by `vendor_name` to list the names, then use the exact one; if several look alike, ask the user which.
- Positions have no date dimension; do not try to count positions by period.
- Do not mix `positions.*` and `submissions.*` in one query (they are not joined). To combine them, run two queries.
- Today there is one position (Tenarai / Meta); other Vendors and Clients appear as their data is imported, so say when a Vendor or Client returns nothing instead of reporting zero as a fact.
- `submissions.submitted_at` for older candidates may be the time the record was created in the system, not the real submission time; mention it when a period answer looks lopsided.

Things to say when they matter:
- `interviews.total` includes canceled interviews (`interviews.canceled` is already inside it). "Held" interviews are passed + failed + no-show + need-to-reschedule + awaiting result.
- `pipeline.candidates` counts submissions, one per candidate today.
- Level, work authorization and years of experience come from the candidate's current data; a blank value shows as an empty group: call it "Unknown" rather than dropping it.
- The statistics service can be unavailable (the tool returns a "not available" error). Say so and stop; do not substitute your own count from the other tools, because that would give a number that may not match the Dashboard.

## What this cannot do

- No names, emails, phone numbers, rates or other personal details: counts only. For "who are they", switch to `marketing_search_candidates` (filter by `status`, `level` and so on) or `marketing_list_interviews`, and keep the list as short as the question needs.
- No writes. To change a status or record, use the other workflows.
- Only Staffing and Marketing (positions, submissions) data is available; if `insights_list_metrics` shows no metric for what was asked (for example revenue, rates, or another business), say that it is not covered.

## Example

"How many candidates are in each status, and how has the number of offers changed by month this half year?"

1. `insights_query` with `measures: ["pipeline.candidates"]`, `dimensions: ["pipeline.current_status"]`, `order: {"pipeline.candidates": "desc"}`.
2. `insights_query` with `measures: ["onboardings.offers"]`, `time_dimensions: [{"dimension": "onboardings.offer_date", "granularity": "month", "date_range": ["2026-05-08", "<today>"]}]`.
3. Reply with the two small tables and one sentence on what stands out (for example the largest group and whether offers are rising); months with no offers do not appear in the result, so say "none" for them.
