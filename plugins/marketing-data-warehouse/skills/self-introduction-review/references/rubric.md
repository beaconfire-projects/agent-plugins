# Rubric — 2.5–3 minute, 10-part self-introduction

Source: `references/guideline.md` (parts, order, rules, timing tiers), plus a required, up-front AI element requested by the Trainer/AM team. Weights, score levels, bands and hard checks below are a **proposed scoring convention** layered on that guideline; the company has not defined official numeric weights. Revise this file when it does. The guideline is the standard; if this file and the guideline disagree, the guideline wins on content and order.

## Parts and weights (total 100)

Order follows the guideline: headline (1–3), AI highlight (4), expand (5–8), hooks (9), close (10).

| # | Part | Must cover | Weight |
|---|---|---|---|
| 1 | Who you are | Role, years of experience, industries or domains, **and an AI tagline** | 6 |
| 2 | Latest company and project | Company (one line on what it does if not well known), team, project | 6 |
| 3 | Core responsibility and headline result | What the candidate mainly does and what was delivered, in the headline | 10 |
| 4 | **Required: AI in your work** | How the candidate uses AI in their own work, placed right after the headline (see below) | 14 |
| 5 | Project background | Business problem, why the project existed, pain points and constraints | 6 |
| 6 | Approach and team result | Delivery method and risk control; overall result credited to the team | 6 |
| 7 | Your work | Join time, what was built, one representative feature, how ownership grew and where it stopped | 14 |
| 8 | Your result | A concrete result the candidate contributed to, tied to the representative feature | 8 |
| 9 | Challenges (2–3 hooks) | One line per challenge, inviting follow-up | 8 |
| 10 | Close | Skill keywords supported by the story and a direction | 6 |
| — | Timing and concision | See below | 8 |
| — | Overall quality | See below | 8 |

## Per-part score levels

Multiply the weight by the level:

- **Full (100%)**: required content clearly present, specific, in the right place, and said briefly.
- **Mostly (75%)**: present but thin or generic, or one required element missing.
- **Partial (50%)**: touched on vaguely, in the wrong place, or mixed into another part.
- **Minimal (25%)**: a passing mention that gives the listener nothing usable.
- **Missing (0%)**: not said.

Status mapping: Full/Mostly = Covered; Partial/Minimal = Partial; Missing = Missing.

Part-specific checks:

- 1: role, industry and years are named, plus an **AI tagline**: a clause saying the candidate is an engineer who works with AI (for example "a backend engineer who builds with AI across the development cycle"). Without the AI tagline, Mostly at best. No stack-list opening. A programming language or stack must be named only if the candidate really uses it; do not credit or require one.
- 2: company, team and project are named. For a company that is not well known, one line on what it does is expected; its absence means Mostly at best.
- 3: **the headline must stand on its own**: role, latest company, project, core responsibility and what was delivered, within roughly the first 40 seconds (about the first 100 words). If the core responsibility or deliverable only appears later, Partial at best. A metric is welcome but not required; do not penalize its absence.
- 4 (AI, required): the introduction must say how the candidate uses AI in their own work, for example AI-based SDLC, copilot-assisted development, or using ChatGPT, Claude, Gemini, Copilot or Cursor for specific work. It counts only if the candidate says it, not if the project merely is an AI product. Count the **stages** covered, from this list: writing or understanding code; writing tests; debugging; pull requests (descriptions, self-review of the diff, code review); checks (lint, CI, verifying a change); feature or technical design; documentation. Different tools for the same stage count as one stage.
  - Full: names the AI tool(s), covers **two or more stages**, says what it helped achieve or how the candidate checks AI output, **and sits right after the headline** (within about the first minute, before the project background).
  - Mostly: two or more stages but no effect and no check of the output; or one stage with a tool and a stated effect; or Full content that first appears after the project background but before the hooks.
  - Partial: one stage with only a tool and no effect; a generic claim ("I use AI tools", "familiar with AI"); AI mentioned only inside a technology list; or the first full mention comes only after the hooks. **The AI tagline in part 1 and a closing phrase such as "working AI-first" are not part 4 content**: a script that has only those has no stated AI practice and scores Partial at best, and the "no concrete AI practice" hard check applies.
  - Minimal: a passing keyword that gives the listener nothing usable.
  - Missing: no statement of using AI in their own work. Building an AI product or agent does not count by itself; note it as a project domain.
  - Should fit the work the candidate says they did on the project; an AI practice unrelated to the described work is flagged "needs verification".
  - If missing or weak: deduct as above, and the advice must say this element is required and up front, and give a spoken line that adds it and covers at least two stages, built only from stated facts with `[confirm]` for the tool and stages.
