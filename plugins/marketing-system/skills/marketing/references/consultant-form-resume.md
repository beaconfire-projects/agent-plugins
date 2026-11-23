# Consultant form email and resume upload

Use this reference when the user wants to (1) email a candidate the one-time **Consultant Details form** link, (2) check whether the candidate filled it in, (3) upload a candidate's **resume** (PDF or DOCX) or check its processing status. It uses only the five tools listed under "Consultant form and resume" in [Tool boundary](tool-boundary.md), all carrying the `marketing` tag. If one is missing, its tag cannot be verified or its schema differs, stop and report the gap; never fall back to staffing tools, REST, SQL, shell uploads outside the steps below, or scripts.

## What the backend does

- **Form email.** Creates a one-time link (valid 7 days, usable once) and emails it to the candidate's primary email (falling back to the current personal email only when there is no primary email). The sender is the shared no-reply address; the calling AM is Reply-To. Sending again cancels the previous unused link. When the candidate submits, the answers are stored in full and **overwrite** the candidate's phone numbers, personal email, emergency contact, education, work authorization (type and expiry), current location, date of birth, SSN last 4, year came to the US and additional tech stacks. The form page itself needs no login.
- **Resume.** The file goes straight from the caller to S3 through presigned URLs. After the upload is confirmed, the backend extracts the text, splits it into chunks and creates OpenAI embeddings in the background, for later candidate matching. Only the **current** resume (the latest completed upload) is used; older versions are kept as files but their vectors are replaced. Candidate matching itself is not part of this workflow.
- **Drive.** When the deployment's Drive sync switch is on, sending the form email or uploading a resume first makes sure the candidate has a Drive folder (named `Name - Batch - PER-…`), the submitted form is written to the folder's details sheet and the resume is copied into the folder's `Resume / Base Resume` sub-folders (created when missing). The switch is a deployment setting; the tools do not control it and Drive problems never block the email or the upload.

## Prerequisites

- The candidate must exist and be visible to the caller (otherwise `not_found`). **Permissions come from the token, not from a role name:** reading the form status or the resume status needs `candidate::view`; sending the form email and uploading a resume need `candidate::edit`. A tool that is not in the tool list means the user was not granted that permission: say so and stop. On top of that the caller must be allowed to edit this candidate (the same rule as editing candidate details: Admin/Manager, the assigned AM, or an AM of the offer's Vendor); otherwise `forbidden` with the reason. There is no special rule for HR any more: whether HR may do this depends only on the permissions Authsome grants them.
- The candidate needs an email address (`no_email` otherwise): fix it through the candidate update workflow first; this skill does not edit contact data.
- Sending needs the deployment's mail settings; `mail_not_configured` / `mail_failed` mean the email was **not** sent and the new link was canceled. Report it; do not retry in a loop.

## Tools and order

| Goal | Call |
| --- | --- |
| Email the form link | `marketing_send_consultant_form_email(candidate_code)` |
| Did the candidate fill it in? | `marketing_get_consultant_form_status(candidate_code)` |
| Upload a resume | `marketing_create_candidate_resume_upload` → PUT to S3 → `marketing_complete_candidate_resume_upload` |
| Resume progress | `marketing_get_candidate_resume_status(candidate_code)` |

### Form email

1. Read `marketing_get_consultant_form_status` first. If the latest status is `sent` and not expired, tell the user that sending again invalidates that link, and confirm.
2. Show the target (candidate code, name) and that an email will be sent to the candidate; obtain confirmation (it is an outward-facing, non-idempotent action: calling twice sends two emails).
3. Call `marketing_send_consultant_form_email`. Report `recipient_email` and `expires_at`. Never display or guess the link; it exists only in the email.
4. If the call fails with an unknown outcome, check `marketing_get_consultant_form_status` before any retry.
5. `status`: `sent` (waiting), `submitted` (done; `used_at` is the time), `expired`, `canceled` (replaced by a newer link or the email could not be sent).

### Resume upload

1. Only `.pdf` and `.docx` are accepted; there is no size limit. Confirm the target candidate and file before uploading. A new upload becomes the current resume once completed.
2. Call `marketing_create_candidate_resume_upload(candidate_code, filename, size_bytes)` with the exact byte size.
3. Upload the file bytes to the returned presigned URL(s) **exactly as instructed** (do not add other headers; URLs are valid for `expires_in` seconds):
   - `mode = "single"` (up to 50 MB): one HTTP `PUT` of the whole file to `url`, with header `Content-Type` equal to `content_type`.
   - `mode = "multipart"` (over 50 MB): split the file into `part_size`-byte pieces (the last may be smaller); `PUT` piece *n* to the `url` of `part_number` *n* (no Content-Type header) and keep the `ETag` response header of every part.
4. Call `marketing_complete_candidate_resume_upload(candidate_code, resume_id, parts)`; `parts` (every `part_number` with its `etag`) is required only for multipart. It is safe to call again after completion. `not_uploaded` means the object is not in S3 yet: upload first, then complete again.
5. Poll `marketing_get_candidate_resume_status`: `uploaded` or `extracting` means processing; `embedded` means done; `failed` carries `last_error` (for example no extractable text in a scanned PDF: ask for a text-based file). Do not poll in a tight loop; once or twice after a short wait is enough.

If the PUT itself fails (for example 403 after the URLs expired), start again from step 2. The abandoned upload leaves no current resume.

## Business constraints

- `marketing_get_candidate_resume_status` returns, per resume version, `download_url`: a presigned S3 link to the original file, valid for `download_expires_in` seconds (30 minutes). Give it to the user to open, do not store or log it, and call the tool again for a fresh link after it expires. `download_url` is null when the resume has no S3 copy yet; report that, and never look for a Google Drive link instead (the tool no longer returns one).
- Never ask for, display or log resume content, SSN or other form answers; the tools do not return them.
- The form answers overwrite existing candidate data by design (business decision); there is no review step. Warn the user that a submission replaces the candidate's current phone, email, address, work authorization and education.
- A `422 invalid_answers` style error comes from the candidate-facing page, not from these tools.
- Do not use this workflow to change marketing status or submit the candidate. Running candidate matching is a separate skill (`candidate-matching`, tool `marketing_match_candidates`, needs `candidate::view`).
- Deleting a resume, downloading the original file and aborting an upload are web-only: there is no tool for them.
