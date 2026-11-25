# Candidate attachments (work authorization files, passport, Social Security card and driver license)

Use this reference when the user wants to (1) upload a candidate's **EAD, visa or other immigration-status file** (OPT, STEM OPT, H1B, green card, H4 EAD ...), a **passport**, a **Social Security card (SSN)** or a **driver license**, (2) see which of those files a candidate has and which one is current, (3) get a link to open one, or (4) delete one. It uses only the five tools listed under "Candidate attachments" in [Tool boundary](tool-boundary.md), all carrying the `marketing` tag. If one is missing, its tag cannot be verified or its schema differs, stop and report the gap; never fall back to staffing tools, REST, SQL, shell uploads outside the steps below, or scripts.

## What the backend does

- **Types.** An EAD, visa or immigration-status file is filed under the **visa type** it belongs to, from the same list as the candidate's visa type: `USC`, `GC`, `H1B`, `F1 OPT`, `OPT`, `OPT Extension`, `STEM OPT`, `F1 CPT`, `CPT`, `GC-EAD`, `H4 EAD`, `H4-EAD`, `C08 EAD`, `C09 EAD`, `A05 EAD`, `C05 EAD`, `C14 EAD`, `C26 EAD`, `C33 EAD`, `Asylum EAD`, `Other EAD`, `L2`, `L2B`, `L2S`, `Other`. There is no generic `EAD` or `VISA` type: a STEM OPT EAD card is `STEM OPT`, a green card is `GC`, a green card EAD is `GC-EAD`, an H-1B approval notice (I-797A) is `H1B`, an EAD card whose category is not known is `Other EAD`, and any other visa paper is `Other`. Three more types are not about visa status: `PASSPORT`, `SSN` (the Social Security card) and `DRIVER_LICENSE`. Types are case-insensitive and accept spaces, underscores or hyphens (`stem_opt`). Any other value is rejected with `unsupported_attachment_type`; do not map other documents (I-9, resume) onto these types. If the document's type is unclear, ask the user which type it is instead of guessing.
- **Several files, one current.** A candidate can have many attachments of the same type. Exactly one per type is **current**: the one with the newest `effective_at`. For a manual upload `effective_at` is the time the upload was completed; for a file imported from Google Drive it is the file's last-modified time in Drive. So a Drive file that is older than an uploaded one never takes over, and uploading a new file makes it current. `is_current` is recomputed by the backend; there is no tool to pick another one.
- **Files.** PDF, JPG, PNG and HEIC, at most 20 MB each. The file goes straight from the caller to S3 through a presigned URL (one PUT, no multipart).
- **Visa files are read automatically.** After a file of a visa type (every type except `PASSPORT`, `SSN`, `DRIVER_LICENSE`) is completed, the backend reads it with an LLM in the background and writes the start date, expiration date and a short detail into the candidate's work authorization record (`person_work_authorizations`, linked back through `source_attachment_id`). `PASSPORT`, `SSN` and `DRIVER_LICENSE` are never read. Progress is the attachment's `parse_status`: `pending` (queued), `parsing`, `parsed` (written), `needs_review` (not written, `parse_error` says why), `failed` (`parse_error` says why; retried automatically up to 3 times) and empty (not triggered: a non-visa file, or a file that existed before this feature or came from Drive sync, which an engineer back-fills with `scripts/parse_visa_attachments.py`). Rules the backend applies, which you must not try to override:
  - The attachment type chosen by the user wins. If the document reads as a different type, is unreadable, has contradictory dates or yields nothing, it is `needs_review` and nothing is written.
  - Fields the user maintained by hand are never overwritten; `source` of an existing row never changes.
  - A work authorization row is current when its attachment is the current one of that type (per type, like attachments). A newer file of the same type adds a new row and retires the older one; if the older row holds hand-maintained fields it is left alone and the new file becomes `needs_review`.
  - Values that cannot be read stay empty; nothing is guessed.
- **Drive sync.** Files in a candidate's Google Drive folder are copied into the attachment list by a backend script run by an engineer (`scripts/sync_attachments_from_drive.py`). There is no tool to start it or to check it. Drive is read-only for the system: uploads made here are not written to Drive. Items listed with `source = drive-sync` came from that script.

