---
name: self-introduction-generate
description: Generate a 2.5–3 minute spoken English interview self-introduction for a candidate from their resume, project story or notes, following Beaconfire's 10-part guideline (headline first, then project, own work, AI use, hooks, close). Use when a Trainer or AM wants a self-introduction script drafted for a candidate. To score an existing self-introduction use self-introduction-review instead. Requires a signed-in Beaconfire account.
allowed-tools:
  - mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__list_dimensions
---

# Self-introduction generate (2.5–3 minutes, answer first)

Audience: Trainers and AMs only. Input: a candidate's resume, project story, interview notes or statements. Output: an English spoken script of 325–390 words that follows `references/guideline.md`, plus a short note for the Trainer/AM. This is an oral script, not a resume summary and not a project report.

## Step 0 — Sign-in gate (always first)

Call the read-only `list_dimensions` tool once (for example with `field: "round"`) from a connector of the **production** warehouse: a connector whose name is exactly `marketing-data-warehouse`. That is either this plugin's own connector (`plugin:marketing-data-warehouse:marketing-data-warehouse`; in Claude Code the tool is `mcp__plugin_marketing-data-warehouse_marketing-data-warehouse__list_dimensions`) or a plain connector of the same exact name, as in the web app or Cowork, where tool identifiers may be opaque IDs and only the connector name tells them apart.

Never use a connector whose name contains `-dev`, or any connector with another name, even if it exposes `list_dimensions`. If you cannot tell which connector a tool belongs to, treat it as not matching. Do not bypass the gate or change MCP configuration. Use no other warehouse tools; the only evidence for the script is the supplied material.

- Success: continue. Never show the tool's output; the call only verifies sign-in.
- Failure of any kind: stop. Tell the user this skill is for signed-in Beaconfire staff, ask them to authenticate the `marketing-data-warehouse` connector (via `/mcp` in Claude Code, or the connector settings in the app; in the web app the plugin must also be enabled), then retry. Do not draft anything.

## Step 1 — Gather the facts

1. Read `references/guideline.md`. It is the standard; follow it exactly.
2. Accept resume text, project story, interview notes or the user's own statements. If nothing usable is given, ask only for the candidate's experience.
3. Use the candidate's **most recent** project unless the user names another. Do not use outside knowledge about the company or the industry.
4. Sort the material into the 10 parts and list what is missing. The parts most often missing are: years of experience, join date, the candidate's own result, how the candidate uses AI, and the ownership boundary (reviews, approvals, what they did not own).
5. If key facts are missing, ask once, in one short batch, for only those facts. If the user cannot supply them, continue and mark each gap `[confirm: ...]` in the script. Never invent a fact to fill a gap. The one exception is the AI part (see item 6 and Step 2), where a clearly marked proposal is allowed.
6. **AI question (always check it).** Unless the source already covers at least two stages, include this in the batch: which AI tools the candidate uses (Claude, ChatGPT, Copilot, Cursor, Gemini …) and for which of these stages: writing or understanding code, tests, debugging, PRs (descriptions, self-review, code review), checks (lint, CI, verifying a change), feature design, docs; plus one concrete thing it helped with. If the candidate or requester cannot say, do not leave the part empty: write a proposal as described in Step 2.

## Step 2 — Draft

Follow the guideline's shape: headline (parts 1–3) → AI highlight (4) → expand (5–8) → hooks (9) → close (10).

