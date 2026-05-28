# Cross-Session Memory Recall with Alchemyst AI (Python)

## Background
Alchemyst AI is a Context Engine that provides AI agents with persistent, cross-session user memory. Memory is scoped by `user_id` and `session_id`: when the same `user_id` issues a query in a brand-new `session_id`, the engine can still surface preferences and facts stored under any prior session for that user. In this task you will write a small Python script that demonstrates this cross-session recall using the official `alchemystai` Python SDK (`v1.context.memory.add` and `v1.context.memory.search`).

## Requirements
- Implement a Python script `run.py` that:
  - Reads the `ALCHEMYST_AI_API_KEY` and `ZEALT_RUN_ID` environment variables.
  - Generates a fresh `user_id` and two distinct `session_id` values (`session_a`, `session_b`) on every run so that concurrent and repeated invocations do not collide. Embed both `ZEALT_RUN_ID` and a `uuid` component in those identifiers.
  - In `session_a`, stores a memory whose content includes the user preference text `I'm vegan` using `v1.context.memory.add`.
  - In `session_b` (different `session_id`, **same** `user_id`), retrieves memories for that user using `v1.context.memory.search` and concatenates the textual content of every returned memory.
  - Writes the recalled text to `/workspace/recalled.txt` (UTF-8). The file must contain the literal substring `vegan` once retrieval succeeds.
  - Appends a single line `Recall OK: user_id=<user_id>` to `/workspace/output.log` after the file has been written.
- The script must call the live Alchemyst AI API (no mocking) and use the `alchemystai` package.

## Implementation Hints
- Install dependencies with `pip install alchemystai`.
- Instantiate the client with `AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])`.
- The Python SDK exposes memory APIs via `client.v1.context.memory.add({...})` and `client.v1.context.memory.search(user_id=..., session_id=...)`. Returned objects expose a `memories` collection whose items have a `content` attribute.
- Because `user_id` and `session_id` are required for every memory call, build them deterministically from `ZEALT_RUN_ID` plus `uuid.uuid4().hex` so each run is unique and safe under parallel execution.
- Searching may need a short retry/wait loop because indexing is not always instantaneous; keep retries bounded and fail loudly if recall never produces the preference.

## Acceptance Criteria
- Project path: /workspace
- Log file: /workspace/output.log
- Recall file: /workspace/recalled.txt
- Run command: `python3 /workspace/run.py`
- After the run command exits with code 0:
  - `/workspace/recalled.txt` must exist and contain the substring `vegan` (case-insensitive).
  - `/workspace/output.log` must contain a line matching `Recall OK: user_id=<user_id>` where `<user_id>` includes the value of `ZEALT_RUN_ID`.
- The script must isolate per-run state by deriving `user_id` and both `session_id`s from `ZEALT_RUN_ID` so that concurrent runs do not interfere.

