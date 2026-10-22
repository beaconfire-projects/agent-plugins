---
name: candidate-matching
description: "Recommend candidates for a job description or reference interview questions, or refresh the resume index after uploads. Use for \"who fits this JD?\", shortlisting people for a position, or finding candidates with related interview-question experience. A recruiter asking who fits wants a compact ranked table first: rank, candidate, overall score and risks. Keep commentary minimal; detailed evidence is on request."
allowed-tools:
  - mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__match_candidates
  - mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__ingest_resumes
  - mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__get_candidate_history
---

# Candidate matching

Use `match_candidates` to recommend up to five distinct eligible people for a role
or reference interview questions. `ingest_resumes` is a separate admin refresh.
Read the response status before presenting results.

The nullable controls have effective matching defaults of
`include_interview_questions=true` and `limit=5`. The server attempts integer
conversion; invalid or less-than-one limits fall back to five, and larger values
are capped at five. The final cap is `min(effective limit, MATCH_FINAL_TOP_N, 5)`;
server configuration may lower it. Fewer than five, including zero, is valid.

## MCP routing — this environment only

Use only the `marketing-data-warehouse` warehouse server bundled by the `marketing-data-warehouse` plugin.
In Claude Code it is registered as `plugin:marketing-data-warehouse:marketing-data-warehouse`.
Short tool names elsewhere in this skill are aliases for these exact tools:

| Short name | Required tool |
|---|---|
| `match_candidates` | `mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__match_candidates` |
| `ingest_resumes` | `mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__ingest_resumes` |
| `get_candidate_history` | `mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__get_candidate_history` |

Before calling, confirm the required tool is registered under this server.
If missing, disconnected, unauthorized or failed, stop the warehouse operation
and report the connection/tool problem; ask to enable, authenticate or reload
this plugin as appropriate. Never substitute a same-named tool from another
plugin, a bare/unscoped server, or the other environment. Do not retry against
another warehouse, merge its results, or change MCP configuration to bypass this
rule. A request for another environment must use that environment's skill instead.
The `allowed-tools` header pre-approves only the listed tool calls; it does not
make other tools unavailable. Follow the routing rules above, and still require
the user request/confirmation specified below before any refresh or export.

## Default reply: ranked table first, minimal commentary

When candidates are returned, start immediately with **one complete ranked table**
using exactly these four columns (translate headers for a non-Chinese reply):

```text
| 排名 | 候选人 | 综合分 | 风险 |
|---|---|---|---|
| <rank> | <name> (<person_id>) | <overall> | <brief risks or —> |
```

- Include every returned candidate in server rank order, one row per person.
  Always show **name (person_id)**, preserving TEMP IDs. Use the returned `overall`
  for 综合分, not the 0–1 `fusion_score`; never invent or adjust scores. If absent,
  show `—`. Do not add a reasons, resume or source column.
- In 风险, use short readable labels such as **低匹配备选** for
  `recommendation_tier=fallback` / `low_match` and **年限未知** for `yoe_unknown`.
  Preserve other material risks briefly. Use `—` when no risks are reported;
  this is not a guarantee that the candidate is risk-free.
- No introduction, methodology or analysis before the table. Do not split off the
  top candidate for a long review or append per-person paragraphs. This applies
  to initial matches and follow-up/re-run results alike.
- After the table, use at most **one or two short sentences** for material warnings,
  incomplete coverage/withheld people or a shortfall, and `location_disclaimer`.
  Combine notices; do not repeat per-person caveats or add an unsolicited next-step
  checklist, resume audit, or offer to refresh/match again.
- By default, omit score explanations, raw tier/state names, source-by-source
  coverage, pool statistics, formulas, lengthy quotes and resume file/version
  details. Expand evidence, resume details, ranking rationale or diagnostics
  **only when the user explicitly asks**. The interpretation rules below are for
  reasoning correctly, not a checklist of fields to print in every answer.
- Brevity must not hide fallback status, material risks, operational failure or
  incomplete coverage. With no candidates, give the status/reason or required
  clarification briefly instead of fabricating table rows.

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
accepts `person_id` for a scoped admin refresh. Local source changes alone
do not establish deployment.

## Current engine and deployment boundary

The current implementation uses **candidate_v2 only**, with ranking policy
`candidate-fusion-v3`. Responses identify `engine=candidate_v2`,
`schema_version=candidate-v2` and `policy_version=candidate-fusion-v3`; these
metadata fields alone do not mean matching succeeded. Always read `status`.
The legacy funnel and engine switch are retired; `MATCH_ENGINE` is ignored.
Never change server configuration or switch ranking policy after a failure.

Do not assume dev/prod has deployed this code. If the live schema or response
still exposes an older contract (such as `FEATURE_DISABLED` for interview IDs),
report the deployment/schema mismatch for operator resolution. Do not advise
enabling the retired engine switch or silently discard reference inputs.

## Matching inputs

