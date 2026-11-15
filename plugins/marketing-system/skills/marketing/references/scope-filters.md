# Scope options, filters and search (shared by every list tool)

**What you may see.** Admin and Manager see every Vendor, Client and Position; an AM sees only the Vendors they are assigned to. Positions without a Primary Vendor are visible to Admin / Manager only. Every list and read tool applies this scope on the server, so never try to widen it.

**Choices for filters.** Call `marketing_list_scope_options()` once: it returns the visible `positions` (code, title, vendor, client), `vendors` and `clients` (a client lists the `vendor_codes` it has positions under). Use these exact codes in filters. A code outside your scope returns an empty result, not an error.

If the connected client does not expose that tool, use `marketing_list_positions(q=...)` or `marketing_search_submission_positions(q=...)` to find the scoped position and retrieve its Vendor and Client codes. For a search that does not require a structured filter, pass the user's terms to `q` or `query`. `marketing_submission_options()` supplies statuses only.

**The three filters.** `vendor`, `client` and `position` are arrays of codes (`COM-…`, `COM-…`, `POS-…`); several values in one filter are OR, the three filters together are AND. They exist on `marketing_search_candidates`, `marketing_list_submissions`, `marketing_list_offers`, `marketing_list_interviews`, `marketing_list_slots`, `marketing_list_positions` and the interview overview. For a candidate they keep people who have, or ever had, a submission, interview or offer on those positions; for every other record they match the record's own position.

**Position is never injected.** Tools no longer accept a hidden "current position". Where a write targets one position (creating or holding slots) pass `position_code`; everywhere else `position` is only a filter. `current_status` (interview progress) needs a `position` filter, otherwise the call is rejected with `current_status needs a position`.

**Search (`q` / `query`).** Send the user's words as typed; do not split them yourself.
- Words are separated by spaces, every word must match somewhere in the record (code, name, title, Vendor, Client, email where the tool says so); order and case do not matter, so `hawkins andrew` finds Andrew S Hawkins.
- With several words a single letter (a middle initial) is ignored; a single-letter query on its own is still searched.
- With a search, results are ordered by relevance (exact code, then words that start a value, then the rest); without one, newest first.
