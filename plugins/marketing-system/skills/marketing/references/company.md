# Companies

Vendor and Client are additive roles on one shared company. All admitted users can read/create Clients and edit basic fields. Adding Vendor requires a lowercase JWT role code `am`, `admin` or `am-manager`, plus exactly one person whose primary email matches the operator; that person is automatically bound as AM. Flags `is_own_entity` and `is_po_vendor` are independent and do not assign an AM.

Use [Create orchestration](create-orchestration.md) for search-first dependency creation and partial-failure recovery.

## Find/create or attach a role

1. Call `marketing_list_companies(q?, role?)` (`role`: `vendor` or `client`; no pagination, omitted filters return the catalog). Resolve ambiguity; `marketing_get_company(code)` returns business `id`, internal decimal-string `company_id`, and `version`.
2. For a Vendor addition call `marketing_company_capabilities`; stop if unavailable and report its reason. Do not try to repair identity/permissions implicitly.
3. Call `marketing_check_company(request)` with required `name`, `legal_name`, `roles`, optional `domain`, flags, and **`use_ai=true` for Vendor creation** (including a Vendor created as a dependency). For non-Vendor company creation, keep `use_ai=false` unless the user requests AI enrichment. Roles may be empty only with an enabled flag. Vendor creation enables AI enrichment by default without a separate consent prompt; respect an explicit user opt-out (`use_ai=false`). AI enrichment is only a suggestion. Review matching company/preview; `ready_create` can mean attach-role, not a new company. A check neither writes nor authorizes a write, and does not establish that existing flags match the request.
4. State identity, roles/flags and supplied profile, plus automatic AM assignment and sheet sync. Under an explicit create goal, proceed without per-company confirmation when unambiguous and complete; ask for missing legal identity/type or ambiguous matches. Review AI suggestions before using them; Vendor creation does not require a separate AI-enrichment consent prompt.
5. Call `marketing_create_company(request)` with `name`, `legal_name`, `roles`, optional domain/flags. New company may include approved `enrichment` (`full_legal_name`, `domain`, `industry`, `notes`, `slug`, `quality_score` as text or null). For role attachment include **both** existing `company_id` and `version`; omit enrichment and both flag fields. Existing flags must be changed with update. `sync_google_sheets` defaults false; true requests only a bounded wait, not guaranteed sheet success.
6. Read `marketing_get_company(code)` using the returned `company.id`; report `created`, `added_roles`, actual roles/flags and task statuses separately.

## Edit an existing company

Read exact code → capability check if adding Vendor → confirm diff → `marketing_update_company(code, request)` → exact readback. Request requires positive `version`; editable fields: `display_name`, `full_legal_name`, `domain`, `industry`, `notes`, `slug`, `quality_score`, `roles`, `is_own_entity`, `is_po_vendor`. Nullable text may be cleared, but display name and roles cannot be null. If sending roles, send the complete superset of current roles: removal is forbidden. Boolean flags must be booleans, not null. Keep at least one company type; the service also recognizes a historical C2C type. No delete, merge, relationship or arbitrary AM-assignment operation exists here.

## Recovery

Duplicate name/domain resolution is rechecked on write. `entity_exists`, `confirmation_required` or `identity_conflict`: search/read again, resolve identity with the user, do not create a near-duplicate. `version_conflict`: read and reconfirm. `vendor_permission_required`, `am_identity_not_found` or `am_identity_ambiguous`: stop for administrator correction. `role_removal_forbidden`/`company_type_required`: explain the constraint. Unknown `company_operation_failed`: verify by code or identity search before proposing any retry. A failed/pending sheet task does not undo a committed company; report it without recreating the company.
