---
name: candidate-matching
description: Recommend trainees for a job description. Use for any "who fits this JD?" request — shortlisting candidates for a role, matching trainees to a position, or refreshing the resume index after new resumes are uploaded. A recruiter asking who fits wants a shortlist with evidence, not documents.
---

# Candidate matching

`match_candidates` recommends 0–5 trainees for a role. A recruiter asking
*"who fits this JD?"* wants a shortlist with evidence, not documents.

**Feed it whatever the AM has — the most specific source wins.**
`jd_text` (a pasted job description) beats `position_id` even when both are given; conflicts
are flagged in `warnings`. `position_id` alone reads the stored JD: an unknown id returns
`status=not_found`, an incomplete stored JD returns `status=needs_jd` with `missing_fields`
— ask the AM for the missing pieces and call again with `jd_text`. With only `chat_context`
or only `interview_questions`, the tool derives what it can and returns `needs_jd` rather
than a low-quality guess — never invent a JD to force a match. Interview-question text the
AM pastes takes priority over the question bank; `include_interview_questions=false` skips
the bank signal entirely (pasted text still applies).

**Read the status before presenting anyone.**
`ok` → present the shortlist. `no_match` → nobody qualified; relay the `rejection_reason`,
never suggest loosening the criteria. `needs_jd` / `not_found` → resolve the input, don't
guess. `degraded` → say which signal was missing. `error` → stop and report the message.
`limit` is clamped to 5; invalid values fall back to 5.

**Every recommendation is traceable — show the evidence.**
Each candidate carries `reasons[].references[]` pointing at a resume version, an interview
document or a training record, plus a `recommended_resume` and `risks`. Present the reasons
and risks, not just the names; a shortlist without evidence is unusable for an AM.

**Always relay the location disclaimer.**
Location is NOT considered this phase. The result carries `location_disclaimer` — repeat it
every time, e.g. *"Location wasn't considered — double-check where each trainee can work
before proposing them."*

**`ingest_resumes` is an admin refresh, not a search tool.**
It re-scans the Resume subtree of each mapped Prepare folder on Drive, embeds every DOCX and
stores new versions. Run it when the AM says resumes were updated, or pass `person_id` for
one trainee. Never run it speculatively before a match.

---

## Examples

| Request | Call |
|---|---|
| "Who fits this JD?" | `match_candidates` with `jd_text` — present reasons, risks and the location disclaimer |
| "Anyone for position 1234?" | `match_candidates` with `position_id` — if `needs_jd`, ask the AM for the missing fields |
| "We uploaded new resumes" | `ingest_resumes` (admin) — then re-run the match |
| "Refresh resumes for one trainee" | `ingest_resumes` with `person_id` |
