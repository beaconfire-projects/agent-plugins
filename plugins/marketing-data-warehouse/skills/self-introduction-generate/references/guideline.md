# Interview Self-Introduction Guideline

Audience: Trainers, AMs and candidates. This is the single standard for how Beaconfire candidates introduce themselves in an interview. The generate skill writes to it and the review skill scores against it.

## 1. Goal and length

The self-introduction is the first thing an interviewer hears. In **2.5–3 minutes** it must answer: who is this person, what did they do recently, how do they work with AI, what is their real contribution, and what should I ask next?

- Spoken English, natural, not read from a script.
- About 130 spoken words per minute: **325–390 words** is on target.
- Answer first, details second. The first 30–40 seconds must already tell the interviewer your role, latest project, core responsibility and what you delivered. Within about the first minute they must also hear how you use AI.

The positioning is an **engineer who works with AI**, not an engineer who happens to have tried a chatbot. This applies to any project, whether it is banking, logistics or anything else: the AI practice is taken from the work the candidate really did on that project.

## 2. The shape

| Stage | Time | Purpose |
|---|---|---|
| A. Headline | 30–40 s | The whole story in brief: who you are (with an AI tagline), where you work, what you own, what you delivered |
| A+. AI highlight | 15–20 s | How you use AI in your own work, right after the headline |
| B. Expand | 1–1.5 min | Evidence for the headline: project background, approach, your work, your result |
| C. Hooks | 20–30 s | 2–3 challenges that invite follow-up questions |
| D. Close | 15 s | Skill keywords and the direction you want to grow in |

## 3. The 10 parts

| # | Part | What to say | Target words |
|---|---|---|---|
| 1 | Who you are | Role, years of experience, industries or domains, **plus an AI tagline** (for example "a backend engineer who builds with AI across the development cycle") | ~25 |
| 2 | Latest company and project | Company (add one line on what it does if it is not well known), team or department, project | ~30 |
| 3 | Core responsibility and headline result | What you are mainly responsible for and what you delivered, in one or two sentences | ~35 |
| 4 | **AI in your work** | Right after the headline: name the tool, cover **at least two stages** of development (see rule 5), say how you verify AI output and what it helped with | ~45 |
| 5 | Project background | The business problem the system solves, why the project existed, the pain points and constraints | ~35 |
| 6 | Approach and team result | How the team delivered and controlled risk (phasing, parallel run, rollback, testing). The overall result, credited to the team | ~35 |
| 7 | Your work | When you joined, what you built, one representative feature explained in business terms, how your ownership grew and where it stopped (reviews, approvals, what you did not own) | ~60 |
| 8 | Your result | A concrete result you contributed to, tied to your representative feature | ~30 |
| 9 | Challenges (2–3 hooks) | One line per challenge, each inviting a follow-up. One may be about AI, for example how you verify AI-generated code | ~40 |
| 10 | Close | Skill keywords supported by your story and the direction you want to go next. AI-assisted engineering may be part of that direction | ~25 |

Parts 1–3 are the headline and come first. Part 4 is the AI highlight and follows immediately. Parts 5–8 expand. Parts 9–10 close.

## 4. Rules

1. **Business first.** Say what the system does for the business before naming technology. Never open with a list of tools.
2. **Credit correctly.** Team or program results are the team's. Say so. Your own result goes in part 8. Never present a team result as yours.
3. **Metrics are optional.** Use a number only if you can explain how it was measured and what you did to affect it. A junior engineer who cannot defend a number should describe the concrete outcome instead (what shipped, what changed, what stopped hurting). An interviewer will dig into any number you give.
4. **Hooks are hooks.** Each challenge is one line: what the problem was and why it was hard. Do not give the solution; leave it for the interviewer to ask.
5. **AI is required, up front, across at least two stages.** Put an AI tagline in part 1 and the full AI part right after the headline (part 4). Name the tool (Claude, ChatGPT, Copilot, Cursor, Gemini and so on) and cover at least two of these stages:
   - writing code or understanding existing code;
   - writing tests;
   - debugging;
   - pull requests: descriptions, self-review of your diff, code review;
   - checks: lint, CI, verifying that a change works;
   - feature or technical design;
   - documentation.

   Say what you do to check AI output (for example tests, review) and what it helped with. Take the stages from work you really did on this project. One tool for one stage is thin; building an AI product is not the same thing.
