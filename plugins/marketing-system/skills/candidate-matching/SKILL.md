---
name: candidate-matching
description: Recommend up to five candidates from the Marketing pool (In Marketing) for a job description, a position or reference interview questions. Use for "who fits this JD / position?", shortlisting people, or finding candidates with related interview-question experience. Read-only; ranks by related interview questions, tech stacks and the current resume. Only the verified marketing-tagged tool marketing_match_candidates is allowed.
---

# Candidate matching

Use only the connected `marketing-system` MCP tool `marketing_match_candidates`, as listed in the [verified tool boundary](references/tool-boundary.md). Its decorator `tags` must contain `marketing` (it declares `marketing` and `candidate-matching`, source `modules/marketing/mcp/candidate_matching.py`): a name prefix or module directory is not proof, so verify the tag on the connected deployment. Do not use staffing-only tools, the data-warehouse plugin, REST, SQL or scripts to rank candidates. If the tool is missing, its tags cannot be verified, or its schema differs, stop and report the capability gap.

Other Marketing work (reading a candidate, creating a submission, checking a resume upload) belongs to the `marketing` skill; this skill only produces the shortlist.

## What it does

The backend recommends up to five distinct people from the marketing pool (marketing status `In Marketing` only; `In Preparation` is not in the pool). The unit is a person, never a resume file. It is read-only; nothing is written. Three kinds of evidence are scored and fused with weights 3:4:3 (policy `candidate-fusion-v3`):

1. **Question** (3): the person's own interview questions that resemble the reference questions. Related exposure, not mastery. Interview results and scores are never ranking features.
2. **Skill** (4): the JD against the person's `additional_tech_stacks` (stored vector).
3. **Resume** (3): the JD against the person's current resume (status `embedded`, all chunks ready).

Evidence that does not exist is left out of the average and is not a penalty. Evidence that exists but is pending, stale or failed (for example a tech stack edited a moment ago whose vector is still being regenerated) withholds the person, so a half-processed profile can never rank better by being incomplete. For each kind of evidence only the top 50 people with a positive score enter the candidate pool (at most 150 in all); nobody outside it is added later. Within the pool a person is `standard` when some source and the fused score are both at least 0.50. Other people with a positive score fill the remaining places as `fallback`: they carry the `low_match` risk and their true score, which is never raised. Standard results always rank before fallback ones. Fewer than five results is normal; no one is invented to fill the list. Location is not considered; say so when presenting results. YOE is `person.years_of_experience`; when the JD states a range the pool is filtered to that range plus or minus two years, and unknown YOE passes and is flagged `yoe_unknown`.

## Prerequisites and order

1. Pick the input. Nothing else is needed from other tools.
   - A position: pass `position_code` (`POS-…`). Its stored JD is used, and `include_interview_questions` (default true) adds that position's own recent interview questions.
   - Pasted JD: pass `jd_text`; it overrides the position's stored JD (a warning says so).
   - Reference questions only: pass `interview_questions` (one per line) and/or `interview_ids` (`INT-…`). These select questions, not the people eligible. Passing either turns off the position's automatic questions.
2. Call `marketing_match_candidates`. Look up an unknown position with the `marketing` skill first; never guess a code.
3. Read `status` before anything else.

## Reading the result

| status | meaning and action |
| --- | --- |
| `ok` | Present the candidates. |
| `degraded` | Candidates are valid, but some people were withheld for pending or failed evidence (`withheld_count`). Say coverage is incomplete. |
| `no_match` | No eligible person has a positive, usable score. Say so; do not pad the list. |
| `needs_jd` | The JD is shorter than 100 characters or names no required skills or responsibilities. Ask the user for a fuller JD (`missing_fields`). Never invent or pad one. |
| `needs_reference` | No JD and no usable questions. Ask for one. |
| `not_found` | The position or interview does not exist or is outside the caller's scope. Do not search for a way around the scope. |
| `error` | Embedding service unavailable or too many explicit reference questions (max 64). Report `rejection_reason`; no fallback ranking exists. |

Present a compact ranked table first: rank, `name (person_code)`, `overall` (0-100, do not recompute), one or two evidence-grounded reasons from `reasons`, a tier column (`recommendation_tier`: `standard` as "recommended", `fallback` as "weak match, for reference only"), and risks (`yoe_unknown` as "YOE unknown", `low_match` as "low match"). List standard rows first as returned; never present a fallback as a firm recommendation. Keep `warnings` and the location note to one or two sentences after the table. Put `resume_url` in an "original resume" column as a clickable link when it is present; it is the Google Drive copy of the current resume. When it is null the resume has not been copied to Drive: show "not provided" and never construct a link from an ID. Show `resume_id` only as an identifier; use the Consultant form and resume workflow for resume status. Expand evidence only when asked.

## Business constraints

- Matching shows relevance of existing evidence, not ability, hire probability or interview outcome.
- **Similar positions are discovered automatically.** With a JD (pasted or a position's) and no explicit references, the backend finds up to ten visible positions whose stored JD vectors are at least 0.70 similar, adds their recent interview questions (plus the supplied position's own) as the reference, and reports `discovered_position_count`. Positions whose JD vector is not ready yet count in `unavailable_position_count` and make the result `degraded`. More than 64 distinct questions are capped with a warning, keeping the most similar positions first. Passing `interview_ids` or `interview_questions` (even empty) turns discovery off.
- **Vectors are generated asynchronously.** Saving a position JD or a consultant's additional tech stack publishes `position.jd_changed` / `person.tech_stack_changed`; a subscriber replaces the old vector and re-embeds just that one item, and an hourly reconciliation job covers writes without events (imports) and missed events. Until it finishes, the changed item is `unavailable`. If a match reports `degraded` right after an edit, wait a minute and run it again; do not treat it as an error. A tech stack that is empty is `absent`, not a penalty.
- If DeepSeek is not configured the YOE filter is skipped and a warning says so.
- The match never writes. Vector regeneration is automatic; there is no tool to trigger it.
- JD, question and tech-stack text is sent, with emails, URLs and phone numbers removed, to the OpenAI embedding service. Do not paste candidate contact details into `jd_text`.
- A person without an embedded current resume is not penalised; if the resume is still processing they are withheld. Use the `marketing` skill's Consultant form and resume workflow to check or finish the upload.

## Error handling

- `candidate_matching_failed`: the call wrote nothing, so retrying once is safe. Report persistent failures rather than looping.
- A `degraded` result is not an error. Do not re-run just to remove it unless the user asks.

## Hand-offs

- To read a recommended person, check their resume processing or send the Consultant form, use the `marketing` skill (Candidate and Consultant form and resume workflows).
- To look up a position code or create a position, use the `marketing` skill's Position workflow, then come back here.
