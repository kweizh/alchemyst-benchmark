# Alchemyst AI Document Update Cycle (TypeScript)

## Background
Alchemyst AI is a Context Engine that manages documents and memory. When adding a document to the context engine, if a document with the same `file_name` in its metadata already exists, the API returns a `409 Conflict` error. To update a document, you must first delete the existing version before adding the new one.

## Requirements
- Write a TypeScript script that demonstrates the full document update cycle in Alchemyst AI.
- The target document's `file_name` must be `policy-${run-id}.md` and its `group_name` must be `["update-test-${run-id}"]`, where `${run-id}` is read from the `ZEALT_RUN_ID` environment variable.
- Step 1: The script must first add the initial document with the content: `Old refund policy: 30-day refunds.`
- Step 2: The script must then update the document to have the new content: `Updated refund policy: 60-day refunds.` by first deleting the old version and then adding the new version with the exact same `file_name` and `group_name`.
- Step 3: The script must log a success message to a file upon completion.

## Implementation Hints
- Initialize the Alchemyst SDK using the `ALCHEMYST_AI_API_KEY` environment variable.
- Read the `ZEALT_RUN_ID` environment variable to construct the target `file_name` (`policy-${run-id}.md`) and `group_name` (`["update-test-${run-id}"]`).
- Use `client.v1.context.add` to add the initial document.
- Since Alchemyst AI rejects duplicate `file_name`s, use the SDK's context methods to delete the old document before adding the new one in Step 2.
- Ensure your TypeScript script handles asynchronous operations and potential delays properly.
- Write the final success message to `/home/user/alchemyst-task/output.log`.

## Acceptance Criteria
- Project path: `/home/user/alchemyst-task`
- Ensure the script is executed and the full cycle (add -> delete -> add) is performed.
- Log file: `/home/user/alchemyst-task/output.log`
- The log file must contain the text `Update cycle successful: policy-${run-id}.md`.
- The context engine must contain the new document content (`Updated refund policy: 60-day refunds.`) and not the old content when searching within the `update-test-${run-id}` group.

