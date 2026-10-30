# Interview Self-Introduction Guideline

Audience: Trainers, AMs and candidates. This is the single standard for how Beaconfire candidates introduce themselves in an interview. The generate skill writes to it and the review skill scores against it.

## 1. Goal and length

The self-introduction is the first thing an interviewer hears. In **2.5–3 minutes** it must answer: who is this person, what did they do recently, what is their real contribution, and what should I ask next?

- Spoken English, natural, not read from a script.
- About 130 spoken words per minute: **325–390 words** is on target.
- Answer first, details second. The first 30–40 seconds must already tell the interviewer your role, latest project, core responsibility and what you delivered.

## 2. The shape

| Stage | Time | Purpose |
|---|---|---|
| A. Headline | 30–40 s | The whole story in brief: who you are, where you work, what you own, what you delivered |
| B. Expand | 1.5–2 min | Evidence for the headline: project background, approach, your work, your result, AI |
| C. Hooks | 20–30 s | 2–3 challenges that invite follow-up questions |
| D. Close | 15 s | Skill keywords and the direction you want to grow in |

## 3. The 10 parts

| # | Part | What to say | Target words |
|---|---|---|---|
| 1 | Who you are | Role, years of experience, industries or domains | ~20 |
| 2 | Latest company and project | Company (add one line on what it does if it is not well known), team or department, project | ~30 |
| 3 | Core responsibility and headline result | What you are mainly responsible for and what you delivered, in one or two sentences | ~35 |
| 4 | Project background | The business problem the system solves, why the project existed, the pain points and constraints | ~45 |
| 5 | Approach and team result | How the team delivered and controlled risk (phasing, parallel run, rollback, testing). The overall result, credited to the team | ~45 |
| 6 | Your work | When you joined, what you built, one representative feature explained in business terms, how your ownership grew and where it stopped (reviews, approvals, what you did not own) | ~60 |
| 7 | Your result | A concrete result you contributed to, tied to your representative feature | ~30 |
| 8 | AI in your work | How you use AI in your own work: the tool, the task, and what it helped with | ~25 |
| 9 | Challenges (2–3 hooks) | One line per challenge, each inviting a follow-up | ~40 |
| 10 | Close | Skill keywords supported by your story and the direction you want to go next | ~25 |

Parts 1–3 are the headline and come first. Parts 4–8 expand it. Parts 9–10 close.

## 4. Rules

1. **Business first.** Say what the system does for the business before naming technology. Never open with a list of tools.
2. **Credit correctly.** Team or program results are the team's. Say so. Your own result goes in part 7. Never present a team result as yours.
3. **Metrics are optional.** Use a number only if you can explain how it was measured and what you did to affect it. A junior engineer who cannot defend a number should describe the concrete outcome instead (what shipped, what changed, what stopped hurting). An interviewer will dig into any number you give.
4. **Hooks are hooks.** Each challenge is one line: what the problem was and why it was hard. Do not give the solution; leave it for the interviewer to ask.
5. **AI is required.** Say how you use AI in your own work (for example AI-assisted coding, tests, debugging, design or review with a named tool). Building an AI product is not the same thing.
6. **Do not go backwards.** Headline first, then expand, then hooks, then close. Do not return to background after you start talking about your work.
7. **No invention.** Say only what is true and what you can discuss in depth. Do not add terms you cannot defend.
8. **Technology belongs to your work.** Mention a technology where it explains what you did or why it mattered, not as a list.

## 5. Timing tiers

The review skill applies the same tiers.

| Length | Tier | Effect |
|---|---|---|
| 2:30–3:00 | On target | No deduction |
| 2:00–2:30 or 3:00–4:00 | Acceptable | Minor deduction |
| 1:30–2:00 or 4:00–4:30 | Off target | Larger deduction |
| Under 1:30 or over 4:30 | Fail | Hard-check flag, band capped |

For text with no recording, estimate time as words ÷ 130: on target is about 325–390 words, acceptable about 260–520, off target about 195–585.

## 6. Example (about 330 words)

Based on a Wells Fargo mobile banking migration. Part 8 is illustrative: a real candidate must say their own practice.

> Hi, I'm a backend engineer with [X] years of experience building enterprise applications, mostly in financial services, especially consumer and mobile banking. *(1)*
>
> Most recently I'm a contractor at Wells Fargo, on the Account Summary team of the Mobile Banking platform. My core job is migrating mobile banking features from a legacy codebase into independent microservices, and I owned the backend for Merchant Deals and the Open Account tile. The program overall cut API response time from about 1,500 ms to 150 ms. *(2, 3, 5)*
>
> Some background. Account Summary, Merchant Deals and Offers all lived in one large legacy codebase, so features were tightly coupled, hard to deploy on their own, and some downstream calls were slow. *(4)*
>
> The teams migrated in phases, starting with smaller features, running legacy and new services in parallel and shifting traffic gradually, with rollback always available. *(5)*
>
> I joined in 2023. For Merchant Deals I built new endpoints and migrated the business logic for a subset of its seven or eight APIs over about six months, and those APIs are now served by the new microservice. Later, two backend engineers left my scrum team and I became the only backend engineer, so I took on day-to-day API work and coordination with the mobile teams, while my changes still went through the principal engineer's review. I also built the backend JSON for the server-driven Open Account tile, so the mobile app could render it dynamically, and I worked closely with the iOS, Android and QA teams to make sure our APIs met the app's needs. *(6, 7)*
>
> *[Illustrative]* I use Copilot to draft unit tests and to explain unfamiliar legacy code before I change it. *(8)*
>
> Two challenges I'm happy to go deeper on: keeping functional parity while the legacy app was still changing, and getting the core service ready for production traffic with enough test coverage for edge cases. *(9)*
>
> Overall, I've gained solid experience in microservice migration, gradual rollouts and API development for mobile, and I want to keep growing in microservices and distributed systems. *(10)*

## 7. Self-check before you speak

- [ ] Within the first 40 seconds I said my role, latest company, project, core responsibility and what I delivered.
- [ ] I explained the business problem before any technology.
- [ ] Team results are credited to the team; my own result is separate.
- [ ] Any number I used, I can explain and defend.
- [ ] I said how I use AI in my own work.
- [ ] I have 2–3 one-line challenges, with no solutions.
- [ ] I ended with skills and a direction.
- [ ] It runs 2.5–3 minutes when spoken aloud.
