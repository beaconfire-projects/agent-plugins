# Business codes

Every business record has a human-readable `code` (prefix + zero-padded sequence number). Tools take and return these codes, not internal database IDs. Recognize an entity by its prefix; never guess the entity from digits alone, never fabricate a code, and never pass an internal numeric `id` where a code is required. Digits wider than the minimum simply grow longer.

| Prefix / example | Entity | Notes |
| --- | --- | --- |
| `PER-010001` | Person (also a Candidate's code) | Lifelong code, 6 digits, unchanged before and after onboarding. A Candidate is a Person, so its Candidate ID is the `PER-` code. HR master people are `PER-000001`–`PER-004063`; Staffing candidates start at `PER-010000`. |
| `CAN-00001` | Legacy candidate code | Old Staffing format only; maps to `PER-(10000 + n)`. Not issued for new Marketing records; if a user gives one, resolve the Person through a search tool. |
| `COM-000123` | Company | One shared code for every company; Vendor / Client / PO flags are roles, not separate code classes. Differs from the internal ID. |
| `REL-000123` | Vendor–Client relationship | Links a Vendor, a Client and the responsible AM. |
| `POS-005000` | Position / JD | 6 digits, sequence starts at 5000. |
| `SUB-000123` | Submission | One candidate submitted to one position; a repeated candidate-position submission gets a new `SUB-` code. |
| `INT-0001` | Interview | 4 digits; belongs to exactly one submission. |
| `OFR-000123` | Formal Offer | 6 digits; one submission may have several offers, each with its own code. |
| `ONB-0001` | Onboarding code | 4 digits; carried on the Offer record. Informational here, not an independent Marketing entity. |
| `OFB-0001` | Offboarding code | 4 digits; assigned to the Offer when the person is confirmed as left. |
| `SLT-00001` | Interview Slot | Staffing scheduling; outside this skill's workflows. |
| `FUP-00001` | Interview follow-up action | System queue (calendar invite, reminder email, question-document copy); read-only context, never a user-addressable target. |

## Rules

- A code is an exact identifier: copy it from a tool result verbatim (case and dashes included). A person's name, email or a company's display name is a search term, not a code.
- A prefix tells you which tool family and argument slot applies (e.g. `SUB-` goes to submission arguments, never to a `person_code` field). If a user supplies a code whose prefix does not match the requested slot, say so and resolve the right record instead of forcing it.
- A company's role flags never change its `COM-` code.
- This workflow never reuses or renumbers a code; the same code on a later read confirms you hold the same record.
