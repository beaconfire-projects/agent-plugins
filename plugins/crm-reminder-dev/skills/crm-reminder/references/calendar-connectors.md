# Calendar connector behavior

Use this reference only after the CRM reminder has been confirmed and created.

## Connector selection

Use the host's connected Google Calendar write tool. Tool names vary by Claude, Codex, and installed plugin version, so select by capability: it must create a Google Calendar event and return a stable event identifier or URL.

If no suitable tool is installed, report that Google Calendar is unavailable and record `failed` with a concise reason. If the tool requests authentication, let the host show its connection flow and record `pending_authorization`. Retry only after the user completes authorization.

## Event payload

- Title: the confirmed reminder subject.
- Start and end: the exact RFC 3339 values returned by MCP.
- Timezone: the exact IANA timezone returned by MCP.
- Reminder: the confirmed lead time.
- Attendees: omit unless the user explicitly requested invitations and confirmed the addresses.

After the connector responds, always call `record_google_calendar_result`. The administration UI relies on that result to show whether the database and calendar are linked.

## Recovery

Calendar writes can succeed even if the response is interrupted. Before retrying an uncertain write, search for an event matching the subject and exact start time when the connector supports search. If found, record it instead of creating a duplicate. Otherwise explain the uncertainty and get user confirmation before another create attempt.