- 5: business problem and pain points come before implementation; constraints are named, not just "legacy".
- 6: states a delivery method and risk control (phasing, parallel run, rollback, testing), not a tool list. A team result must be credited to the team; a claim with no attribution gets at most Mostly.
- 7: gives join time, scope, one representative feature at business level, and a boundary (reviews, approvals, what the candidate did not own). Growth of ownership is credited when the story shows it, but it is not required. Missing join time or missing boundary is Mostly at best. Merely listing technologies is Partial at best. Unbounded solo claims get at most Mostly.
- 8: a concrete personal result tied to the representative feature. **Metrics are optional**: a clear outcome (what shipped, what changed) is enough for Full. A number counts only if the candidate says what it measures and what they did to affect it; an unexplained or unattributed number is flagged "needs verification" and is not credited as a personal result. A team result restated as personal is Partial and triggers the attribution flag.
- 9: 2–3 challenges, each one line, ending with an offer to go deeper. One challenge = Mostly at best; none = Missing; four or more, or full solution walkthroughs = Partial (hooks should not be exhausted). One AI-related hook is fine but not required.
- 10: skill keywords supported by the story plus a direction (AI-assisted engineering may be part of it); generic "hard-working" language does not count.

## Timing and concision (8)

Use the recording duration if known. For text, estimate duration as words ÷ 130 (leave out bracketed markers) and say it is an estimate.

| Length | Tier | Score |
|---|---|---|
| 2:30–3:00 | On target | 8 |
| 2:00–2:30 or 3:00–4:00 | Acceptable | 6 |
| 1:30–2:00 or 4:00–4:30 | Off target | 4 |
| Under 1:30 or over 4:30 | Fail | 0, and the hard check triggers |

Also note any part that runs far beyond its target words in the guideline (it crowds out others) as a concision comment; it does not change the tier.

## Overall quality (8)

Score 0–8:

- Order follows the guideline: headline, then AI, then expand, then hooks, then close, without going backwards (3).
- Project and personal content kept separate and team vs personal credit correct (2).
- Business first, with technology only where it explains value, and **AI as a highlight, not the whole story**: roughly 15–25% of the words. Above about 35% crowds out the project and loses this point (1).
- Natural and spoken rather than read (2). If delivery cannot be assessed from a transcript, award these sub-points proportionally from the assessable content and say so.

## Bands

| Total | Band | Meaning |
|---|---|---|
| 85–100 | Meets standard | Ready to use; polish only |
| 70–84 | Needs improvement | Structure mostly present; fix the listed gaps and re-record |
| 50–69 | Below standard | Several parts missing or weak; rework before client use |
| <50 | Not structured | Does not follow the guideline structure |

## Hard checks (flag; cap band at "Needs improvement" if any triggers)

- Part 3 (headline) missing entirely, or the headline is absent from the opening.
- Part 7 missing entirely.
- AI in your work missing entirely (part 4 scores 0), **or no concrete AI practice stated** (part 4 scores Partial or lower, for example only the part 1 tagline and a closing phrase, or a practice behind an unverified `[suggested]` marker).
- A team/program result presented as the candidate's own.
- Technology list used in place of project/business explanation in the opening or first half.
- Facts that appear invented or contradict themselves (flag as "needs verification"; do not accuse), including an AI practice or a language or stack the candidate would not plausibly have used given the described work.
- Duration under 1:30 or over 4:30 (measured, or estimated from words).

## Scoring discipline

- Score only what was said. Evidence required for every score above 0.
- Round part scores to the nearest whole number; the total is their sum.
- Do not add or remove parts for the candidate's background; all 10 apply to every self-introduction.
- The candidate speaks English; quote evidence in English. Do not penalize accent, name or non-native phrasing; judge structure and content.
