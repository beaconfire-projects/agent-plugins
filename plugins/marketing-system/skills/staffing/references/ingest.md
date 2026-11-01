# Process emails or read the client chat now

Tools: `staffing_preview_mail_ingest`, `staffing_run_mail_ingest`, `staffing_get_mail_ingest_status`, `staffing_preview_chat_ingest`, `staffing_run_chat_ingest`, `staffing_get_chat_ingest_status`.

The system reads the mailbox (Submission and L2 Selected emails, interview invitations) and the client's chat group (interview results, scores and dates) by itself every few minutes. Use this workflow only when the user wants it **now**, for example "process the emails now" or "refresh the client chat". These runs create candidates, update interviews and send Feishu notices, so look before running.

## Steps

1. **Preview first.** Call `staffing_preview_mail_ingest` or `staffing_preview_chat_ingest` (read only; it can take up to a minute). Nothing is written and nothing is sent. Show the numbers in plain words:
   - **Mail**: emails in the window, how many were handled before, how many candidates would be created or updated, duplicates, emails that need a person, emails left for the next run (a run handles at most 50). Show the `alerts` text: that is what the team would get in Feishu.
   - **Chat**: messages read, results recognised, interviews that would be updated, results already set, results that differ from what is on file (a real run changes nothing for those), candidates with no such interview, results that could not be matched.
   - If everything is zero or already set, say there is nothing to do and stop.
2. **Confirm.** Say what a real run will do ("create 2 candidates and update 1; 3 alerts go to Feishu") and wait for a clear yes. A preview does not need a yes; the real run does.
3. **Run.** Call `staffing_run_mail_ingest` or `staffing_run_chat_ingest`. It runs in the background and answers `started` or `busy` (a run is already in progress: wait and try again, do not start another).
4. **Check the result** after a short wait with `staffing_get_mail_ingest_status` or `staffing_get_chat_ingest_status` and report the counts of the latest run. If the run is not finished yet, say so and check again once; do not loop.
5. If the status shows the scheduled run is still a **dry run**, tell the user: the automatic runs only preview until the dry-run setting is turned off on the server (a manual run always writes).

## Do not

- Do not run without previewing and confirming, unless the user explicitly says to skip the preview.
- Do not start a second run while one is `busy`.
- Do not repeat names, emails or other personal details from the preview beyond what the user needs to decide.