6. **AI is a highlight, not the whole story.** AI should be roughly 15–25% of the words: the tagline, part 4, at most one short mention inside your work, optionally one hook, and a phrase in the close. The rest is the project and your contribution.
7. **Do not go backwards.** Headline, then AI, then expand, then hooks, then close. Do not return to background after you start talking about your work.
8. **No invention.** Say only what is true and what you can discuss in depth, especially about AI: the interviewer will ask about it first. Do not name a language or stack you did not use.
9. **Technology belongs to your work.** Mention a technology where it explains what you did or why it mattered, not as a list.

## 5. Timing tiers

The review skill applies the same tiers.

| Length | Tier | Effect |
|---|---|---|
| 2:30–3:00 | On target | No deduction |
| 2:00–2:30 or 3:00–4:00 | Acceptable | Minor deduction |
| 1:30–2:00 or 4:00–4:30 | Off target | Larger deduction |
| Under 1:30 or over 4:30 | Fail | Hard-check flag, band capped |

For text with no recording, estimate time as words ÷ 130: on target is about 325–390 words, acceptable about 260–520, off target about 195–585.

## 6. Example (about 370 words)

Based on a Wells Fargo mobile banking migration. Part 4 is illustrative: a real candidate must say their own practice, taken from their own work.

> Hi, I'm a backend engineer who builds with AI across the development cycle, with [X] years of experience, most recently in consumer and mobile banking. *(1)*
>
> At Wells Fargo, I'm on the Mobile Banking platform's Account Summary team, which owns the account overview screen. My core job is backend development and migrating features from a legacy codebase into microservices: I migrated part of the Merchant Deals APIs and contributed to Offers and the Open Account tile. Overall, the program cut Account Summary response time from about 1,500 ms to about 150 ms, a joint effort across several teams. *(2, 3)*
>
> *[Illustrative]* On the AI side, I use Claude to understand legacy code before migrating it, to draft tests that compare new endpoints with legacy behavior, and to review my own diff before a PR. I treat its output as a draft and verify it with those tests. *(4)*
>
> Some background. Account Summary, Merchant Deals and Offers all lived in one large legacy codebase from around 2012, which made independent deployment hard, and slow downstream calls made the overview slow to open. *(5)*
>
> Since 2021 the teams have migrated in phases, core Account Summary last, running legacy and new services in parallel, moving traffic by user group, with rollback to legacy. The core service took production traffic in July 2026. *(6)*
>
> I joined in May 2023. Merchant Deals lets customers browse and activate merchant offers in the app; of its seven or eight APIs I migrated the business logic for some, then our team added caching and rolled it out gradually, about six months end to end. I also contributed backend logic and JSON for the server-driven Open Account tile. After two engineers left, I became the only backend engineer, handling day-to-day API work and coordination with iOS, Android and QA, while my code still went through Principal Engineer review. *(7)*
>
> The Merchant Deals APIs I migrated now serve live traffic from the new microservice. *(8)*
>
> Two things I'm happy to go deeper on: keeping the new service in sync while the legacy app kept changing, and getting the core service production-ready with enough corner-case testing. *(9)*
>
> Overall, I've built experience in legacy modernization, gradual rollouts and mobile backend support, and I want to keep growing in backend and distributed systems, working AI-first. *(10)*

## 7. Self-check before you speak

- [ ] My opening sentence says I am an engineer who works with AI.
- [ ] Within the first 40 seconds I said my role, latest company, project, core responsibility and what I delivered.
- [ ] Within the first minute I said how I use AI: the tool, at least two stages, and how I check its output.
- [ ] My AI practice comes from work I really did, and I can answer follow-up questions about it.
- [ ] I explained the business problem before any technology.
- [ ] Team results are credited to the team; my own result is separate.
- [ ] Any number I used, I can explain and defend.
- [ ] AI is about a fifth of the introduction, not all of it.
- [ ] I have 2–3 one-line challenges, with no solutions.
- [ ] I ended with skills and a direction.
- [ ] It runs 2.5–3 minutes when spoken aloud.
