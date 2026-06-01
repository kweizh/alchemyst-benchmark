# Idempotent Ingest with 409 Conflict Handling (Alchemyst AI, Python)

## Background
In Alchemyst AI's context engine, the `add` endpoint uses `metadata.file_name` as a deduplication key. When a document with the same `file_name` already exists, the API responds with `409 Conflict`. A robust ingest pipeline must detect this case, remove the existing document for that source, and re-add the new content so that the operation is effectively idempotent.

You will build a tiny Python CLI on top of the `alchemystai` SDK (v0.10.0) that performs one ingest attempt per invocation. The CLI is rerunnable: the first run typically ingests cleanly, and any subsequent run for the same `run-id` should detect the `409`, recover from it, and still succeed.

The `alchemystai` Python SDK API surface is described in the official Python API Reference (v0.10.0):
https://raw.githubusercontent.com/Alchemyst-ai/alchemyst-sdk-python/refs/tags/v0.10.0/api.md

You MUST consult that reference before assuming any method names exist on the client.

## Requirements
- Provide a Python entrypoint `main.py` in the project directory that can be executed via `python3 main.py`.
- Read the Alchemyst API key from the `ALCHEMYST_AI_API_KEY` environment variable. Do not hardcode it.
- Read the run identifier from the `ZEALT_RUN_ID` environment variable and use it to namespace any externally visible resource names so concurrent runs do not collide.
- Attempt to add exactly one document into the Alchemyst context engine using `client.v1.context.add(...)` (sync, not async).
- The document MUST carry `metadata.file_name` and a `source` value that both include the `run-id`, so the conflict can be both triggered and resolved deterministically.
- If the add call succeeds, the CLI MUST log a final structured result line indicating no conflict was encountered.
- If the add call fails with HTTP status 409 (Conflict), the CLI MUST:
  - Log a clear human-readable message indicating a conflict was detected.
  - Delete the conflicting document(s) for this run via `client.v1.context.delete(...)`.
  - Retry the add call exactly once; this retry MUST succeed.
  - Log a final structured result line indicating the conflict was resolved.
- The CLI MUST always exit with status code 0 when the conflict path is exercised correctly (i.e., never re-raise the 409 to the user).
- Any other API error (auth, 4xx other than 409, 5xx) is allowed to surface as a non-zero exit.

## Implementation Hints
- Install the SDK with `pip install alchemystai` and import it as `from alchemyst_ai import AlchemystAI`.
- The Python SDK auto-retries 409 by default. To make the conflict observable on the first failure (and to keep tests fast), consider constructing the client with `max_retries=0`.
- Status errors are raised as subclasses of `alchemyst_ai.APIStatusError`, which exposes `status_code`. You can branch on `status_code == 409` to enter the recovery path.
- `client.v1.context.delete(...)` deletes by `source` (with `by_doc=True`). Using a `source` value that is unique per run-id ensures `delete` only removes the document you just attempted to (re-)ingest, and not other unrelated content.
- Use `context_type="resource"` and `scope="internal"` for the add call.
- The final log line MUST be the very last line printed to stdout, and MUST be a single line of the exact form:
  - `RESULT: {"status": "ok", "conflict_resolved": false}` on a clean add
  - `RESULT: {"status": "ok", "conflict_resolved": true}` after the 409 recovery path
  Quoting/spacing must match a JSON object that can be parsed with `json.loads` after stripping the `RESULT: ` prefix.

## Acceptance Criteria
- Project path: /home/user/myproject
- Command: `python3 main.py`
- The command reads `ALCHEMYST_AI_API_KEY` and `ZEALT_RUN_ID` from the environment.
- The command exits with code 0 on both a clean add and on a 409 recovery.
- The last line of stdout matches the pattern:
  `RESULT: {"status": "ok", "conflict_resolved": <true|false>}`
  with `conflict_resolved` being a JSON boolean (`true` or `false`, lower-case).
- Running the command twice in a row with the same `ZEALT_RUN_ID` and the same `ALCHEMYST_AI_API_KEY`:
  - The second invocation MUST exit 0.
  - The second invocation's final `RESULT` line MUST have `"conflict_resolved": true`.
- Externally visible identifiers (`metadata.file_name`, `source`) used against the Alchemyst API MUST include the `run-id` so concurrent evaluations do not interfere.
- No mocking of the Alchemyst API is allowed; the CLI must talk to the real service using the provided API key.