- **JD:** Nonblank `jd_text` takes precedence over the supplied position's current
  stored JD; conflicts appear in `warnings`. Use `position_id` in `POS-XXXX` form
  (e.g. `POS-0440`); normalize an unambiguous shorthand, never guess an ID. Every
  supplied position/interview locator is validated even when inline text wins.
  Unknown locators return `not_found`.
- **Incomplete JD:** A supplied or stored nonblank JD needs at least 100 normalized
  characters, usable technical source text, and parsed required skills or
  responsibilities. Otherwise expect `needs_jd`; ask for `missing_fields`.
  Questions cannot rescue an incomplete JD,
  and the agent must not invent or pad a JD to force a match.
- **Explicit references:** `interview_questions` is pasted question text;
  `interview_ids` is a list of known interview IDs. When both are supplied, the
  server unions and deduplicates their questions with provenance. These locators
  select reference questions, **not** the people eligible for recommendation.
  Supplying either parameter suppresses automatic similar-position discovery,
  even if its value is an empty string/list. Omit unused parameters.
- **Automatic references:** With a JD, no explicit references and automatic
  discovery enabled, the server discovers up to ten similar current-JD positions
  at normalized similarity
  >=0.50 and includes any supplied position when resolving questions. This is
  not the candidate recommendation threshold. A position without a JD can use
  its own questions only when automatic references are enabled.
- **Questions only:** Without a JD, usable question text or interview references
  run only the question-experience round; skill/resume rounds are `not_executed`.
  Empty valid references with a usable JD still permit skill/resume matching.
  Neither a JD nor usable questions → `needs_reference`; ask for a JD, question
  text or known interview IDs, never fabricate reference material.
- **Controls:** `include_interview_questions=false` disables automatic stored
  reference discovery, not explicit question text/interview IDs or the search
  for related candidate histories. `chat_context` is compatibility-only: it
  creates neither a JD nor reference questions.

## Read status before presenting anyone

| Status | Action |
|---|---|
| `ok` | Show the four-column ranked table first; label low-match alternatives in the risk column. Briefly note a shortfall after the table if reported. |
| `no_match` | Relay `rejection_reason` and any `insufficient_causes`; do not relax qualifications or invent filler. |
| `needs_jd` | Ask for the reported missing JD fields and retry with real `jd_text`. |
| `needs_reference` | Ask for a usable JD or question/interview references. |
| `not_found` | Resolve the unknown position or interview ID; this is not a valid empty match. |
| `degraded` | Show returned candidates in the table first, if any; add a short coverage warning with the withheld count when relevant. Summarize material warnings, not raw diagnostics. An empty degraded result does not prove nobody qualifies. |
| `error` | Stop and report the safe error code/message; do not turn an operational failure into `no_match`. |

For `INVALID_INPUT`, correct the parameters. `IDENTITY_AMBIGUOUS` needs identity
clarification, not a guessed alias. Availability or reference-budget errors
require recovery or a user-agreed narrower scope, not silent truncation or an
algorithm fallback. Requests allow at most 64 deduplicated reference questions
and have a bounded text budget; never trim supplied references without agreement.

## Ground the shortlist in evidence

**Always show name + id together.** Use the returned `name (person_id)`, e.g.
`Ilana Zhu (PER-0123)`, for every shortlisted person. Preserve returned TEMP IDs;
do not invent a formal ID. Use this person ID as `person_id` for an explicitly
requested resume refresh.

Preserve server rank and use returned `reasons`, `references`, `risks` and
`recommended_resume` to ground the answer, not as mandatory output sections.
Default to the four-column table above, with returned overall scores and brief
material risk labels, not per-person explanations. Provide evidence or resume information only
on explicit request. References must come from the tool, never invented quotes
or links. V2 evidence comes from related
interview questions, consultant `additional_tech_stacks`, and current resumes.
Interview-question exposure is **not mastery**; interview outcomes/pass-fail are
not ranking features, and skills must not be inferred from `batch_track`.

Eligibility requires a valid current consultant profile with status
**`IN MARKETING` only** (trimmed and case-normalized). `IN PREPARATION`,
`In Prepareing`, other and unknown statuses are excluded. JD-based YOE uses a
±2-year tolerance, and unknown YOE passes but remains a disclosed risk.
No JD means no invented YOE filter. A resume is not required. Status and evidence
come from the synchronized warehouse, not a live Sheets/Drive read on each match.

### Ranking and low-match alternatives

Question/skill/resume relevance uses weights **3:4:3**, normalized over
`present_scored` sources. `overall = 100 × fusion_score`; both describe relevance,
not probabilities of success or confidence. Real zero scores stay in the fusion
denominator; missing or unexecuted sources do not. Strong lower-weight evidence
can outrank weaker higher-weight evidence. Do not re-rank by source priority or
an LLM opinion.

Each source contributes at most its **50 positive-scoring distinct people**.
The deduplicated union (at most 150 people) is frozen, then fully revalidated and
rescored. The 0.5 standard threshold does not exclude low-positive people from
this initial pool. Lost candidates are not replaced from outside the fixed pool.
Every returned person must still be eligible, have no executed source marked
`unavailable`, have positive fusion, and have a valid positive evidence reference.

