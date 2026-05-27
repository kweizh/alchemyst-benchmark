# Cross-Session Memory Recall with Alchemyst AI (TypeScript)

## Background
[Alchemyst AI](https://getalchemystai.com/) is a Context Engine that gives AI agents persistent memory across sessions. With the official TypeScript SDK `@alchemystai/sdk`, an application can store conversational memories tied to a `sessionId` and later recall those memories from a completely different session using a semantic `query`. This task exercises that cross-session recall capability end-to-end against the real Alchemyst platform.

You will build a small Node.js (TypeScript) program that:

1. Generates a unique synthetic `userId`, a session A id, and a session B id.
2. In session A, adds a memory entry stating that the user's preferred coding language is Rust.
3. In session B (different `sessionId`, same `userId`), queries the Alchemyst memory/context for the user's preferred coding language.
4. Writes the search result to `/workspace/recall.json`.

## Requirements
- Use Node.js 20+ and the official `@alchemystai/sdk` npm package.
- Read the API key from the `ALCHEMYST_AI_API_KEY` environment variable (the package picks it up automatically when set; you may also pass it explicitly to the client constructor).
- Generate fresh, unique IDs with `crypto.randomUUID()` (from Node's built-in `node:crypto`). To keep parallel runs isolated, read the `ZEALT_RUN_ID` environment variable and combine it with the random UUIDs (for example `zealt-${ZEALT_RUN_ID}-<uuid>`).
- Add the memory entry in session A using `client.v1.context.memory.add` with a `sessionId` and a `contents` array; the stored text MUST include the literal word `Rust` (case-sensitive) and convey that it is the user's preferred coding language.
- After adding, wait long enough for the platform to index the memory (a few seconds is sufficient) before searching.
- From session B, search for the preference using `client.v1.context.search` with a natural-language query about the user's preferred coding language. Use `scope: "internal"` and reasonable similarity thresholds (e.g. `similarity_threshold: 0.8`, `minimum_similarity_threshold: 0.5`). If no results come back, retry the search a few times with a short delay before giving up.
- Write the recall result to `/workspace/recall.json` as a JSON object with at least these top-level fields:
  - `userId`: the synthetic user id used for the run.
  - `sessionA`: the session id used to store the memory.
  - `sessionB`: the session id used to perform the recall.
  - `query`: the natural-language query string sent to `context.search`.
  - `contexts`: the array returned by the SDK (use the SDK's `contexts` field as-is; each entry should preserve its `content` and any score/timestamp fields).
- The final state of `/workspace/recall.json` MUST contain at least one entry in `contexts` whose `content` field mentions `Rust`.

## Implementation Hints
- Install the SDK with `npm install @alchemystai/sdk` and write your program in TypeScript; you can run it via `tsx`, `ts-node`, or by compiling with `tsc` and then running with `node`.
- The client is constructed as `new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY })` (default import from `@alchemystai/sdk`).
- `client.v1.context.memory.add` takes `{ sessionId, contents: [{ content: "..." }], metadata? }`. The platform-side user identity is bound to the API key, so the `userId` you generate is application-side metadata; you may also embed it inside the stored `content` string so semantic search can find it.
- `client.v1.context.search` returns `{ contexts: Array<{ content?: string; score?: number; ... }> }`.
- Use `fs/promises` to write the JSON file. Make sure the file is valid JSON.
- Indexing is not instantaneous; consider polling with a few retries until a Rust-related context is returned, then write the file.
- Use a sensible exit code: `0` on success, non-zero on failure.

## Acceptance Criteria
- Project path: `/workspace`
- Log file: `/workspace/run.log` (capture stdout/stderr of the script there; include the chosen `userId`, `sessionA`, `sessionB`, and the search response summary).
- Output file: `/workspace/recall.json`
- The script reads `ZEALT_RUN_ID` from the environment and uses it as part of every generated id.
- `/workspace/recall.json` must be valid JSON and contain top-level keys `userId`, `sessionA`, `sessionB`, `query`, and `contexts` (an array).
- `sessionA` and `sessionB` must differ from each other.
- At least one element of `contexts` must have a `content` field that contains the substring `Rust` (case-sensitive).
- The script must successfully complete the add-then-search flow against the real Alchemyst AI API (no mocking).

