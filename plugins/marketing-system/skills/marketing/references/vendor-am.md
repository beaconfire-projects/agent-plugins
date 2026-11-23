# Vendor AMs

仅可使用实际声明 tags 含 `marketing` 的 MCP 工具；本页三个工具已核对 `marketing/mcp/vendor_ams.py` 的 `{"marketing", "vendors"}` 声明。无法验证标签或工具不在目录里时停止，不得通过 REST、SQL 或脚本绕过。

An AM sees the data of the vendors they are assigned to; admins and managers see every vendor. Only users whose JWT role codes include `admin` or `am-manager` can see and call these tools (everyone else does not get them in the tool list: say so, do not look for a workaround). This is about **Vendor** assignment. Assigning an AM to a *candidate* is a different, separate action.

## Look up

`marketing_list_vendor_ams(q?)` returns every vendor (newest first) with `client_count` and its `ams` (`person_code`, `name`, `email`). `q` matches vendor name or code, or an AM's name or email. A vendor with an empty `ams` has no AM: only managers and admins can see its data. Use the returned `vendor_code` (`COM-nnnnnn`) when assigning; never invent codes. Resolve ambiguous vendor names with the user.

## Assign (batch)

1. Confirm the vendors and the AM **login emails** with the user. The email must belong to an active member of the Authsome application; the tool checks it, you do not guess or fix emails.
2. Show the plan (which emails → which vendors) and get a clear yes.
3. Call `marketing_assign_vendor_ams(vendor_codes, emails)`: up to 100 vendors and 50 emails per call; every email is assigned to every vendor. Everything is validated first and **nothing is written if anything is wrong**: a vendor or an AM that cannot be found (every missing vendor code and AM email is listed together in one answer), an invalid email, an email that is not an Authsome member, a person who is a candidate. Fix the named problem and call again.
4. **This tool never creates a person, and the backend no longer reads the HR master record.** If the answer says `Vendor not found: ...` show the codes to the user and resolve them with `marketing_list_vendor_ams(q)`; never guess or invent a vendor code. If it says `AM not found: ...` show the emails to the user: nobody in this system has them.
   - Only when the user explicitly asks to add that person as a new AM **and** `marketing_create_person` is in your tool list (it needs the `people::create` permission), follow the manual path in [Create a Person](create-person.md) (legal first name, last name and primary email are required; do not infer names from the email; this creates only a Person, never a candidate), show the plan and get a clear yes, create the person, read it back, and then call `marketing_assign_vendor_ams` again.
   - If `marketing_create_person` is not available to the user (the user lacks `people::create`), say that HR or an admin has to create the person in People first, and stop. Do not look for another way to create the person.
   - An AM who exists but is still refused with the Authsome message is an Authsome membership problem, not a missing person: report it as such.
   Already-assigned pairs change nothing (`unchanged`), so repeating is safe.
5. Read back with `marketing_list_vendor_ams(q=...)` and report the returned AMs. A change takes effect on the AM's next request.

## Unassign (batch)

1. Confirm the vendors and emails and get a clear yes. Say when it would leave a vendor without any AM.
2. Call `marketing_unassign_vendor_ams(vendor_codes, emails)` (same limits). Removing does not need the person to still be in Authsome. Emails that match nobody are listed in `not_found_emails` and skipped; pairs that were not assigned are `unchanged`.
3. Report `vendor_has_no_am` per vendor: those vendors can now only be seen by managers and admins until an AM is added. Read back with `marketing_list_vendor_ams`.

## Unknown outcomes

A tool error that says the outcome may be unknown: read the current state with `marketing_list_vendor_ams` before any retry; never blindly repeat a write. Each real change is audited (channel `mcp`, no emails recorded).