| `recommendation_tier` | Presentation |
|---|---|
| `standard` | At least one source score >=0.5 and fusion score >=0.5 after revalidation. Present as a standard match, not a guarantee of ability. |
| `fallback` | Other safe, evidence-backed positive matches, returned only when standard matches do not fill the requested cap. Use the brief label **低匹配备选** (low-match alternative) and other material risk labels. Show the actual overall score in the table; expand evidence only if requested. Never inflate scores. |

Fallback has no separate fixed minimum score; it is not permission to recommend
zero-score, uncited or unavailable evidence. Standard candidates come first;
within each tier the server sorts by unrounded fusion descending, then person ID
ascending. Preserve returned rank. Low-match alternatives alone do not cause
`degraded`, and neither fallback nor extra invented candidates should be used to
hide a shortfall.

Use `round_stats`, per-candidate `source_scores` / `coverage`, `withheld_count`
and `reference_resolution` internally to interpret coverage, and explain them
only when asked for diagnostics. Still give a brief coverage warning for degraded
results in the default reply. `round_stats`
counts initial source states, not final recommendations. `withheld_count` counts
operational/evidence withholding, not everyone omitted by eligibility, pool
budgets or ranking. Returned `source_scores` cannot reconstruct omitted people's
scores. Compatibility `funnel_stats` L2/L3/L4 zeros are retired counters, not
evidence that matching found nobody.

| Evidence state | Meaning |
|---|---|
| `present_scored` | Usable scored evidence, including a genuine zero-relevance mismatch. |
| `absent` | No usable content; excluded from fusion, not a penalty. |
| `not_executed` | The request did not activate this round. |
| `unavailable` | Evidence could not safely be used (e.g. outdated vectors, pending processing or failed verification); affected candidates are withheld, not treated as merely missing evidence. |

### Resume freshness and recommended files

Matching accepts current DOCX or Google Docs resume evidence only when the source
Drive modification time is known and within the last **365 days** (inclusive),
ownership is valid, verification matches the current content hash, and compatible
vectors are ready. Creation/ingestion dates do not substitute for modification
time. Expired, unknown-time or unsupported files are policy exclusions and can
leave resume evidence `absent`; they do not alone disqualify a person with other
healthy evidence. Recent supported files that are pending, failed, unverified or
misattributed make coverage `unavailable`. One unsafe required resume can withhold
the person even if another resume is healthy; do not cherry-pick around the failure.

`recommended_resume` can be null, especially for question-only matches. When
present, it is selected from scored resume references, not an LLM-picked "best"
resume; fused evidence can span multiple files. Do not invent a best-fit resume
or treat an unscored resume link as scored evidence.
Drive links require the recipient's permissions; a returned URL does not grant access.

**Always relay `location_disclaimer` once, briefly after the table.** Location is
NOT considered. Use the returned disclaimer (e.g. "本期匹配未考虑 Location 维度")
without appending a generic verification checklist.

## Resume refresh is admin work

`ingest_resumes` re-scans the Resume subtree of each mapped Prepare folder on Google
Drive, processes eligible recent DOCX/Google Docs resumes and stores verified
versions after freshness and ownership checks. It does not make old files fresh
merely by ingesting them. Run it only when the AM requests a refresh after
uploads/updates; pass `person_id` to scope it to one person. Never run it speculatively before a match or as a search tool.

Report the returned status, per-action `counts` and `source_revision`; `failed`
or `error` means the refresh did not complete successfully. This tool is not the
separate v2 evidence-vector refresh and does not guarantee fresh v2 coverage.
Do not trigger backfills, paid vector refreshes or configuration changes to
repair a degraded result. If a match was requested, re-run it after a successful
ingestion and still honor any freshness/coverage warnings.

## Examples

| Request | Call |
|---|---|
| "Who fits this JD?" | `match_candidates(jd_text=...)`; show the rank / name + ID / overall score / risks table first, then at most two short sentences for location/coverage notices. |
| "Anyone for position POS-0440?" | `match_candidates(position_id="POS-0440")`; follow returned status and engine. |
| "Who has related experience with these questions?" | `match_candidates(interview_questions=...)`; only the question-experience source executes without a JD. |
| "Use these interview records as references" | `match_candidates(interview_ids=[...])` with real IDs; add `jd_text` if supplied. |
| "Use this JD and both sets of references" | `match_candidates(jd_text=..., interview_questions=..., interview_ids=[...])`; the server unions the explicit references. |
| "Match only this JD, without automatic question discovery" | `match_candidates(jd_text=..., include_interview_questions=false)`; omit unused reference parameters. |
| "We uploaded new resumes; refresh the index" | `ingest_resumes()`; re-run matching only if requested. |
| "Refresh resumes for PER-0123" | `ingest_resumes(person_id="PER-0123")`. |
