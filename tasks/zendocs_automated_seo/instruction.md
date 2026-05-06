# Zendocs Backend

## Background
You are building the backend for Zendocs, an automated SEO and indexing tool. You will use Express.js, SQLite, and the `@alchemystai/sdk` to ingest documents and make them searchable.

## Requirements
1. You have an empty directory at `/home/user/zendocs-backend`. Initialize a Node.js project in it.
2. Install `express`, `sqlite3`, and `@alchemystai/sdk`.
3. Create an Express server in `index.js` listening on port 3000.
4. Initialize a SQLite database `zendocs.db` with a `documents` table (`file_name` TEXT PRIMARY KEY, `content` TEXT, `group_name` TEXT).
5. Implement `POST /api/docs/generate`:
   - Accepts JSON: `{ "fileName": "string", "content": "string", "group": "string" }`.
   - Saves or updates the document in the SQLite database.
   - Adds the document to Alchemyst AI using `client.v1.context.add({ documents: [{ content, metadata: { file_name: fileName, group_name: [group] } }], scope: 'internal' })`.
   - **Handling Updates**: If a document with the same `fileName` already exists in Alchemyst AI, the `add` operation will fail with a 409 Conflict. You must catch this error, delete the old document from Alchemyst AI (using `client.v1.context.delete({ metadata: { file_name: fileName } })`), and then retry adding the new document.
6. Implement `GET /api/docs/search`:
   - Accepts query parameters `q` (search query) and `group` (group to filter by).
   - Searches Alchemyst AI using `client.v1.context.search` with `similarity_threshold: 0.5` and `scope: 'internal'`.
   - Filters the search by the provided group. *Hint: The Alchemyst AI TypeScript SDK has a parameter naming inconsistency. Storage uses `group_name` (snake_case), but search filtering requires `groupName` (camelCase) inside the `metadata` filter.*
   - Returns the search results as JSON: `{ "results": [...] }` (where the array contains the contexts returned by Alchemyst).

## Constraints
- Project path: `/home/user/zendocs-backend`
- Start command: `node index.js`
- Port: 3000
- The Alchemyst API key will be provided in the `ALCHEMYST_AI_API_KEY` environment variable.