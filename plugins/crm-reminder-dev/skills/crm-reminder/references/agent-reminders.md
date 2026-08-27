# Host-agent reminder behavior

Use this reference only after the CRM reminder has been explicitly confirmed and created.

## Scheduling

Use the host's native reminder, automation, or scheduled-task tool. In Codex, prefer the app automation tool used for reminders and scheduled tasks. Create a one-time notification at:

`notification_at = meeting_start_at - remind_before_minutes`

Preserve the confirmed IANA timezone and use an absolute date and time. The notification message must include the customer name, company, meeting subject, and meeting start time so it is useful without reopening the original conversation.

Do not create a recurring automation for a one-time meeting reminder. Do not use a shell cron job, background process, Calendar popup, or database row as a substitute for the host's native notification.

## Availability and recovery

If the host has no native scheduled-notification capability, report the agent notification as unavailable. Do not claim the overall workflow completed.

Before retrying after an interrupted or uncertain create response, inspect existing host automations for the same meeting reminder and notification time when the host supports listing them. Reuse the existing task instead of creating a duplicate. If its existence cannot be determined, explain the uncertainty before retrying an external write.

If scheduling fails, preserve the CRM Reminder. Report each result independently.
