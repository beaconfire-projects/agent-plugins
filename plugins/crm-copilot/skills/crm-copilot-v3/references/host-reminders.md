# Host notification handoff

Read this reference after `reminder_create` returns `status=COMMITTED`.

CRM persistence and a Claude/host notification are separate operations:

1. Use the host's native notification, reminder, automation, or scheduled-task
   capability when one is available. Create a one-time notification at the
   confirmed `remind_at` time, preserving the confirmed IANA timezone.
2. Include the reminder content, CRM reminder ID, customer name, and any
   confirmed company or meeting context in the notification message.
3. Reuse an existing host notification when the host supports listing and the
   same CRM reminder/time already exists. Do not create duplicates after an
   uncertain response.
4. If the host cannot schedule notifications, report the CRM reminder as
   saved and the host notification as unavailable. Never claim that the MCP
   database row itself will notify Claude.

The V2 MCP service does not execute delivery workers or push notifications;
the host-agent step is intentionally outside the CRM database transaction.
