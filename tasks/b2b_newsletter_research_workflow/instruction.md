# B2B Newsletter API with Alchemyst AI

## Background
Create a Node.js Express server that acts as a B2B Newsletter research workflow using the Alchemyst AI Context Engine.

## Requirements
- Create an Express API in `/home/user/project`.
- POST `/ingest`: Ingests a document into Alchemyst AI. Expects JSON body `{ "content": "...", "group": "..." }`. It should call `client.v1.context.add` with `context_type: 'resource'`, `source: 'docs'`, `scope: 'internal'`, and metadata `group_name: [group]`.
- GET `/research`: Searches Alchemyst AI. Expects query params `query` and `group`. It should call `client.v1.context.search` with the query and filter by `group_name: [group]`, then return the search results as JSON.

## Implementation Guide
1. Initialize a Node.js project in `/home/user/project`.
2. Install `express` and `@alchemystai/sdk`.
3. Create `index.js` that sets up the server on port 3000. Use the `ALCHEMYST_AI_API_KEY` environment variable to initialize the client.

## Constraints
- Project path: `/home/user/project`
- Start command: `node index.js`
- Port: 3000