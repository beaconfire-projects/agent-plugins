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
5. If key facts are missing, ask once, in one short batch, for only those facts. If the user cannot supply them, continue and mark each gap `[confirm: ...]` in the script. Never invent a fact to fill a gap.

## Step 2 — Draft

Follow the guideline's shape: headline (parts 1–3) → expand (4–8) → hooks (9) → close (10).

- **Headline first.** Within about 40 seconds the listener knows the role, latest company, project, core responsibility and what was delivered. If the company is not well known, add one line on what it does.
- **Business before technology.** Never open with a stack list. Name a technology only where it explains what the candidate did or why it mattered.
- **Credit correctly.** Team or program results are credited to the team. The candidate's own result belongs in part 7. Never turn a team result into a personal one unless the source clearly attributes it to the candidate.
- **Metrics are optional.** Use a number only if the source supports it and the candidate could explain it. Do not add or round up numbers. If there is no defensible number, describe the concrete outcome instead.
- **Ownership.** Say when the candidate joined, what they built, one representative feature in business terms, how ownership grew (only if the source shows it) and where it stopped.
- **AI is required.** Say how the candidate uses AI in their own work, using only what the candidate stated: the tool, the task and what it helped with. Building an AI product does not count. If it is not stated, write the line with `[confirm: tool and task]` and flag it in the note; never invent a tool or task.
- **Hooks.** Two or three challenges, one line each, what the problem was and why it was hard, ending with an offer to go deeper. No solutions.
- **Close.** Skill keywords the story supports and the direction the candidate wants to grow in. No generic "hard-working" language.
- **Spoken English.** First person, short and medium sentences, natural paragraph breaks, the candidate's own terminology. No section labels, numbers or headings in the script. No source-language such as "according to the resume".
- **Do not go backwards.** Once the candidate's own work starts, do not return to add project background.

Length: 325–390 words (about 2.5–3 minutes at 130 words per minute). If over, cut in this order: minor features, implementation detail, repeated background, generic wording. Never cut the headline, the candidate's scope, a clear result, the AI line or the hooks. If under 325, add concrete detail from the source, not filler.

## Step 3 — Self-check (not a score)

Before returning, check against the guideline's self-check list and the hard checks used by self-introduction-review: headline in the first 40 seconds; no stack-list opening; team vs personal credit correct; AI line present; 2–3 one-line hooks; no unsupported facts; word count in range; no going backwards. Fix problems before showing the script.

## Step 4 — Output

1. The script as plain paragraphs in the message.
2. Save it as a Markdown file (`self-introduction-<candidate>.md`) in the working directory when file writing is available; otherwise say it can be copied from the message.
3. A short note for the Trainer/AM, in the requester's language (default Chinese), covering: word count and estimated time; every `[confirm]` item to settle with the candidate; facts left out because the source did not support them; anything the candidate may be asked to defend (numbers, tools).
4. Mention that once the candidate has practiced the script, `self-introduction-review` can score the recording or transcript.

Do not send the script to the candidate or anyone else automatically; the requester decides delivery.

See `examples/` for reference-quality scripts.
