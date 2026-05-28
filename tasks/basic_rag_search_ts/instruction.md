# Basic RAG Ingest and Search with Alchemyst AI (TypeScript)

## Background
You are building the simplest possible Retrieval-Augmented Generation (RAG) flow on top of [Alchemyst AI](https://getalchemystai.com/docs/getting-started/quickstart), a managed Context Engine. Your job is to write a small Node.js/TypeScript script that uses the official `@alchemystai/sdk` package to (1) ingest a short FAQ document into the Alchemyst context store and (2) search for the answer to a question and print the matching snippet.

The script must hit the real Alchemyst API using the `ALCHEMYST_AI_API_KEY` environment variable. Do not mock the SDK.

## Requirements
- Create a Node.js/TypeScript project at `/home/user/rag_task`.
- Use the official `@alchemystai/sdk` package (already installed in the environment).
- Implement a script named `index.ts` that:
  1. Reads `ZEALT_RUN_ID` from the environment and generates a UUID suffix for the document `file_name` to avoid `409 Conflict` errors on retries.
  2. Ingests the following FAQ document into the Alchemyst context store using `client.v1.context.add`:
     - `content`: `"Refund policy: We offer a 30-day money back guarantee. To request a refund, email support@example.com with your order ID."`
     - `metadata.file_name`: `faq-<run-id>-<uuid>.md` (must be globally unique per run/retry).
     - `metadata.group_name`: `["alchemyst-harbor", "<run-id>"]`.
     - `context_type`: `"resource"`, `source`: `"docs"`, `scope`: `"internal"`.
  3. Searches for the question `"What is the refund policy?"` using `client.v1.context.search` with:
     - `similarity_threshold`: `0.5`
     - `scope`: `"internal"`
     - `metadata.groupName`: `["<run-id>"]` (note camelCase `groupName` is required for the search endpoint in the TS SDK).
  4. Prints output to **stdout** AND appends it to `/home/user/rag_task/output.log` in the exact format described in **Acceptance Criteria** below.
- The script must be runnable with `npx tsx /home/user/rag_task/index.ts` from the project directory.

## Implementation Hints
- The Alchemyst TS SDK is imported as the default export: `import AlchemystAI from '@alchemystai/sdk'` and constructed with `new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY })`.
- Watch out for the documented parameter inconsistency: storage uses `group_name` (snake_case) inside `metadata`, while the TS search endpoint expects `groupName` (camelCase) inside `metadata`.
- Use any UUID library available (e.g. `node:crypto`'s `randomUUID()`) to guarantee uniqueness of `file_name` per run.
- `client.v1.context.search` returns `{ contexts: [...] }` where each context has a `content` field. Use the first context's `content` for the snippet output.
- Read the current `run-id` from the `ZEALT_RUN_ID` environment variable and embed it in the `file_name` and `group_name` so that concurrent runs do not interfere with each other.

## Acceptance Criteria
- Project path: `/home/user/rag_task`
- Log file: `/home/user/rag_task/output.log`
- The script must successfully call the real Alchemyst API (no mocks).
- The document `file_name` in the ingested metadata must follow the pattern `faq-<run-id>-<uuid>.md` and be unique per run (using a UUID suffix).
- The document `group_name` must include `"<run-id>"` (the value of `ZEALT_RUN_ID`).
- After execution, `/home/user/rag_task/output.log` must contain, in order, lines matching the following patterns (one item per line):
  - `Stored file_name: <file_name>` — the exact `file_name` used during ingestion.
  - `Search matches: <N>` — the number of contexts returned by the search (must be `>= 1`).
  - `Top snippet: <content>` — the `content` of the top-ranked context, which must include the substring `30-day money back guarantee`.

