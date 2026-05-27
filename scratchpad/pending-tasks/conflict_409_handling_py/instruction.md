# Alchemyst AI: Graceful 409 Conflict Handling on Document Re-Add

## Background
You are integrating the Alchemyst AI Context Engine into a content pipeline. The pipeline periodically refreshes the same logical document (identified by a stable `file_name`). Alchemyst uses `metadata.file_name` as a deduplication key on the `v1.context.add` endpoint, so attempting to re-add a document that already exists raises a **`409 Conflict`** (Alchemyst's recommended remediation is to delete the previous version, then re-add the new content — see the troubleshooting docs).

Your task is to write a Python script that **detects** this conflict at runtime, **recovers** from it programmatically, and **records** what happened in a structured status report.

The environment has been pre-seeded with one document that the script will collide with. The collision target is deterministic and derived from the run id (see `Acceptance Criteria`).

## Requirements
- Use the official Python SDK (`alchemystai` on PyPI, imported as `alchemyst_ai`).
- Read `ALCHEMYST_AI_API_KEY` and `ZEALT_RUN_ID` from the environment. Derive the collision target identifiers from `ZEALT_RUN_ID` exactly as specified in `Acceptance Criteria` (this is how the pre-seeded document was registered).
- Attempt to add a NEW version of the document (different `content`) but with the SAME `source`, `metadata.file_name`, and same `context_type`/`scope` as the pre-loaded document.
- The script MUST detect the resulting `409 Conflict` from the SDK (do NOT rely on automatic retries succeeding — disable retries on the initial conflicting `add` call so the conflict surfaces as an exception).
- When the 409 is observed, the script MUST: (a) delete the existing document(s) for that source via the SDK delete API, then (b) re-add the new content. The second add MUST succeed.
- After the recovery completes, write a JSON status report file documenting what happened (see schema in `Acceptance Criteria`).
- If the initial add succeeds without a 409 (unexpected — the environment is pre-seeded specifically to trigger it), the script MUST exit non-zero and the status report MUST set `conflict_detected` to `false`.

## Implementation Hints
- Read `ALCHEMYST_AI_API_KEY` and `ZEALT_RUN_ID` from `os.environ`. Optionally read `ALCHEMYST_ORG_ID` (default to `""` if unset — personal API keys accept an empty organization id on the delete endpoint).
- The SDK exposes a `client.v1.context.add(context_type=..., documents=[...], scope=..., source=..., metadata={...})` signature; the deduplication key is the top-level `metadata.file_name`. See the [Python SDK docs](https://getalchemystai.com/docs/integrations/sdk/python-sdk).
- Errors are surfaced as subclasses of `alchemyst_ai.APIStatusError`; a 409 has `status_code == 409` (the more specific class `alchemyst_ai.ConflictError` is also acceptable to catch). See the [Handling errors](https://getalchemystai.com/docs/integrations/sdk/python-sdk#handling-errors) section.
- Use `client.with_options(max_retries=0).v1.context.add(...)` for the conflicting call so the 409 is not silently swallowed by SDK retries (the SDK retries 409 by default).
- For deletion, call `client.v1.context.delete(source=<source>, organization_id=<org_id_or_empty_string>, by_doc=True)`. See [Delete context data](https://getalchemystai.com/docs/api-reference/endpoint/api/v1/context/delete/post).
- After re-adding, you do NOT need to immediately query Alchemyst to verify — record the outcome in the status report; the verifier will independently query Alchemyst.
- Useful reference patterns: [Pattern 2 — Document Updates](https://getalchemystai.com/docs/advanced/usage-patterns#pattern-2%3A-handling-document-updates) and [Troubleshooting — Common Errors (Add)](https://getalchemystai.com/docs/advanced/troubleshooting#common-errors-add).
- The new (v2) content you re-add MUST literally contain the marker substring `POLICY_V2_MARKER` somewhere in its text, so the verifier can locate it via the Alchemyst search API.

## Acceptance Criteria
- Project path: `/home/user/myproject`
- Command: `python3 /home/user/myproject/solution.py`
- Status report path: `/home/user/myproject/status.json`
- Required environment variables read by the script:
  - `ALCHEMYST_AI_API_KEY` (API auth)
  - `ZEALT_RUN_ID` (run id; used to derive the collision target identifiers below)
  - `ALCHEMYST_ORG_ID` (optional; default to empty string `""` if unset)
- Collision target identifiers MUST be derived from `ZEALT_RUN_ID` exactly as follows (these match how the pre-seeded v1 document was registered):
  - `source`           = `f"conflict409-{ZEALT_RUN_ID}"`
  - `metadata.file_name` = `f"policy-{ZEALT_RUN_ID}.md"`
  - `metadata.group_name` = `[f"conflict-eval-{ZEALT_RUN_ID}"]`
  - `context_type`     = `"resource"`
  - `scope`            = `"internal"`
- The script must exit with code `0` on the happy path (initial add fails with 409 → delete → re-add succeeds).
- The script must exit with a non-zero code if the initial add does NOT raise a 409, or if the recovery `add` fails.
- `status.json` must be valid JSON with EXACTLY these top-level keys and value types:
  ```json
  {
    "conflict_detected": true,
    "initial_add_status_code": 409,
    "delete_status": "success",
    "re_added": true,
    "file_name": "policy-<ZEALT_RUN_ID>.md",
    "source": "conflict409-<ZEALT_RUN_ID>",
    "run_id": "<ZEALT_RUN_ID>"
  }
  ```
  - `conflict_detected` (boolean): `true` only if the initial add raised a 409.
  - `initial_add_status_code` (number): the numeric HTTP status code observed on the initial add (409 on happy path).
  - `delete_status` (string): `"success"` if the SDK delete call returned without raising.
  - `re_added` (boolean): `true` if the second `add` call succeeded.
  - `file_name`, `source`, `run_id` (strings): the derived/provided values.
- After the script runs, the new content must be present in Alchemyst:
  - The new (re-added) document content MUST literally contain the marker substring `POLICY_V2_MARKER`.
  - A `client.v1.context.search` query targeting the new content must return a result whose `content` contains `POLICY_V2_MARKER`.
  - The pre-seeded marker phrase `POLICY_V1_MARKER` must NOT appear in search results for the same query window (the old document has been replaced).

