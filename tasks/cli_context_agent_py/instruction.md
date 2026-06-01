# Context-Aware Terminal Assistant CLI (Python + Alchemyst AI v0.10.0 + OpenAI)

## Background
Inspired by Alchemyst's official CLI Agent example (https://getalchemystai.com/docs/example-projects/team/cli-chatbot), build a Python command-line *context-aware terminal assistant* that combines the **Alchemyst AI Python SDK (`alchemystai`, v0.10.0)** as a Context Engine with **OpenAI** as the answer-generating LLM. The CLI must support two subcommands: one to ingest a local note file into Alchemyst, and one to ask a natural-language question whose answer is grounded on the ingested notes.

### CRITICAL — Python SDK v0.10.0 API surface
In `alchemystai==0.10.0` there is **NO `client.v1.context.memory.search(...)`** method, even though the TypeScript SDK and some marketing pages mention one. **You MUST consult the authoritative Python API reference at https://raw.githubusercontent.com/Alchemyst-ai/alchemyst-sdk-python/refs/tags/v0.10.0/api.md before coding.** For document ingestion and retrieval you should use:
- `client.v1.context.add(...)` — store a document.
- `client.v1.context.search(...)` — semantic search over stored context.
- `client.v1.context.delete(...)` — remove previously-stored documents (useful for idempotent re-ingest).

## Requirements
- Implement a re-runnable CLI entrypoint at `/home/user/myproject/main.py` that exposes two subcommands:
  - `ingest <file>`: read a local text or markdown file (relative paths are resolved from `/home/user/myproject/`) and add its contents as a document to the Alchemyst context engine.
  - `ask <question>`: search the Alchemyst context engine for chunks relevant to `<question>`, build an OpenAI chat-completion prompt that injects those chunks as grounding context, call OpenAI, and print the model's answer to stdout.
- Both subcommands must read `ALCHEMYST_AI_API_KEY` and `OPENAI_API_KEY` from environment variables. Do not hardcode keys.
- The CLI must read `ZEALT_RUN_ID` from the environment and incorporate it into the document's `file_name` metadata so that concurrent runs do not collide on Alchemyst's uniqueness constraint (which otherwise raises `409 Conflict`).
- The notes directory `/home/user/myproject/notes/` will exist in the environment and contain at least one seeded markdown file the executor can ingest.
- The CLI must be re-runnable: running `ingest` twice on the same file must succeed both times (e.g., by delete-then-add, by suffixing `file_name` with `ZEALT_RUN_ID`, or by handling `409` gracefully).

## Implementation Hints
- Install dependencies with `pip3 install alchemystai==0.10.0 openai`. The Python import path for the Alchemyst SDK is `alchemyst_ai`.
- Initialize the Alchemyst client with `AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])` and the OpenAI client with `OpenAI(api_key=os.environ["OPENAI_API_KEY"])`.
- On `ingest`: read the local file from disk, then call `client.v1.context.add(...)` with the file contents as the document, `context_type="resource"`, `source="cli-notes"`, `scope="internal"`, and a `metadata` dict whose `file_name` value is a unique string that includes the basename of the file AND the `ZEALT_RUN_ID` value (for example `notes/refunds.md-${ZEALT_RUN_ID}`).
- On `ask`: call `client.v1.context.search(query=<question>, scope="internal", similarity_threshold=...)`, iterate `result.contexts` and concatenate the `content` fields into a grounding block, then pass that as the system or user content to an OpenAI Chat Completion (any modern chat-completion model is acceptable). Print the model's answer text to stdout. If no contexts are returned, you may still call OpenAI but include an explicit no-context note.
- The CLI is invoked via plain positional subcommands: `python3 main.py ingest <file>` and `python3 main.py ask <question>`. The `<question>` argument may contain spaces; the CLI should accept it as a single positional argument (quoted) or join trailing argv tokens.
- Use `python3` (not `python`).

## Acceptance Criteria
- Project path: /home/user/myproject
- Command (ingest): `python3 main.py ingest <relative_path>` where `<relative_path>` is a path under `/home/user/myproject/` (e.g. `notes/refunds.md`).
- Command (ask): `python3 main.py ask "<question>"`.
- Both subcommands must exit with status code 0 on success.
- `ingest` must read the file from disk and call Alchemyst `v1.context.add(...)` against the live service (no mocks, no in-process stubs).
- `ask` must call Alchemyst `v1.context.search(...)` and then call OpenAI's chat-completion API against the live service (no mocks, no in-process stubs). The model's answer text must be printed to stdout.
- Running `ingest` on the same file twice in a row must not crash the second invocation (CLI must be idempotent / re-runnable).
- The CLI must not hardcode the runtime values of `ALCHEMYST_AI_API_KEY` or `OPENAI_API_KEY`; the source must reference both environment variable names.
- The CLI must read `ZEALT_RUN_ID` and use it to namespace the `file_name` metadata for ingested documents so concurrent runs do not 409.

