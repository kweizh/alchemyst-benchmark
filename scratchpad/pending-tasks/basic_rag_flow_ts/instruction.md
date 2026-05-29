# Basic RAG Flow with Alchemyst AI

## Background
Alchemyst AI provides a Context Engine that simplifies document chunking, embedding, and retrieval. In this task, you will build a basic RAG flow using the Alchemyst AI TypeScript SDK to store a policy document and retrieve it.

## Requirements
- Initialize the Alchemyst client using the `ALCHEMYST_AI_API_KEY` environment variable.
- Add a single document to the context engine containing the text: `Policy: 30-day refunds for all electronics`.
- To prevent conflicts with concurrent runs, the document's metadata must include a `file_name` set to `refunds-${run-id}.md`, where `run-id` is read from the `ZEALT_RUN_ID` environment variable.
- Include the document in the `support` group.
- After adding the document, search the context engine for the query `refund policy for electronics` within the `support` group.
- Write the retrieved document content to a log file.

## Implementation Hints
- Use `@alchemystai/sdk` and a TypeScript execution environment (e.g., `tsx` or `ts-node`).
- Use `client.v1.context.add` to ingest the document. You will need to provide `context_type: 'resource'`, `source: 'docs'`, and `scope: 'internal'` along with the `documents` array.
- Use `client.v1.context.search` to retrieve the document. You can filter by `metadata: { group_name: ["support"] }`.
- **Important**: Document indexing might take a few seconds. Add a short sleep (e.g., 3-5 seconds) between adding the document and searching for it to ensure it is available in the retrieval index.
- Format the output in the log file exactly as requested.

## Acceptance Criteria
- Project path: `/home/user/alchemyst-rag`
- Ensure the script is executed and the log file is generated.
- Log file: `/home/user/alchemyst-rag/output.log`
- The log file must contain the retrieved policy text in the format: `Retrieved Policy: <content>`.

