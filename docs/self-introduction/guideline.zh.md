# 面试自我介绍指南（中文版）

> 本文是 `guideline.en.md` 的中文对照版，仅供阅读。标准以英文版为准，两者有出入时请告知，以便同步修正。

适用对象：Trainer、AM 和学员。这是 Beaconfire 学员面试自我介绍的唯一标准：生成 skill 按它写稿，评审 skill 按它打分。

## 1. 目标和时长

自我介绍是面试官听到的第一段内容。要在 **2.5–3 分钟**内回答：这个人是谁、最近做了什么、真正的贡献是什么、我接下来该问什么。

- 用英文口语，自然表达，不照稿念。
- 约每分钟 130 个英文单词：**325–390 词**为合适长度。
- 结论先行，细节在后。前 30–40 秒就要让面试官知道你的角色、最近的项目、核心职责和交付了什么。

## 2. 整体结构

| 阶段 | 时间 | 作用 |
|---|---|---|
| A. 开场结论 | 30–40 秒 | 先把整个故事讲个大概：你是谁、在哪工作、负责什么、交付了什么 |
| B. 展开 | 1.5–2 分钟 | 为开场结论提供证据：项目背景、整体思路、你做的事、你的成果、AI |
| C. 钩子 | 20–30 秒 | 2–3 个挑战，引导面试官追问 |
| D. 收尾 | 15 秒 | 技术关键词和想发展的方向 |

## 3. 10 个部分

| # | 部分 | 要说什么 | 目标词数 |
|---|---|---|---|
| 1 | 你是谁 | 角色、年限、行业或领域 | ~20 |
| 2 | 最近的公司和项目 | 公司（不出名就补一句它是做什么的）、团队或部门、项目 | ~30 |
| 3 | 核心职责和开场成果 | 你主要负责什么、交付了什么，一两句话 | ~35 |
| 4 | 项目背景 | 系统解决什么业务问题、为什么要做这个项目、痛点和约束 | ~45 |
| 5 | 整体思路和团队成果 | 团队怎么交付、怎么控制风险（分阶段、并行运行、回滚、测试）；整体成果，归属于团队 | ~45 |
| 6 | 你的工作 | 什么时候加入、做了什么、一个用业务语言解释的代表性功能、你的所有权如何扩大、边界在哪（评审、审批、你不负责的部分） | ~60 |
| 7 | 你的成果 | 你参与的一个具体成果，和代表性功能挂钩 | ~30 |
| 8 | 工作中使用 AI | 你在自己的工作中怎么用 AI：哪个工具、做什么任务、带来什么帮助 | ~25 |
| 9 | 挑战（2–3 个钩子） | 每个挑战一句话，引导追问 | ~40 |
| 10 | 收尾 | 有故事支撑的技术关键词，以及下一步想去的方向 | ~25 |

第 1–3 部分是开场结论，放最前；第 4–8 部分展开；第 9–10 部分收尾。

## 4. 规则

1. **业务优先**：先说系统对业务做了什么，再提技术。不要用技术栈清单开场。
2. **归属要对**：团队或项目整体的成果属于团队，要明说；你自己的成果放在第 7 部分。不能把团队成果说成个人成果。
3. **指标不是必须的**：只有当你能解释这个数字怎么来的、你做了什么影响它时才用。初级工程师很难量化，也说不清的话，就描述具体结果（交付了什么、变了什么、哪个问题不再出现）。面试官会深挖你说的每个数字。
4. **钩子就是钩子**：每个挑战一句话，说清问题是什么、为什么难。不要讲解决方案，留给面试官去问。
5. **AI 是必填项**：说明你在自己的工作中怎么用 AI（例如用某个工具辅助编码、测试、调试、设计或评审）。开发 AI 产品不等于在工作中使用 AI。
6. **不要走回头路**：开场结论 → 展开 → 钩子 → 收尾。开始讲你的工作后，不要再回头补项目背景。
7. **不要编造**：只说真实的、你能深入讨论的内容。不要加你无法解释的术语。
8. **技术服务于你的工作**：技术出现在能说明你做了什么、为什么重要的地方，不要罗列。

## 5. 时长分级

评审 skill 使用同样的分级。

| 时长 | 等级 | 影响 |
|---|---|---|
| 2:30–3:00 | 达标 | 不扣分 |
| 2:00–2:30 或 3:00–4:00 | 可接受 | 轻微扣分 |
| 1:30–2:00 或 4:00–4:30 | 偏离 | 较多扣分 |
| 低于 1:30 或高于 4:30 | 不合格 | 触发硬性检查，档位封顶 |

没有录音只有文字时，用词数 ÷ 130 估算：达标约 325–390 词，可接受约 260–520 词，偏离约 195–585 词。

## 6. 示例（约 330 词）

以 Wells Fargo 手机银行迁移为素材。第 8 部分仅为示意：真实学员必须说自己的实际做法。

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

## 7. 开口前自查

- [ ] 前 40 秒内说清了：我的角色、最近的公司、项目、核心职责、交付了什么。
- [ ] 先讲了业务问题，再讲技术。
- [ ] 团队成果归团队；我自己的成果单独说。
- [ ] 用到的数字，我都能解释并经得起追问。
- [ ] 说了我在自己的工作中怎么用 AI。
- [ ] 有 2–3 个一句话挑战，没有讲方案。
- [ ] 以技能和方向收尾。
- [ ] 出声念一遍，用时 2.5–3 分钟。
