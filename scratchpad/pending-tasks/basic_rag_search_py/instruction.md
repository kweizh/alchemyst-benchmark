# Basic RAG Search with Alchemyst AI (Python SDK)

## Background
Alchemyst AI is a Context Engine that provides AI agents with persistent memory and business-specific data through built-in chunking, embedding, and retrieval. In this task you will use the official Python SDK (`alchemystai`) to ingest a small policy document into the Alchemyst context engine and then query that same context engine for an answer.

## Requirements
- Create a Python script at `/home/user/myproject/rag_search.py` that:
  - Initializes an `AlchemystAI` client using the `ALCHEMYST_AI_API_KEY` environment variable.
  - Ingests exactly one document via `client.v1.context.add(...)` whose `content` is the refund policy text below.
  - Sets `context_type="resource"`, `source="docs"`, and `scope="internal"` when adding the document.
  - Provides `metadata` for the document including a `file_name` field that is unique per run, of the form `refund-policy-<run-id>.md` (see Implementation Hints).
  - After ingesting, calls `client.v1.context.search(...)` with the query `What is the refund policy?`, `similarity_threshold=0.7`, `scope="internal"`, and prints the content of the top match to stdout.
  - Mirrors the printed top-match line into the log file `/home/user/myproject/output.log`.
- Run the script so that it actually ingests the document into Alchemyst and writes the log file.
- Document content (must be ingested verbatim):

  ```
  Our refund policy: We offer a 30-day money back guarantee. Contact support@example.com to request a refund.
  ```

## Implementation Hints
- Install the Alchemyst Python SDK with `pip install alchemystai`; import it as `from alchemyst_ai import AlchemystAI`.
- Read `run-id` from the `ZEALT_RUN_ID` environment variable and append it to the `file_name` metadata value to avoid `409 Conflict` errors across repeated runs (the Alchemyst API rejects duplicate `file_name` values).
- Use `client.v1.context.add` to ingest the document (it accepts a list under `documents=[{...}]`).
- Use `client.v1.context.search` to retrieve the top match; the response object exposes a `contexts` attribute (a list) where each entry has a `content` attribute.
- After printing the top match, also write that same content into `/home/user/myproject/output.log` on a line beginning with `Top Match:`.

## Acceptance Criteria
- Project path: /home/user/myproject
- Script path: /home/user/myproject/rag_search.py
- Log file: /home/user/myproject/output.log
- The agent MUST read `run-id` from the `ZEALT_RUN_ID` environment variable and use the value `refund-policy-${run-id}.md` as the `metadata.file_name` for the ingested document.
- After running the script:
  - A document with `metadata.file_name = refund-policy-${run-id}.md` MUST be retrievable from the Alchemyst context engine via `v1.context.search` for the query `What is the refund policy?` with `scope="internal"` and `similarity_threshold=0.7`.
  - The log file MUST contain a line of the format `Top Match: <content>` where `<content>` includes the exact substring `30-day money back guarantee`.

