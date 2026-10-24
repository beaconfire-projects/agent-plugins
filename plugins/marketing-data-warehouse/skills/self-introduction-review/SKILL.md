---
name: self-introduction-review
description: Score and coach a candidate's interview self-introduction (spoken audio or text) against Beaconfire's 10-part structure. Reports which parts are covered or missing, a part-by-part score, an overall score and band, objective evidence, and concrete fixes. Use when a Trainer or AM wants to check whether a candidate's self-introduction meets company standard. Requires a signed-in Beaconfire account.
allowed-tools:
  - mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__list_dimensions
---

# Self-introduction review (10-part standard)

Audience: Trainers and AMs only (not for candidates to self-check). Input: one candidate's self-introduction as an audio recording or as text. Output: an objective, evidence-based scorecard and improvement plan. Do not rewrite the candidate's story from scratch; judge what was actually said.

## Step 0 — Sign-in gate (always first)

Before reading the rubric or evaluating anything, call the read-only `list_dimensions` tool once (for example with `field: "round"`) from a connector of the **production** warehouse: a connector whose name is exactly `marketing-data-warehouse`. That is either this plugin's own connector (`plugin:marketing-data-warehouse:marketing-data-warehouse`; in Claude Code the tool is `mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__list_dimensions`) or a plain connector of the same exact name, as in the web app or Cowork, where tool identifiers may be opaque IDs and only the connector name tells them apart.

Environment separation: never use a connector whose name contains `-dev` (such as `marketing-data-warehouse-dev`), or any connector with another name, even if it exposes a tool named `list_dimensions`. When more than one connector qualifies, prefer this plugin's own. If you cannot tell which connector a tool belongs to, treat it as not matching. Do not stop merely because the connector is not plugin-scoped. Do not bypass the gate or change MCP configuration. The `allowed-tools` header only pre-approves the Claude Code tool name above; it does not make other tools unavailable. Use no other warehouse tools to enrich or verify the review; its evidence remains the supplied recording or text.

- Success: continue.
- No qualifying connector, authentication error, or any failure: stop. Tell the user this skill is for signed-in Beaconfire staff, ask them to authenticate the `marketing-data-warehouse` connector (via `/mcp` in Claude Code, or the connector settings in the app; in the web app the plugin must also be enabled), then retry. Do not score, summarize the rubric, or offer a partial review.

Never show the user the tool's output; the call only verifies sign-in.

## Step 1 — Input

- Accept audio (any format the environment can decode) or pasted/attached text. If neither is provided, ask only for the candidate's self-introduction.
- Do not ask for a JD, resume, or target role. Ask nothing else unless the input is unusable.
- Audio, local shell available (e.g. Claude Code or the desktop Code tab): first check for an installed transcriber (`mlx_whisper`, `whisper`) and `ffmpeg`, and use it if present. A tool shell often does not load the user's shell profile, so `command -v` alone can miss a working install: if `command -v` fails, also look in `~/Library/Python/*/bin`, `~/.local/bin`, and `/opt/homebrew/bin` (or run the check through `zsh -ic`) before concluding it is missing, and call it by its full path when found there. If missing, tell the user and ask before installing anything; never install silently. On Apple Silicon offer `brew install ffmpeg` and `uv tool install mlx-whisper` (isolated, no system Python changes), and warn that the first run downloads a ~1.5 GB model. On other machines `mlx_whisper` does not apply: suggest `faster-whisper` or `whisper.cpp`, or a pasted transcript. After installing, run it on the recording before scoring.
- Audio: transcribe with an available transcription capability, near-verbatim, with timestamps when offered; mark `[unclear]`; never fill gaps from an expected script. If the audio cannot be decoded or transcribed (for example this environment has no transcription tool, as in a web chat, or a shell exists but is sandboxed with no network so the speech model cannot be downloaded), treat it as having no transcription capability: do not guess or score from a template, and stop and reply in the requester's language with this guidance instead of a bare error:
  1. This environment cannot transcribe the audio, so it cannot be scored directly.
  2. Get a transcript elsewhere, and always name these options: a meeting tool's own transcript (Zoom, Otter, Feishu Minutes), or on the user's own Mac the command `mlx_whisper <file> --model mlx-community/whisper-large-v3-turbo --output-format txt` (needs ffmpeg). Give the CLI command, not a Python script, and do not name a specific Python version.
  3. Paste or attach the transcript with timestamps, and keep interviewer and candidate lines distinguishable. A transcript still gets a full structural score; only pace and delivery are "not assessed".
