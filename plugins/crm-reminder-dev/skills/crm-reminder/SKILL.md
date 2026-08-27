---
name: crm-reminder
description: Create and query CRM reminders, search and update customer records, and schedule host-agent notifications through crm-reminder-mcp. Use for CRM customer lookups or changes and requests to schedule, remember, follow up with, or meet a customer.
---

# CRM Reminder

Use `crm-reminder-mcp` as the only source of truth for chat-driven customer and reminder operations. Do not bypass missing MCP capabilities with direct REST calls, database queries, or shell scripts. If the requested operation has no suitable MCP tool, say that it is not supported and identify the missing tool.

## Choose the workflow

- For creating a meeting reminder, follow **Create reminder**.
- For finding or viewing customers, follow **Query customers**.
- For changing customer information, follow **Update customer**.
- For listing the token owner's reminders, follow **Query reminders**.

## Create reminder

1. Determine the user's current time and IANA timezone. Preserve the original user text. If the host supplies a voice transcript but not the audio file, pass the transcript and do not claim that original audio was stored.
2. Call `prepare_reminder`. Pass the raw request and every known field, including customer name, email, phone, company, job title, meeting start, duration, and reminder lead time. The MCP result remains a draft and must not create a customer.
3. If required fields are missing or multiple customer candidates are returned, ask only for the missing choice or value, then prepare a corrected draft.
4. Present the complete customer and reminder details, including every field listed in `defaulted_fields`. Also show the exact agent notification time, calculated as `meeting_start_at - remind_before_minutes`. Ask for explicit confirmation of customer creation, the reminder, and the agent notification. Do not treat the initial scheduling request as confirmation of an automatically extracted customer.
5. Only after an affirmative confirmation, call `confirm_reminder` with `confirmed=true`. Use `customer_id` when the user selects an existing candidate. Otherwise pass all user-confirmed customer fields so the new customer record includes email and phone when provided.
6. Create a one-time notification with the host agent's native reminder or scheduled-task capability. In Codex, use the available automation/schedule tool. Schedule it for the exact notification time shown at confirmation, and make its message identify the customer, company, meeting subject, and meeting start time. Follow [references/agent-reminders.md](references/agent-reminders.md).
7. Report CRM Reminder and host-agent notification separately. Say the overall workflow is complete only when both succeeded.

## Query customers

1. Call `search_customers` with the user's name, email, phone, company, or job-title query. An empty query may be used only when the user explicitly asks for all customers.
2. If no customer matches, say so. If multiple customers match, show enough non-sensitive fields to distinguish them and ask the user to select one when selection is needed.
3. For a single match or an explicit list request, present the MCP result. Do not supplement it from the admin API or database.

## Update customer

1. Call `search_customers` to resolve the target. Never guess a customer ID.
2. If there is not exactly one unambiguous match, ask the user to select the customer.
3. Show the current values and proposed changes for name, email, phone, company, and job title. Ask for explicit confirmation. A request to change a value is not itself the required confirmation when customer identity was resolved automatically.
4. Only after confirmation, call `update_customer` with the selected `customer_id`, changed fields, and `confirmed=true`. Use `clear_email` or `clear_phone` only when the user explicitly asks to remove that value.
5. Return the updated MCP record and identify every field changed.

## Query reminders

1. Call `list_my_reminders`. Pass explicit status or meeting-start date filters when the user supplied them; otherwise return the token owner's reminders without inventing a time range.
2. Present subject, customer, meeting time, and status. Respect the MCP limit and state when the result was limited.
3. “My” always means the authenticated MCP user. Never use an admin endpoint to broaden the result to other users.

## Invariants

- Customer creation and customer updates always require explicit human confirmation.
- Never invent a customer, company, role, contact detail, attendee, time, timezone, or automation ID.
- The authenticated MCP identity identifies the actor and reminder owner. Do not accept or send a model-generated `created_by` or owner value.
- Treat vague times and defaults as values to display prominently before confirmation.
- A database reminder and a host-agent notification are distinct results; never imply that one substitutes for another.
- Do not expose OAuth tokens, authorization headers, or other credentials in chat, logs, or tool arguments.
