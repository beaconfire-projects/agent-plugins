---
name: self-introduction-review
description: Score and coach a candidate's interview self-introduction (spoken audio or text) against Beaconfire's 10-part structure. Reports which parts are covered or missing, a part-by-part score, an overall score and band, objective evidence, and concrete fixes. Use when a Trainer or AM wants to check whether a candidate's self-introduction meets company standard. Requires a signed-in Beaconfire account.
---

# Self-introduction review (10-part standard)

Audience: Trainers and AMs. Input: one candidate's self-introduction as an audio recording or as text. Output: an objective, evidence-based scorecard and improvement plan. Do not rewrite the candidate's story from scratch; judge what was actually said.

## Step 0 — Sign-in gate (always first)

Before reading the rubric or evaluating anything, call the `list_dimensions` tool of the `marketing-data-warehouse` MCP connector once (it is read-only).

- Success: continue.
- Tool unavailable, authentication error, or any failure: stop. Tell the user this skill is for signed-in Beaconfire staff, ask them to authenticate the `marketing-data-warehouse` connector (via `/mcp` in Claude Code, or the connector settings in the app), then retry. Do not score, summarize the rubric, or offer a partial review.

Never show the user the tool's output; the call only verifies sign-in.

## Step 1 — Input

- Accept audio (any format the environment can decode) or pasted/attached text. If neither is provided, ask only for the candidate's self-introduction.
- Do not ask for a JD, resume, or target role. Ask nothing else unless the input is unusable.
- Audio: transcribe with an available transcription capability, near-verbatim, with timestamps when offered; mark `[unclear]`; never fill gaps from an expected script. If the audio cannot be decoded or transcribed (for example this environment has no transcription tool, as in a web chat), stop and reply in the requester's language with this guidance instead of a bare error:
  1. This environment cannot transcribe the audio, so it cannot be scored directly.
  2. Get a transcript elsewhere: a meeting tool's own transcript (Zoom, Otter, Feishu Minutes), or locally `mlx_whisper <file> --model mlx-community/whisper-large-v3-turbo --output-format txt` (needs ffmpeg).
  3. Paste or attach the transcript with timestamps, and keep interviewer and candidate lines distinguishable. A transcript still gets a full structural score; only pace and delivery are "not assessed".
- If several speakers appear, evaluate only the candidate's prepared introduction. Prompted answers to interviewer follow-ups do not count toward coverage.
- Text input: delivery, pace and length-in-minutes are "not assessed" unless the user supplies the duration (about 130 spoken words per minute is a rough guide).

## Step 2 — Evaluate

Read `references/rubric.md` and follow it exactly: the 10 parts, per-part criteria, score levels, weights, bands, and hard checks. Key principles:

- Judge each part as **Covered / Partial / Missing** with evidence: a short quote (with timestamp when available) or an explicit "not found".
- Parts 1–5 are about the project; parts 6–10 are about the candidate. Penalize mixing them, going backwards in the narrative, and technology lists that replace business explanation.
- Team results must be credited to the team (part 5); the candidate's own result belongs in part 8. Flag any team result presented as personal.
- Challenges (part 9) should be 2–3 one-line hooks that invite questions, not full solutions.
- Never invent facts, metrics, tools, ownership, or dates, and never penalize the candidate for experience they may have but did not say; say "not stated". Do not infer from accent or name.
- Be objective. Do not inflate scores to be encouraging; do not use a bare "good/bad" without evidence.

## Step 3 — Report

Write in the requester's language (default Chinese); keep quotes and sample wording in the language the candidate used. Use this order, concise and table-first:

1. **Verdict line:** total score /100, band, one-sentence reason.
2. **Part checklist table:** `# | Part | Status | Score | Evidence / what is missing`, all 10 parts plus the overall-quality row.
3. **Covered vs missing:** two short lists.
4. **Strengths:** at most 3, each with evidence.
5. **Priority fixes:** 3–5 items ordered by score gain, each with what was heard, why it loses points, and a one-to-two-sentence spoken fix built only from facts the candidate stated (mark unknown facts `[confirm]`).
6. **Hard-check flags:** any that triggered (see rubric).
7. **Scope notes:** input type, duration if known, what was not assessed.
8. Offer the full transcript or a corrected-structure outline on request; include the transcript only if asked or for audio input when short.

Do not send the report to the candidate or anyone else automatically; the requester decides delivery.
