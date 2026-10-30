# Example — Wells Fargo Mobile Banking (about 330 words)

Part 8 (AI) is illustrative: the source had no AI use, so a real script must carry `[confirm: tool and task]` until the candidate states it. Numbers in brackets are guideline part numbers, not spoken.

Hi, I'm a backend engineer with [confirm: years] years of experience building enterprise applications, mostly in financial services, especially consumer and mobile banking. (1)

Most recently I'm a contractor at Wells Fargo, on the Account Summary team of the Mobile Banking platform. My core job is migrating mobile banking features from a legacy codebase into independent microservices, and I owned the backend for Merchant Deals and the Open Account tile. The program overall cut API response time from about 1,500 ms to 150 ms. (2, 3, 5)

Some background. Account Summary, Merchant Deals and Offers all lived in one large legacy codebase, so features were tightly coupled, hard to deploy on their own, and some downstream calls were slow. (4)

The teams migrated in phases, starting with smaller features, running legacy and new services in parallel and shifting traffic gradually, with rollback always available. (5)

I joined in 2023. For Merchant Deals I built new endpoints and migrated the business logic for a subset of its seven or eight APIs over about six months, and those APIs are now served by the new microservice. Later, two backend engineers left my scrum team and I became the only backend engineer, so I took on day-to-day API work and coordination with the mobile teams, while my changes still went through the principal engineer's review. I also built the backend JSON for the server-driven Open Account tile, so the mobile app could render it dynamically, and I worked closely with the iOS, Android and QA teams to make sure our APIs met the app's needs. (6, 7)

[confirm: tool and task] For example: I use Copilot to draft unit tests and to explain unfamiliar legacy code before I change it. (8)

Two challenges I'm happy to go deeper on: keeping functional parity while the legacy app was still changing, and getting the core service ready for production traffic with enough test coverage for edge cases. (9)

Overall, I've gained solid experience in microservice migration, gradual rollouts and API development for mobile, and I want to keep growing in microservices and distributed systems. (10)
