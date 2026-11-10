# Example — Walmart Fulfillment (about 345 words)

Join date, years and the review process were not in the source, so they carry `[confirm]`; AI use was not in the source either, so part 4 carries a `[suggested]` proposal built from the allocation and reservation work, to be verified with the candidate. Numbers in brackets are guideline part numbers, not spoken.

Hi, I'm Harvey, a backend engineer who builds with AI across the development cycle, with [confirm: years] years of experience, mostly in logistics and fulfillment. (1)

Most recently I worked on Walmart Fulfillment Services, on Inbound Inventory Planning. My core job was backend development for Allocation and Capacity, the services that decide which fulfillment centers receive a seller's inventory and how much each can take. One result I contributed to was taking Capacity V3 into production without affecting existing V2 consumers. (2, 3)

[suggested: confirm you really do this] On the AI side, I use Claude to draft test cases for allocation and reservation scenarios, such as retries and concurrent requests, and to review my changes for race conditions before opening a PR. I run those tests against the real logic, so AI output is a draft I verify. (4)

When third-party sellers send goods into Walmart's fulfillment network, the system chooses the fulfillment centers under routing rules and weekly capacity limits for each program. The business needed richer cases like box-level and two-tier allocation while consumers were already live on the V2 APIs. (5)

So the team used versioned APIs: keep the V2 contract, add V3, and let each workflow migrate at its own pace. (6)

[confirm: join date] On Allocation, I worked on API and business logic for box-level allocation, custom break-pack and two-tier allocation. On Capacity, I worked mostly on V3: the APIs, the data model and the reservation flow, plus database and performance optimization, metrics, alerts and production troubleshooting. My ownership stayed focused on these features [confirm: review and approval process]. (7)

One flow that processes multiple items took about 30 seconds. By replacing repeated database lookups with batch fetches and reusing the data already fetched, I helped bring it under 2 seconds. (8)

Three challenges I'm happy to go deeper on: keeping V3 backward compatible with live V2 consumers while requirements were still inconsistent; making capacity reservations correct under retries and concurrency across several fulfillment centers; and troubleshooting production slowness. (9)

Overall, I've worked on API versioning, idempotency, concurrency, performance and production troubleshooting, and I want to keep growing in backend, distributed and data-intensive systems, working AI-first. (10)
