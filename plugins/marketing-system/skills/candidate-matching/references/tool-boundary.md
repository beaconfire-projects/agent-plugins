# Verified tool boundary

This skill's capability contract lists **1 tool**. It was checked against its actual decorator in the local backend checkout (`modules/marketing/mcp/candidate_matching.py`), and the declaration is `tags={"marketing", "candidate-matching"}`. This is source-contract verification, not a claim that the connected deployment has the tool: verify that the connected `marketing-system` server exposes it with a tag set that includes `marketing` and a compatible schema before the first call. Allow only a tool whose actual declared tags include `marketing`; a `marketing_` name prefix or a module directory is not proof.

Source paths below are code provenance under `backend/app/`, not runtime calls or relative file links.

## Candidate matching (1)

Source: `modules/marketing/mcp/candidate_matching.py`. The listed decorator has tags `marketing`, `candidate-matching`. Workflow: [SKILL.md](../SKILL.md).

- `marketing_match_candidates`

Inputs: `position_code`, `jd_text`, `interview_questions`, `interview_ids`, `include_interview_questions`, `limit` (1-5). Read-only; it sends sanitized JD, question and tech-stack text to the OpenAI embedding service and may call DeepSeek to parse YOE from the JD.

## Not allowed

No other tool qualifies for this skill, including:

- staffing-only tools and tools without the `marketing` tag, even if their names begin `marketing_`;
- the data-warehouse plugin's `match_candidates`, `ingest_resumes` and `get_candidate_history`;
- REST, SQL or scripts that rank people or read the vector tables directly.

Reading a person, checking a resume upload, sending the Consultant form, or looking up a position uses tools that belong to the `marketing` skill and its own [tool boundary](../../marketing/references/tool-boundary.md); do not call them from here as a substitute for a missing matching tool. If the tool is missing, its tags cannot be verified, or its schema differs, stop and report the capability gap; never replace it with another tool, REST, SQL or a script.