- If several speakers appear, evaluate only the candidate's prepared introduction. Prompted answers to interviewer follow-ups do not count toward coverage.
- Text input: delivery, pace and length-in-minutes are "not assessed" unless the user supplies the duration (about 130 spoken words per minute is a rough guide).

## Step 2 — Evaluate

Read `references/rubric.md` and follow it exactly: the 10 parts, per-part criteria, score levels, weights, bands, and hard checks. Key principles:

- Judge each part as **Covered / Partial / Missing** with evidence: a short quote (with timestamp when available) or an explicit "not found".
- Parts 1–5 are about the project; parts 6–10 are about the candidate. Penalize mixing them, going backwards in the narrative, and technology lists that replace business explanation.
- Team results must be credited to the team (part 5); the candidate's own result belongs in part 8. Flag any team result presented as personal.
- Challenges (part 9) should be 2–3 one-line hooks that invite questions, not full solutions.
- **Required AI element:** the introduction must say how the candidate uses AI in their own work (AI-based SDLC, copilot-assisted development, using AI to bootstrap development and testing, or ChatGPT/Claude/Gemini/Copilot doing a named task). Score it per the rubric. Building an AI product is not the same as using AI in one's work. If missing or weak, deduct and make it a priority fix: say it is required and give a spoken line using only stated facts, with `[confirm]` for the tool and task.
- Never invent facts, metrics, tools, ownership, or dates, and never penalize the candidate for experience they may have but did not say; say "not stated". Do not infer from accent or name.
- Be objective. Do not inflate scores to be encouraging; do not use a bare "good/bad" without evidence.

Coaching checks for the improvement advice (they feed the advice and the overall-quality row; they never add or remove parts):

- **Hook:** is there a concrete reason for the interviewer to ask the next question (a challenge, decision, tradeoff or outcome from the candidate's own work), specific, credible and early enough? Name the follow-up question it would invite. If weak or absent, suggest one or two natural spoken lines built only from facts the candidate stated; where a crucial fact is missing, say what to confirm first. No clickbait, exaggeration, or a teaser that hides the basic project summary.
- **Business first:** the setting and problem come before frameworks and platforms. For each named technology, check whether the candidate says what problem it solved or why it was used; a bare stack list explains nothing. Only recommend keywords the candidate's own account supports; never insert attractive terms the candidate did not say. Distinguish scale or reach (events per day, users) from a demonstrated outcome.
- **Ownership wording:** "I" for the candidate's real decisions and results, "we" for real team work. Flag repeated "we" only where it hides the candidate's contribution; never turn a team achievement into a solo one. Wording like "familiar with" vs "built/owned" signals different levels: suggest stronger verbs only when the account supports that level.
- **Spoken expression:** note comprehension problems (long lead-ins, chronology before the point, filler repetition, unexplained jargon, vague pronouns, abrupt transitions). Judge pace, pauses and natural flow only if the original audio or reliable acoustic observations are actually available; a transcript alone cannot show fluency, so mark delivery "not assessed". Ground feedback in specific moments, not accent or an assumption about non-native speech; code-switching is not an error by itself.

## Step 3 — Report

Write in the requester's language (default Chinese); keep quotes and sample wording in the language the candidate used. Use this order, concise and table-first:

1. **Verdict line:** total score /100, band, one-sentence reason.
2. **Part checklist table:** `# | Part | Status | Score | Evidence / what is missing`, all 10 parts plus the required-AI row and the overall-quality row.
3. **Covered vs missing:** two short lists.
4. **Strengths:** at most 3, each with evidence.
5. **Hard-check flags:** any that triggered (see rubric).
6. **Final improvement advice:** the closing section for the Trainer/AM to act on and pass to the candidate.
   - *Priority fixes:* 3–5 items ordered by score gain, each with what was heard (quote or timestamp), why it loses points, and a one-to-two-sentence spoken fix built only from facts the candidate stated (mark unknown facts `[confirm]`).
   - *Hook:* whether one exists, the follow-up question it invites, and a suggested line.
   - *Spoken expression:* wording and ownership issues; delivery marked "not assessed" when only a transcript was available.
   - *Re-recording checklist:* 3–5 short items the candidate can check before the next take.
7. **Scope notes:** input type, duration if known, what was not assessed.
8. Offer the full transcript or a corrected-structure outline on request; include the transcript only if asked or for audio input when short.

Do not send the report to the candidate or anyone else automatically; the requester decides delivery.
