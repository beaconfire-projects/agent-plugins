# Example — Wells Fargo Mobile Banking (about 370 words)

Part 4 (AI) was not in the source, so the script carries a `[suggested: confirm you really do this]` proposal built from the candidate's real project work, to be verified with the candidate before use. Years were not in the source either. Numbers in brackets are guideline part numbers, not spoken.

Hi, I'm a backend engineer who builds with AI across the development cycle, with [confirm: years] years of experience, most recently in consumer and mobile banking. (1)

At Wells Fargo, I'm on the Mobile Banking platform's Account Summary team, which owns the account overview screen. My core job is backend development and migrating features from a legacy codebase into microservices: I migrated part of the Merchant Deals APIs and contributed to Offers and the Open Account tile. Overall, the program cut Account Summary response time from about 1,500 ms to about 150 ms, a joint effort across several teams. (2, 3)

[suggested: confirm you really do this] On the AI side, I use Claude to understand legacy code before migrating it, to draft tests that compare new endpoints with legacy behavior, and to review my own diff before a PR. I treat its output as a draft and verify it with those tests. (4)

Some background. Account Summary, Merchant Deals and Offers all lived in one large legacy codebase from around 2012, which made independent deployment hard, and slow downstream calls made the overview slow to open. (5)

Since 2021 the teams have migrated in phases, core Account Summary last, running legacy and new services in parallel, moving traffic by user group, with rollback to legacy. The core service took production traffic in July 2026. (6)

I joined in May 2023. Merchant Deals lets customers browse and activate merchant offers in the app; of its seven or eight APIs I migrated the business logic for some, then our team added caching and rolled it out gradually, about six months end to end. I also contributed backend logic and JSON for the server-driven Open Account tile. After two engineers left, I became the only backend engineer, handling day-to-day API work and coordination with iOS, Android and QA, while my code still went through Principal Engineer review. (7)

The Merchant Deals APIs I migrated now serve live traffic from the new microservice. (8)

Two things I'm happy to go deeper on: keeping the new service in sync while the legacy app kept changing, and getting the core service production-ready with enough corner-case testing. (9)

Overall, I've built experience in legacy modernization, gradual rollouts and mobile backend support, and I want to keep growing in backend and distributed systems, working AI-first. (10)