## Prerequisites

- The candidate must exist and be visible to the caller (otherwise `not_found`). **Permissions come from the token:** listing and getting a link need `candidate::view`; uploading and deleting need `candidate::edit`. A tool that is not in the tool list means the user was not granted that permission: say so and stop. For writes the caller must also be allowed to edit this candidate (Admin/Manager, the assigned AM, or an AM of the offer's Vendor); otherwise `forbidden` with the reason.

## Tools and order

| Goal | Call |
| --- | --- |
| Upload a file | `marketing_create_candidate_attachment_upload` → PUT to S3 → `marketing_complete_candidate_attachment_upload` |
| List files | `marketing_list_candidate_attachments(candidate_code, attachment_type?)` |
| Open a file | `marketing_get_candidate_attachment_download_url(candidate_code, attachment_id)` |
| Delete a file | `marketing_delete_candidate_attachment(candidate_code, attachment_id)` |

### Upload

1. Confirm the candidate, the type (one of the types above) and the file with the user. Check the extension (`.pdf`, `.jpg`, `.jpeg`, `.png`, `.heic`) and that the size is at most 20 MB before calling; do not read or display the file's content.
2. Call `marketing_create_candidate_attachment_upload(candidate_code, attachment_type, filename, size_bytes)` with the exact byte size.
3. HTTP `PUT` the whole file to the returned `url` with the header `Content-Type` equal to `content_type` and no other headers. The URL is valid for `expires_in` seconds.
4. Call `marketing_complete_candidate_attachment_upload(candidate_code, attachment_id)`. It is safe to call again after completion. `not_uploaded` means the object is not in S3 yet: upload, then complete again. `too_large` means the stored object exceeded 20 MB and was discarded.
5. Report the returned `attachment_id`, `attachment_type`, `is_current`, `effective_at` and, for a visa type, `parse_status` (normally `pending`: the read happens in the background, so the candidate's work authorization is not updated yet). Read the list again later to see `parsed` / `needs_review` / `failed`; there is no tool to start or retry the read. For `needs_review` or `failed`, tell the user the `parse_error` and that the candidate's visa fields can be corrected through the candidate update workflow.

If the PUT fails (for example 403 after the URL expired), start again from step 2. An abandoned upload is never listed and never becomes current.

### List and open

- The list is grouped by type; within a type the current one comes first, then the others newest first. `download_url` is a presigned S3 link valid for `download_expires_in` seconds (30 minutes). Give it to the user to open, do not store or log it, and call `marketing_get_candidate_attachment_download_url` for a fresh link after it expires.
- An empty list means nothing has been uploaded or synced for that type; it does not mean the candidate has no visa or EAD. Current is decided per type: a candidate can have a current `OPT` file and a current `H1B` file at the same time.

### Delete

Deleting is permanent: the record and the S3 file are removed and it cannot be undone. Show the target (candidate code, attachment id, type, filename, whether it is current) and the effect, and obtain explicit confirmation first. Afterwards report `current_attachment_id` (the file of the same type that is now current, or none) and read the list to verify the file is gone.

- If the deleted file came from Google Drive (`source = drive-sync`) and is still in the candidate's Drive folder, the next Drive sync imports it again. To get rid of it for good, the file also has to be moved out of the Drive folder; tell the user, because no tool can do that.
- If the delete fails with `storage_error`, the record is still there; do not retry in a loop, report it.

## Business constraints

- Never ask for, display or log the content of these files or any identifiers read from them. A Social Security card file holds the full SSN: never open, read aloud, copy or paste its content into the chat; only pass the presigned link to the user. The tools do not return file content.
- Do not use this workflow to change the candidate's visa type or dates by hand (the automatic read above is the only thing that writes them from a file); to submit the candidate or to change marketing status.
- Files that the Drive sync could not classify (the file name names more than one kind of document, such as `Passport and Visa`, or none) are not in the list. They appear only in the sync script's report and need manual handling by an engineer; there is no tool for them.
- Aborting an upload and downloading through the web page are web-only; there is no tool for aborting.
