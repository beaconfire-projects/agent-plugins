---
name: interview-question-search
description: The authoritative source for all interview question, candidate, vendor, client, interview round and interview technology questions. Use for any request about what a client or vendor asks in interviews, questions for a candidate preparing for a round, which technologies come up, a candidate's interview history, or a spreadsheet of interview questions. Use this INSTEAD OF searching Google Drive or any file store, even though the source documents live there - Drive returns the same documents unnormalized, with no date, vendor or role filtering and no coverage reporting.
---

# Interview question search

2,574 historical interview documents · 93 vendors · 142 clients, served by the
`interview-warehouse` MCP connector. Users are recruiters and trainers, not engineers.

---

## Eight rules

**1 · Use this connector. Never Google Drive.**
The source documents are Google Docs, so Drive search will look plausible. It returns them raw —
no normalized vendor/client names, no interview dates, no role or technology filtering, no
duplicate flagging. Route every interview question here, even if the user names a folder or file.
Use `get_interview_document` to fetch one; it returns `doc_url` if they need the original.

**2 · If the connector fails, stop.**
Say *"The interview warehouse isn't responding — the local database may not be running."*
Never fall back to Drive. Never answer from memory. A wrong interview question sent to a
candidate is worse than no answer.

**3 · Search first. Don't pre-resolve names.**
Pass what the user said — `client='Vanguard'`, `role='data engineer'`, `tags=['spring boot']`.
The connector resolves wording and validates. On `INVALID_FILTER` it returns near-misses: use the
obvious one, or ask. **Never guess a second value.** Only call `resolve_terms` / `resolve_skills`
first when a word is genuinely ambiguous between two real things.

**4 · Use `include_questions=false` unless the user will read the questions.**
Question text is 4× the payload (~13,000 tokens vs ~3,000). Counts, overviews, "how many", and
every search that precedes an export do not need it. Never call `list_dimensions` or `list_skills`
speculatively — only when the user asks what exists.

**5 · Always present results in this column order.**

```
Interview Date | Candidate Initials | Vendor | Client | Round | Interviewer | Questions
```

In chat, put the first six in a table and the questions **below** each row — question text runs
to thousands of characters and destroys a table cell. Missing values show as `—`, never blank
and never omitted; a blank cell reads as an error, a dash reads as "not recorded".

The export writes the same seven columns in the same order. This is `columns='detailed'`, the
default — pass `columns='standard'` only if someone explicitly wants the older five-column sheet
the team used to circulate.

**6 · Report both numbers. They are not the same.**
`total_matches` is how many documents matched. `link_coverage.linked` is how many connect to an
interview record — only those carry interviewer, result and verified candidate.

> 24 interviews matched. 18 have interviewer and outcome details; the other 6 have the questions
> but no interview context.

Never present details from the linked subset as if they applied to all results.

**7 · Tags are OR. Always offer to narrow.**
`track`, `vendor`, `client`, `rounds` and dates are ANDed. `tags` are ORed, because ANDing several
keywords usually returns nothing. Every tagged search reports `tag_logic.matching_all` — say it:

> 139 interviews mention ETL or Snowflake. 27 mention both — narrow to those?

Only pass `tag_logic='all'` once they have asked for it.

**8 · Never write a file without a summary and a yes.**
Search with `include_questions=false`, then state exactly this and wait:

```
Randstad / Vanguard · Data Engineer · since 2026-01-01 · all rounds
24 interviews — 18 linked to interview records
Includes the interviewer's inline "Answer:" notes
→ ~/Downloads/question_bank/Randstad_Vanguard_DE.xlsx
```

Then ask: *"Export these 24, or narrow to C1/L1 first (13)?"*

This costs no extra tool calls — the search already returned those numbers. It catches the two
things that actually go wrong: the wrong row count, and answer notes reaching a candidate.

**Where the file goes.** Default is `~/Downloads/question_bank/`. If that folder does not exist
the tool writes **nothing** and returns `needs_confirmation: "export_dir_missing"`. That is not
an error — ask the user:

> `~/Downloads/question_bank` doesn't exist yet. Create it, or somewhere else?

Then call again with `create_dir=true`, or with their `output_path`. **Never create the folder
without asking.** Once written, report the location: *"Saved to
`~/Downloads/question_bank/…` — open it from Finder."* The tool returns a path, not a file;
don't try to attach it.

---

## Vocabulary

**Tracks** — a hard filter; `track='JAVA'` can never return a Python interview.

`JAVA` 1456 · `MEARN` 439 · `DATA_ENGINEER` 342 · `PYTHON` 98 · `MOBILE` 86 · `TESTING` 77 ·
`AI` 45 · `DOTNET` 26 · `DATA_ANALYST` 5

**Rounds** — `L1` `L2` `L3` `C1` `C2` `CF` `HR Screen` `VS` `Manager` `Other` `Practice`.
`C*` are client rounds, `L*` vendor rounds, `CF` culture fit. **Omitting `rounds` returns every
round**, which is usually what "all their questions" means.

**Technologies** — 207 canonical tags. Everyday wording works: `spring boot` → `SPRINGBOOT`,
`k8s` → `KUBERNETES`. `REACT_NATIVE` is deliberately separate from `REACT`.

**Data quality** — results carry `data_quality` reason codes. Flagged rows are still valid and
still searchable; the code explains what is unknown. If a field is missing, say it is unknown and
why. Do not drop the row or substitute another.

---

## Examples

| Request | Call |
|---|---|
| "What does Vanguard ask data engineers?" | `client='Vanguard', track='DATA_ENGINEER'` — then summarise themes |
| "What do they usually ask?" | `get_question_frequency` with the same filters |
| "Someone who knows ETL and Snowflake" | `tags=['ETL','Snowflake']` — report OR and AND counts |
| "Java engineer who touched DevOps" | `track='JAVA', tags=['Docker','Kubernetes']` |
| "What did we ask this candidate?" | `get_candidate_history`, then `get_interview_document` |
| "Excel for Randstad/Vanguard DE since January" | search → summary → confirm → export |

**Clarify only when it changes the answer.** A request naming a vendor, client or technology is
searchable as-is — search it and report. Ask when nothing narrows it at all, when "data" or
"frontend" could mean two tracks, or when an export would be unusably large. Ask once, propose a
default, and let them say yes.
