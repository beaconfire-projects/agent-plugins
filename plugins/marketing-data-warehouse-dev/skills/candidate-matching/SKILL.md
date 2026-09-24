---
name: candidate-matching
description: Recommend candidates for a job description or reference interview questions, or refresh the resume index after uploads. Use for "who fits this JD?", shortlisting people for a position, or finding candidates with related interview-question experience. A recruiter asking who fits wants a shortlist with evidence, not documents.
---

# Candidate matching

Use `match_candidates` to recommend up to five distinct eligible people for a role
or reference interview questions. `ingest_resumes` is a separate admin refresh.
Read the response status before presenting results.

The nullable controls have effective matching defaults of
`include_interview_questions=true` and `limit=5`. The server caps results at five;
invalid numeric limits fall back to five. Fewer than five, including zero, is valid.

## Tool input contract

`match_candidates` accepts only these seven inputs: `position_id`, `jd_text`,
`chat_context`, `interview_questions`, `include_interview_questions`, `limit`
and `interview_ids`.

`candidate_id` has been removed with no compatibility alias. Never send it,
including as null. If a cached MCP schema or old call still includes it, refresh
the MCP tool schema and rebuild the call using only supported inputs; stale
calls fail argument validation before matching runs. Do not substitute
`person_id`: matching has no person-scoping input. Reference locators select
questions, not the people eligible for recommendation. A candidate-history
request belongs to the separate `get_candidate_history` tool, using its own schema.

Returned candidate `person_id` fields are unchanged. `ingest_resumes` still
accepts `person_id` for a scoped admin refresh. The source interface change alone
does not establish deployment or engine enablement.

## Respect the server's engine

Matching defaults to the **legacy** JD/resume funnel. **candidate_v2** requires
operator enablement; the skill must not assume it is deployed or enabled.
`interview_ids` under legacy returns `FEATURE_DISABLED`, even for an empty list.
V2 matching responses identify `engine=candidate_v2`; `schema_version=candidate-v2`
alone does not prove v2 ranking ran (routing errors also use it).
Never change server configuration or silently substitute legacy ranking after a
v2 failure.

### Inputs for candidate_v2

- **JD:** Nonblank `jd_text` takes precedence over the supplied position's current
  stored JD; conflicts appear in `warnings`. Use `position_id` in `POS-XXXX` form
  (e.g. `POS-0440`); normalize an unambiguous shorthand, never guess an ID. Every
  supplied position/interview locator is validated even when inline text wins.
  Unknown locators return `not_found`.
- **Incomplete JD:** A supplied or stored nonblank JD needs at least 100 normalized
  characters and parsed required skills or responsibilities. Otherwise expect
  `needs_jd`; ask for `missing_fields`. Questions cannot rescue an incomplete JD,
  and the agent must not invent or pad a JD to force a match.
- **Explicit references:** `interview_questions` is pasted question text;
  `interview_ids` is a list of known interview IDs. When both are supplied, the
  server unions and deduplicates their questions with provenance. These locators
  select reference questions, **not** the people eligible for recommendation.
  Supplying either parameter suppresses automatic similar-position discovery,
  even if its value is an empty string/list. Omit unused parameters.
- **Automatic references:** With a JD and no explicit references, the server
  discovers similar current-JD positions and includes any supplied position when
  resolving questions. A position without a JD can use its own questions only.
- **Questions only:** Without a JD, usable question text or interview references
  run only the question-experience round; skill/resume rounds are `not_executed`.
  Empty valid references with a usable JD still permit skill/resume matching.
  Neither a JD nor usable questions → `needs_reference`; ask for a JD, question
  text or known interview IDs, never fabricate reference material.
- **Controls:** `include_interview_questions=false` disables automatic stored
  reference discovery, not explicit question text/interview IDs or the search
  for related candidate histories. `chat_context` is compatibility-only: it
  creates neither a JD nor reference questions.

### Legacy compatibility

Use `jd_text` or `position_id` for legacy matching. Inline JD wins; unknown positions
return `not_found`, and missing/incomplete JD returns `needs_jd` with `missing_fields`.
Chat-only or question-only input still goes through legacy JD assembly/completeness
checks, not the v2 questions-only flow. If it returns `needs_jd`, ask for missing
information rather than inventing a JD. Pasted `interview_questions` take priority
over the bank; `include_interview_questions=false` skips the bank but retains pasted text.
Do not promise v2 reference fusion, evidence states or ranking semantics for legacy
responses.

## Read status before presenting anyone

