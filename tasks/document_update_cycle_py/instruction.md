# Update an Existing Document in the Alchemyst AI Context Engine

## Background
Alchemyst AI is a context engine that stores documents and makes them retrievable via semantic search. When the *same* `file_name` is added again, the API returns a `409 Conflict` because Alchemyst uses `metadata.file_name` as a deduplication key.

An organization has already ingested an outdated policy document with `metadata.file_name = "policy_v1.md"`. The policy needs to be revised, but the file name must stay the same so downstream consumers keep working. You must implement the "delete-then-add" update pattern using the Alchemyst AI Python SDK.

## Requirements
- Write a Python script that, when executed, updates the existing policy document stored in Alchemyst AI.
- Remove the old version of the document using the Alchemyst context-delete API.
- Ingest the new version of the document using `v1.context.add` with `metadata.file_name = "policy_v1.md"` (the file name must NOT change).
- The new document content must replace the old one. After your script runs, a semantic search for the policy must surface the **new** content, and the **old** content must no longer be retrievable.
- The script must run end-to-end without raising an exception (including no `409 Conflict`).
- Log the outcome to a log file so the verifier can confirm execution.

## Implementation Hints
- Read `ZEALT_RUN_ID` from the environment. The pre-existing document was ingested with `source = "policy-docs-${ZEALT_RUN_ID}"`. Reuse that exact `source` value for both delete and add so the update is scoped correctly and parallel runs do not collide.
- Read `ALCHEMYST_AI_API_KEY` from the environment and use the `alchemystai` (`alchemyst_ai`) Python package to talk to Alchemyst.
- The new policy content to ingest is:
  > `Refund Policy v2: We now offer a 90-day money-back guarantee for all customers worldwide. Contact refunds@example.com to request a refund.`
- Keep `context_type = "resource"` and `scope = "internal"` for the add call, matching the initial ingestion.
- The Alchemyst delete endpoint operates per `source`. Refer to the Alchemyst API reference for the exact parameter names accepted by the Python SDK's `v1.context.delete` method.
- After deleting, give the backend a brief moment before re-adding to avoid race conditions.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /home/user/myproject/output.log
- Use the Alchemyst AI Python SDK (`alchemyst_ai` package) and the `ALCHEMYST_AI_API_KEY` environment variable.
- The script must read `ZEALT_RUN_ID` from the environment and use `source = "policy-docs-${ZEALT_RUN_ID}"` for both the delete and the add operation.
- The new document must be added with `metadata.file_name = "policy_v1.md"` (same file name as the original).
- After the script runs, the log file must contain a line in the exact format `Update status: success`.
- After the script runs, calling `v1.context.search` with a relevant query about the refund policy must return at least one context whose content contains the phrase `90-day` (the new content), and no returned context content may contain the phrase `7-day` (the old content).

