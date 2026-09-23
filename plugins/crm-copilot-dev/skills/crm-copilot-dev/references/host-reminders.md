# Host notification handoff

Read this reference immediately after `reminder_create` returns
`status=COMMITTED`. The host notification step is mandatory.

CRM persistence and a Claude/host notification are separate operations:

1. **Google Calendar is the default host notification.** If a Google
   Calendar tool (e.g. `create_event`) is available in the session, always
   use it — do not fall back to a generic scheduled-task/trigger
   notification when Calendar is available, and do not ask the user which
   to use. Create one calendar event per committed reminder:
   - **Start time**: the confirmed `hostNotification.scheduleAt` /
     `remind_at` time, in the confirmed IANA timezone.
   - **Duration**: exactly 15 minutes (end time = start time + 15 minutes).
     Do not default to 30 minutes or a full hour.
   - **Title**: short, identifying who or what the follow-up is about (e.g.
     "Follow up: <Name> (<Company>)").
   - **Description**: enough context to act on the reminder without
     re-reading the original notes — the person's name, company/role, what
     was discussed, and what the follow-up is — plus the CRM reminder ID for
     traceability.
   - **Reminder override**: add a popup reminder ~10 minutes before the
     event start, so the user gets a heads-up in addition to the calendar
     entry itself.
   - Do not also create a scheduled-task/trigger notification for the same
     reminder when the calendar event was created successfully — that
     produces duplicate notifications for the user.
2. **Fallback**: if no Google Calendar tool is available in the session, or
   the `create_event` call fails, fall back to the host's native
   notification, reminder, automation, or scheduled-task capability when one
   is available. Create a one-time notification at
   `hostNotification.scheduleAt` (the confirmed `remind_at` time), preserving
   the confirmed IANA timezone. On mobile this must be a host-level
   notification/calendar reminder, not merely a CRM database row or an MCP
   App page. Tell the user plainly that the calendar event could not be
   created and why, rather than silently switching mechanisms.
3. Include the reminder content, CRM reminder ID, customer name, and any
   confirmed company or meeting context in the notification message
   (calendar event description, or fallback notification message).
4. Reuse an existing host notification/calendar event when the host supports
   listing and the same CRM reminder/time already exists. Do not create
   duplicates after an uncertain response.
5. If the host cannot schedule notifications or calendar events at all,
   report the CRM reminder as saved and the host notification as
   unavailable. Never claim that the MCP database row itself will notify
   Claude. Do not report the overall reminder workflow as complete until the
   host call (calendar event or fallback notification) returns success.

The V2 MCP service does not execute delivery workers or push notifications;
the host-agent step is intentionally outside the CRM database transaction.