| Status | Action |
|---|---|
| `ok` | Present the returned shortlist. |
| `no_match` | Relay `rejection_reason` and any `insufficient_causes`; do not relax qualifications or invent filler. |
| `needs_jd` | Ask for the reported missing JD fields and retry with real `jd_text`. |
| `needs_reference` | Ask for a usable JD or question/interview references. |
| `not_found` | Resolve the unknown position or interview ID; this is not a valid empty match. |
| `degraded` | Present only returned candidates, if any, and explicitly report incomplete coverage, warnings and withheld evidence/people. An empty degraded result does not prove nobody qualifies. |
| `error` | Stop and report the safe error code/message; do not turn an operational failure into `no_match`. |

For `INVALID_INPUT`, correct the parameters. `IDENTITY_AMBIGUOUS` needs identity
clarification, not a guessed alias. `FEATURE_DISABLED` needs operator enablement
before interview-ID matching can work; ask for a supported JD-based request instead
of silently discarding the references. Availability or reference-budget errors
require recovery or a user-agreed narrower scope, not silent truncation or fallback.

## Present evidence, not just names

**Always show name + id together.** Use the returned `name (person_id)`, e.g.
`Ilana Zhu (PER-0123)`, for every shortlisted person. Preserve returned TEMP IDs;
do not invent a formal ID. Use this person ID as `person_id` for an explicitly
requested resume refresh.

For each recommendation, preserve server rank and summarize `reasons`, their
`references`, `risks`, and `recommended_resume` when present. References must come
from the tool, never invented quotes or links. V2 evidence comes from related
interview questions, consultant `additional_tech_stacks`, and current resumes.
Interview-question exposure is **not mastery**; interview outcomes/pass-fail are
not ranking features, and skills must not be inferred from `batch_track`.

V2 fuses question/skill/resume relevance with weights **5:3:2**, normalized over
present scored sources. Scores (`fusion_score` / `overall`) are relevance, not
probabilities of success or confidence. Strong lower-weight evidence can outrank
weaker higher-weight evidence; do not re-rank by source priority or an LLM opinion.
Eligibility is current `IN MARKETING` / `IN PREPARATION` consultants; JD-based YOE
uses a ±2-year tolerance, and unknown YOE passes but remains a disclosed risk.
No JD means no invented YOE filter. A resume is not required.

Use v2 `round_stats`, per-candidate `source_scores` / `coverage`, `withheld_count`
and `reference_resolution` to explain execution and coverage. In v2 responses, the
compatibility `funnel_stats` L2/L3/L4 zeros are retired counters, not evidence that
v2 found nobody.

| Evidence state | Meaning |
|---|---|
| `present_scored` | Usable scored evidence, including a genuine zero-relevance mismatch. |
| `absent` | No usable content; excluded from fusion, not a penalty. |
| `not_executed` | The request did not activate this round. |
| `unavailable` | Evidence could not safely be used (e.g. stale, pending or failed); affected candidates are withheld, not treated as merely missing evidence. |

`recommended_resume` can be null, especially for question-only matches. Do not
invent a best-fit resume or treat an unscored resume link as scored evidence.
Drive links require the recipient's permissions; a returned URL does not grant access.

**Always relay `location_disclaimer`.** Location is NOT considered. Repeat the
returned disclaimer every time, e.g. "Location wasn't considered
— double-check where each candidate can work before proposing them."

## Resume refresh is admin work

`ingest_resumes` re-scans the Resume subtree of each mapped Prepare folder on Google
Drive, summarizes/embeds DOCX resumes and stores new versions. Run it only when the
AM requests a refresh after uploads/updates; pass `person_id` to scope it to one
person. Never run it speculatively before a match or as a search tool.

Report the returned status, per-action `counts` and `source_revision`; an error
means the refresh did not complete successfully. This tool is not the separate v2 evidence-vector
refresh and does not guarantee fresh v2 coverage. Do not trigger backfills or engine
activation to repair a degraded result. If a match was requested, re-run it after
a successful ingestion and still honor any freshness/coverage warnings.

## Examples

| Request | Call |
|---|---|
| "Who fits this JD?" | `match_candidates(jd_text=...)`; present reasons, risks and the location disclaimer. |
| "Anyone for position POS-0440?" | `match_candidates(position_id="POS-0440")`; follow returned status and engine. |
| "Who has related experience with these questions?" | `match_candidates(interview_questions=...)`; questions-only matching requires v2. |
| "Use these interview records as references" | `match_candidates(interview_ids=[...])` with real IDs; add `jd_text` if supplied; requires v2. |
| "Use this JD and both sets of references" | `match_candidates(jd_text=..., interview_questions=..., interview_ids=[...])`; v2 unions the explicit references. |
| "Match only this JD, without automatic question discovery" | `match_candidates(jd_text=..., include_interview_questions=false)`; omit unused reference parameters. |
| "We uploaded new resumes; refresh the index" | `ingest_resumes()`; re-run matching only if requested. |
| "Refresh resumes for PER-0123" | `ingest_resumes(person_id="PER-0123")`. |
