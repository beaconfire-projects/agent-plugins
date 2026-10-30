# Example — Walmart Fulfillment (about 340 words)

Join date, years, the review process and AI use were not in the source, so they carry `[confirm]`. Numbers in brackets are guideline part numbers, not spoken.

Hi, I'm Harvey, a backend engineer with [confirm: years] years of experience building enterprise and distributed systems, mostly in logistics and fulfillment. (1)

Most recently I worked on Walmart Fulfillment Services, on the Inbound Inventory Planning team. My core job was backend development for Allocation and Capacity, the services that decide which fulfillment centers receive a seller's inventory and how much each one can take. One result I contributed to was taking Capacity V3 into production without affecting existing V2 consumers. (2, 3)

Some background. When third-party sellers send goods into Walmart's fulfillment network, the system has to choose the right fulfillment centers under routing rules and weekly capacity limits for each program. The business needed more complex cases, like box-level and two-tier allocation, but existing consumers were already live on the V2 APIs. (4)

So the team used versioned APIs: keep the V2 contract, add V3, and let each workflow migrate at its own pace. (5)

[confirm: join date] On Allocation, I built API and business logic for box-level allocation, custom break-pack and two-tier allocation. On Capacity, I focused on V3: the APIs, the data model and the reservation flow. I also worked on database and performance optimization, metrics, alerts and production troubleshooting. My ownership stayed focused on these features [confirm: review and approval process]. (6)

One flow that processes multiple items took about 30 seconds. By replacing repeated database lookups with batch fetches and reusing the data already fetched, I helped bring it under 2 seconds. (7)

[confirm: tool and task] For example: I use Claude to generate test cases for new reservation scenarios. (8)

Three challenges I'm happy to go deeper on: keeping V3 backward compatible with live V2 consumers while requirements were still inconsistent; making capacity reservations correct under retries and concurrency across several fulfillment centers; and troubleshooting production slowness. (9)

Overall, I've worked on API versioning, idempotency, concurrency, performance and production troubleshooting, and I want to keep growing in backend, distributed and data-intensive systems. (10)
