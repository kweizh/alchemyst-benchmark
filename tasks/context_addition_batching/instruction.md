# Batch Add Documents to Alchemyst AI

## Background
Alchemyst AI provides a `v1.context.add` method to ingest documents. We need to ingest a batch of markdown files from a directory into the context engine.

## Requirements
- You have a Node.js project at `/home/user/project` with `@alchemystai/sdk` installed.
- There are three markdown files in `/home/user/docs`: `policy1.md`, `policy2.md`, and `policy3.md`.
- Write a TypeScript script `batch_add.ts` in `/home/user/project` that reads these three files and adds them to Alchemyst AI in a single `client.v1.context.add` request.
- For each document, the `content` should be the file's content, and the `metadata` should include `file_name` (e.g., `policy1.md`) and `group_name: ["support"]`.
- Use `context_type: 'resource'`, `source: 'docs'`, and `scope: 'internal'` in the request.
- Execute the script to ensure the documents are added successfully.

## Constraints
- Project path: `/home/user/project`
- The script must be named `batch_add.ts` and placed in `/home/user/project`.
- The script must run successfully using `npx tsx batch_add.ts`.
- The environment variable `ALCHEMYST_AI_API_KEY` is provided.