# Alchemyst AI TypeScript: Filtered Search by `groupName`

## Background
The Alchemyst AI TypeScript SDK (`@alchemystai/sdk`) has a documented parameter-casing inconsistency: documents are **stored** with `metadata.group_name` (snake_case), but **searched** with `metadata.groupName` (camelCase). Write a small Node.js script that exercises this inconsistency by ingesting documents into two groups and then retrieving only one of them.

## Requirements
- Add six documents to the Alchemyst context engine using `@alchemystai/sdk`:
  - Three documents tagged with `metadata.group_name = ["alpha-${ZEALT_RUN_ID}"]`.
  - Three documents tagged with `metadata.group_name = ["beta-${ZEALT_RUN_ID}"]`.
  - Every document MUST use a `metadata.file_name` that includes a fresh `uuid` suffix to avoid `409 Conflict` errors (the file name must also include `${ZEALT_RUN_ID}` so concurrent trials do not collide).
  - Document `content` must be distinct so search results are meaningful.
- Issue a single search via `v1.context.search` that filters by `metadata.groupName: ["alpha-${ZEALT_RUN_ID}"]` (camelCase, as required by the search API) and a `query` that is generic enough to match the alpha-group content.
- Write the result to `/workspace/group_result.json` containing the count of returned context items and the de-duplicated, sorted list of group names observed across all returned contexts' `metadata.group_name` values.

## Implementation Hints
- Read your API key from the `ALCHEMYST_AI_API_KEY` environment variable.
- Read the `ZEALT_RUN_ID` environment variable and use it to namespace both group names and file names so the task is safe to re-run.
- Use the official quickstart pattern: `new AlchemystAI({ apiKey })` then `client.v1.context.add({ documents, context_type: 'resource', source: 'docs', scope: 'internal' })` for ingestion and `client.v1.context.search({ query, similarity_threshold, scope: 'internal', metadata: { groupName: [...] } })` for retrieval.
- The search filter MUST be `groupName` (camelCase) — this is the inconsistency this task is designed to exercise.
- Use a `similarity_threshold` low enough (e.g. 0.3-0.5) to ensure the three alpha documents are retrievable.
- After search returns, inspect each context's `metadata.group_name` array, flatten and de-duplicate them, then sort lexicographically before writing the JSON.
- Ingestion is asynchronous server-side; consider giving the index a short wait (e.g. ~10 seconds) before searching so the documents are indexed.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /workspace/group_result.json
- The script is executable end-to-end from the project directory using `npm` and Node.js 20+.
- The script reads `ALCHEMYST_AI_API_KEY` and `ZEALT_RUN_ID` from the environment.
- `/workspace/group_result.json` MUST exist after the script completes and MUST be a JSON object with exactly these top-level keys and types:
  ```json
  {
    "count": number,
    "groups": string[]
  }
  ```
  - `count` is the number of context items returned by the single search call.
  - `groups` is the sorted, de-duplicated list of group names extracted from `metadata.group_name` across all returned contexts.
- All returned context items MUST be tagged exclusively with the alpha group for the current `ZEALT_RUN_ID` (i.e. no beta-group contexts leak into the result).

