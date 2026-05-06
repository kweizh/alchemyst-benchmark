# Alchemyst AI Context Search Dashboard

## Background
Build a web-based dashboard for managing and searching AI context using Alchemyst AI. You will build a Next.js application that provides a UI for ingesting documents into the context engine and searching them using Context Arithmetic.

## Requirements
1. You have a Next.js project initialized at `/home/user/dashboard`.
2. Install `@alchemystai/sdk`.
3. Create an API route `POST /api/ingest` to ingest a document.
   - It should accept a JSON body with `content` (string), `file_name` (string), and `group_name` (array of strings).
   - Use `client.v1.context.add` to add the document. Ensure `context_type: 'resource'`, `source: 'docs'`, and `scope: 'internal'` are set.
   - **Friction Point Handling**: Attempting to add a document with an existing `file_name` triggers a 409 Conflict. Your code must catch this error, append a unique timestamp to the `file_name`, and retry the insertion to ensure success.
   - Place `file_name` and `group_name` in the document's `metadata`.
4. Create an API route `POST /api/search` to search the context.
   - It should accept a JSON body with `query` (string) and `group_name` (array of strings).
   - Use `client.v1.context.search` with a `similarity_threshold` of `0.5`.
   - Filter the search using the provided `group_name` array to demonstrate Context Arithmetic (Intersection).
   - **Crucial TS SDK Detail**: In the TypeScript SDK, storage uses `group_name` (snake_case) inside metadata, but search uses `groupName` (camelCase) at the root level of the search parameters.
5. Create a frontend page at `app/page.tsx` (or `pages/index.tsx` depending on the Next.js router) with two sections:
   - **Ingest Section**: A form with id `ingest-form` containing a textarea for content (id `content-input`), an input for file name (id `filename-input`), and an input for comma-separated group names (id `groupname-input`). A submit button (id `ingest-btn`). Upon successful ingestion, display a visible element with id `ingest-success`.
   - **Search Section**: A form with id `search-form` containing an input for query (id `query-input`) and an input for comma-separated group names (id `search-groupname-input`). A submit button (id `search-btn`). Display the retrieved document contents inside a div with id `search-results`.

## Constraints
- Project path: `/home/user/dashboard`
- Start command: `npm run build && npm start`
- Port: 3000
- The environment will provide `ALCHEMYST_AI_API_KEY`.
- You must use Node.js and Next.js.