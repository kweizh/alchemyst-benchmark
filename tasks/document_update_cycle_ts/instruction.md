# Update an Existing Document with the Alchemyst AI TypeScript SDK

## Background
Alchemyst AI is a managed Context Engine that stores documents for semantic retrieval. Alchemyst uses `metadata.file_name` as a deduplication key: trying to `add` a document whose `file_name` already exists in the same scope returns a `409 Conflict`. The recommended way to update an existing document is the **delete-then-add** pattern: first delete the stored document by its `file_name`, then `add` the new version with the same `file_name`.

An organization has already ingested an onboarding policy into Alchemyst with a `file_name` of `onboarding_v1-${ZEALT_RUN_ID}.md` and an effective date of `2024-01-01`. The policy has been revised and now uses an effective date of `2025-05-01`. Your job is to write a Node.js + TypeScript script using the official `@alchemystai/sdk` package that applies this update against the **real** Alchemyst API.

## Requirements
- Use Node.js 20+ and the official `@alchemystai/sdk` package (already installed in the environment).
- The script must hit the real Alchemyst API using `ALCHEMYST_AI_API_KEY` from the environment. Do **not** mock the SDK.
- The project lives at `/home/user/update_task`. Write your script at `/home/user/update_task/index.ts`.
- The script must implement the **delete-then-add** update pattern:
  1. Read `ZEALT_RUN_ID` from the environment and reconstruct the existing document's `file_name` as `onboarding_v1-${ZEALT_RUN_ID}.md`.
  2. Delete the existing document from the Alchemyst context store using its `file_name`.
  3. Add the new version of the document with the **same** `file_name` (so downstream consumers keep working) but with the updated content.
- The new document content must be exactly:
  > `Onboarding Policy: Effective date: 2025-05-01. All new hires must complete onboarding within 14 days of their start date.`
- After the script runs, a semantic search for the onboarding policy must surface the **new** content. The old phrase `Effective date: 2024-01-01` must no longer be returned by search results scoped to this run.
- The script must run end-to-end without raising an exception (in particular, no `409 Conflict`) and write a structured log file so the verifier can confirm execution.

## Implementation Hints
- Import the SDK as the default export and construct a client with the API key:
  - `import AlchemystAI from '@alchemystai/sdk'`
  - `new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY })`
- The Alchemyst TypeScript SDK exposes context operations under `client.v1.context.*` (e.g., `add`, `delete`, `search`).
- The deduplication key is `metadata.file_name`. When deleting by file name, consult the [Alchemyst troubleshooting docs](https://getalchemystai.com/docs/advanced/troubleshooting) and the [usage-patterns guide](https://getalchemystai.com/docs/advanced/usage-patterns) for the exact delete-then-add flow.
- Watch out for the documented parameter inconsistency: storage uses `group_name` (snake_case) in metadata, while the TS search endpoint expects `groupName` (camelCase). Use `metadata.group_name = ["<run-id>"]` on `add`, and `metadata.groupName = ["<run-id>"]` on `search`.
- The initial document was ingested with `context_type: "resource"`, `source: "onboarding-docs-${ZEALT_RUN_ID}"`, and `scope: "internal"`. Reuse those exact values for both the delete and the add operations so the update is scoped correctly and parallel runs do not collide.
- After deleting, give the backend a brief moment (a few hundred milliseconds) before re-adding, to avoid race conditions.
- The script can be executed with `npx tsx /home/user/update_task/index.ts` from the project directory.

## Acceptance Criteria
- Project path: `/home/user/update_task`
- Log file: `/home/user/update_task/output.log`
- The script must successfully call the real Alchemyst API (no mocks) and read `ALCHEMYST_AI_API_KEY` and `ZEALT_RUN_ID` from the environment.
- The script must use the existing `file_name` `onboarding_v1-${ZEALT_RUN_ID}.md` for both the delete and the re-add operations (the file name must NOT change across the update).
- After execution, `/home/user/update_task/output.log` must contain, on separate lines:
  - A line in the exact format `Updated file_name: onboarding_v1-<run-id>.md` where `<run-id>` is the value of `ZEALT_RUN_ID`.
  - A line in the exact format `Update status: success`.
- After execution, calling `client.v1.context.search` (or the equivalent REST endpoint) with `metadata.groupName = ["<run-id>"]` and `scope = "internal"` for a query about the onboarding policy must return at least one context whose content contains the substring `Effective date: 2025-05-01`, and **no** returned context content may contain the substring `Effective date: 2024-01-01`.

