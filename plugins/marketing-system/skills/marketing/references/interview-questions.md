# Interview questions

Use this reference to search historical interview questions, see which questions are asked most often, read the stored question document of one interview, or re-fetch it. It uses only the four tools in [Tool boundary](tool-boundary.md) that carry the `marketing` tag. If one is missing, its tags cannot be verified, or its schema differs, stop and report the gap; never fall back to staffing tools, REST, SQL or scripts.

## Where the data comes from

When an interview is saved with an **Interview Questions Link** (a Google Doc), the backend fetches the document in the background, keeps its two sections (`Question List` and `Code Question List`), splits them into individual questions and generates an embedding for each question. Every question is typed `non_code` (from Question List) or `code` (from Code Question List). Clearing the link or deleting the interview removes the stored questions. Historical documents were migrated by interview ID.

Prerequisites: the feature must be enabled on the deployment. If a search returns nothing for an interview that clearly has a link, read its document (below) before concluding there are no questions.

## Tools and order

| Goal | Call |
| --- | --- |
| Find questions by wording, topic or filters | `marketing_search_interview_questions` |
| Most frequently asked questions | `marketing_get_question_frequency` |
| Full stored text and fetch status of one interview | `marketing_get_interview_document(interview_code)` |
| Re-fetch one interview's document | `marketing_refresh_interview_questions(interview_code)` |

1. **Search.** Use `q` for literal text. Use `query_text` to rank by meaning (for example "kafka consumer lag"); it sends only that text, with emails, URLs and phone numbers removed, to OpenAI. Combine with `question_type` (`code` / `non_code`), `tech` (text in the position's tech family or stack), `round_type`, `candidate_code`, `date_from` / `date_to`, and `vendor` / `client` / `position` codes (see [Scope filters](scope-filters.md)). Results are limited to interviews the caller may see; an interview outside that scope is reported as not found.
2. **Read the `mode` and `notes` fields.** `semantic` means ranked by similarity (only questions that already have an embedding take part). `keyword` means filter matches, newest interview first. If the embedding service was unavailable the tool falls back to keyword mode and explains why in `notes`; tell the user the ranking is not semantic in that case.
3. **Frequency.** `marketing_get_question_frequency` counts a question once per interview. Questions merge only when identical after lowercasing and removing numbering, punctuation and extra spaces, so rewordings are separate rows. Say this when presenting counts. `min_interviews` defaults to 2.
4. **One interview.** Use the `interview_code` (`INT-…`) from a hit. `status` is `success`, `pending` (not fetched yet), `failed` (reason in `last_error`) or `none` (never fetched). Show the two source sections when the user wants the original text.
5. **Refresh.** Only when the document is `pending` or `failed`, or the user says the link or document changed and nothing updated. It reads the Google Doc and calls OpenAI, so it can take seconds. Report the returned `status` and `last_error`; do not retry in a loop.

## Business constraints

- Questions are historical interview material for preparation; never present a question as a guaranteed future question.
- Do not infer a candidate's performance from the questions asked.
- A `failed` status with a 403/404 message means the backend cannot read that Google Doc (permission or deleted file). Refreshing will not help; ask the owner to share the document with the service account or correct the link on the interview.
- Questions and links can contain business-sensitive text. Quote what is needed, keep candidate details to what the user asked for, and do not copy question text into other tools.
- The tools never change the interview record or its link. To correct the link, update the interview with the Interview workflow; the background fetch then follows automatically.

## Error handling

- `not_found: Interview not found`: the code does not exist or is outside the caller's scope. Do not search for a way around the scope.
- `interview_questions_failed`: the operation could not be completed and a refresh outcome may be unknown. Read the document back with `marketing_get_interview_document` before any retry.
- An empty result is a valid answer. Say which filters were applied and suggest loosening them; do not guess missing data.