- **Headline first, with an AI tagline.** Within about 40 seconds the listener knows the role, latest company, project, core responsibility and what was delivered. Part 1 carries a one-clause AI tagline in the candidate's real role, for example "a backend engineer who builds with AI across the development cycle". Name a language or stack (for example Java) only if the source says the candidate uses it. If the company is not well known, add one line on what it does.
- **Business before technology.** Never open with a stack list. Name a technology only where it explains what the candidate did or why it mattered.
- **Credit correctly.** Team or program results are credited to the team. The candidate's own result belongs in part 8. Never turn a team result into a personal one unless the source clearly attributes it to the candidate.
- **Metrics are optional.** Use a number only if the source supports it and the candidate could explain it. Do not add or round up numbers. If there is no defensible number, describe the concrete outcome instead.
- **Match the verb to the source.** "Participated in" or "worked on" in the source becomes "contributed to" or "worked on", not "owned" or "built". Credit the team for what the team did (caching, rollout, go-live) even inside a sentence about the candidate's own work. Say nothing about earlier career or industry history that the source does not contain; use `[confirm: ...]`.
- **Ownership.** Say when the candidate joined, what they built, one representative feature in business terms, how ownership grew (only if the source shows it) and where it stopped.
- **AI is required, up front, across at least two stages.** Put the AI tagline in part 1 and the full AI part (part 4, about 45 words, 2–3 short sentences) **right after the headline and before the project background**: the tool, at least two stages (code, tests, debugging, PRs, checks such as lint/CI/verification, design, docs), how the candidate checks the AI output (for example with tests or review) and what it helped with. Building an AI product does not count.
  - **Take the practice from this project's real work, whatever the domain** (banking migration, logistics and warehousing, e-commerce and so on): for example tests for the allocation or reservation rules the candidate worked on, understanding legacy code before migrating it, checking a diff before a PR.
  - **AI is a highlight, not the whole story**: about 15–25% of the words in total, namely the tagline, part 4, at most one short mention inside the candidate's own work, and a phrase in the close. Add an AI-related hook only if the source itself supports it; never add one as a proposal. Everything else is the project and the candidate's contribution.
  - If the source or the requester states it, use exactly what was stated.
  - If it is not stated and cannot be obtained, **write a proposal instead of leaving the part empty**: pick at least two stages that fit work the candidate really did on this project, use a common tool (Claude, ChatGPT or Copilot), name one way to check the output and one plausible, modest effect. Do not invent metrics, time savings or results.
  - The tagline alone never satisfies the AI requirement: the script always needs the concrete part 4.
  - **Markers: one per proposal, at the start of the part 4 paragraph, never inside a sentence.** If part 4 is a proposal, begin that paragraph with `[suggested: confirm you really do this]`. Write the part 1 tagline, any short AI mention in the candidate's own work and the phrase in the close as plain text without markers: they depend on the part 4 proposal, and the Trainer note lists them as to be verified together with it. A proposal must never be presented as a confirmed fact, and the candidate must be able to discuss it in depth, because the interviewer will ask about it first.
- **Hooks.** Two or three challenges, one line each, what the problem was and why it was hard, ending with an offer to go deeper. No solutions.
- **Close.** Skill keywords the story supports and the direction the candidate wants to grow in. No generic "hard-working" language.
- **Spoken English.** First person, short and medium sentences, natural paragraph breaks, the candidate's own terminology. No section labels, numbers or headings in the script. No source-language such as "according to the resume".
- **Do not go backwards.** Once the candidate's own work starts, do not return to add project background.

Length: 325–390 words (about 2.5–3 minutes at 130 words per minute). If over, cut in this order: minor features, implementation detail, repeated background, generic wording. Never cut the headline, the candidate's scope, a clear result, the AI line or the hooks. Count the words of the spoken script without the text inside `[...]` markers, and count a `[confirm: ...]` placeholder as one word. If under 325, add concrete detail from the source, not filler. Keep AI within about 15–25% of the words when trimming or adding.

## Step 3 — Self-check (not a score)

Before returning, check against the guideline's self-check list and the hard checks used by self-introduction-review: headline in the first 40 seconds; no stack-list opening; team vs personal credit correct; AI tagline in part 1 and AI part right after the headline (stated, or a marked proposal), AI roughly 15–25% of the words; 2–3 one-line hooks; no unsupported facts; word count in range; no going backwards. Fix problems before showing the script.

## Step 4 — Output

1. The script as plain paragraphs in the message.
2. Save it as a Markdown file (`self-introduction-<candidate>.md`) in the working directory when file writing is available; otherwise say it can be copied from the message.
3. A short note for the Trainer/AM, in the requester's language (default Chinese), covering: word count and estimated time; every `[confirm]` item to settle with the candidate; every `[suggested]` AI proposal together with the unmarked AI tagline and closing phrase that depend on it, which the Trainer/AM must verify with the candidate (the candidate should really use these practices and be ready for follow-up questions) and from which the marker must be removed before the script is used or sent to `self-introduction-review`; facts left out because the source did not support them; anything the candidate may be asked to defend (numbers, tools).
4. Mention that once the candidate has practiced the script, `self-introduction-review` can score the recording or transcript.

Do not send the script to the candidate or anyone else automatically; the requester decides delivery.

See `examples/` for reference-quality scripts.
