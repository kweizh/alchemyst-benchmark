# Delete a User's Memory and Verify Removal (Alchemyst AI, Python SDK)

## Background
Alchemyst AI is a context engine that provides AI agents with persistent memory across sessions. The `alchemystai` Python SDK exposes a `v1.context.memory` resource (with `add`, `update`, and `delete` methods) and a `v1.context.search` method that searches stored context (including memory) for relevant chunks.

This task exercises the *memory deletion lifecycle*: you will store a piece of memory for a single user/session, delete it through the documented Python SDK delete API, and then verify by searching that nothing referencing the memory remains.

## Requirements
- Use the official `alchemystai` Python package and the real Alchemyst AI Platform API.
- Read the credential `ALCHEMYST_AI_API_KEY` from the environment.
- Read the `run-id` from the `ZEALT_RUN_ID` environment variable so the task is safe to run concurrently.
- Use UUIDs scoped by `run-id` for both `userId` and `sessionId` so each run is isolated.
- The memory entry to insert MUST contain the text `User's nickname is Bumble`.
- After insertion, delete the memory through `v1.context.memory.delete` (the documented delete method on the Python SDK's memory resource).
- After deletion, search the Alchemyst context for the query `Bumble` (scoped to the same `userId`) and write the JSON result to `/workspace/post_delete_search.json`.
- The JSON file must demonstrate that no surviving result mentions `Bumble`.
- Log the user id, session id, and a final status line to a log file.

## Implementation Hints
- Install/import the Python SDK as `alchemyst_ai` (PyPI name: `alchemystai`).
- Construct the client with `AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])`.
- The memory resource lives at `client.v1.context.memory`; the delete method's parameter names are documented in the SDK's `api.md` / source — read the docstring or signature if you are unsure which keyword arguments to pass.
- Use `client.v1.context.search(...)` to verify post-deletion state; pass the same `user_id` you used when adding the memory and provide the required `query`, `similarity_threshold`, and `minimum_similarity_threshold` parameters.
- Serialize the search result with the SDK response's `.to_dict()` / `model_dump()` (or `json.loads(json.dumps(..., default=str))`) before writing JSON.
- Allow a brief wait (a few seconds) between writes and reads — the platform indexes asynchronously.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /home/user/myproject/output.log
- Output artifact: /workspace/post_delete_search.json
- The `run-id` value (from `ZEALT_RUN_ID`) MUST be embedded in both the `userId` and `sessionId` so concurrent runs do not collide.
- The log file MUST contain lines in the following formats (one occurrence each):
  - `UserId: <userId>`
  - `SessionId: <sessionId>`
  - `Status: success`
- After execution:
  - `/workspace/post_delete_search.json` MUST exist and contain valid JSON.
  - When the JSON is serialized as a string, it MUST NOT contain the substring `Bumble` (case-insensitive) — i.e., no surviving search result mentions the deleted memory.

