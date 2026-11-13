# Candidate creation is a deliberate gap

Scenario: “create candidate”, promote an existing person, or continue marketing after HR import.

**There is currently no tool with the `marketing` decorator tag for creating/converting a candidate or changing candidate marketing status. Stop rather than calling staffing-only candidate tools.** A shared Person, consultant flag and eligible candidate are not interchangeable. Do not smuggle candidate fields into a person import/update.

1. Clarify whether the user needs an ordinary Person or an eligible candidate. If only manual Person creation or an approved HR person import is wanted, load [create person](create-person.md) and obtain its separate confirmation.
2. For a submission goal, use `marketing_search_submission_candidates(q, page, page_size)` to check existing eligibility; resolve one result with the user. If present, continue with the [submission workflow](submission.md), not a new candidate creation.
3. If missing, explain that nonappearance can mean eligibility/scope, not necessarily absence. An authorized all-vendor operator may use `marketing_list_people` and `marketing_get_person` for the independent shared-person lookup; never use that to bypass a denied scoped operation.
4. Hand off candidate creation/conversion/readiness to an authorized human in the approved application/process. Provide known Person code, intended candidate identity and missing readiness requirement, without unnecessary personal data. Ask for completion and the exact candidate code; do not claim any write occurred.
5. After the human reports completion, run `marketing_search_submission_candidates` again and verify the returned identity/eligibility before resuming. If still absent or denied, stop and report the unresolved gap; do not automatically repeat import or call another plugin.

No write confirmation can authorize a nonexistent marketing-tag tool. Candidate return-to-marketing status changes have the same boundary: manual completion, then supported readback where available, not invented automation.

Submission-based Interview creation/editing is now available through the separately documented [Interview workflow](interview.md); it does not fill the candidate-conversion gap.

For Position creation/editing and JD parsing, use the supported [Position workflow](position.md).
