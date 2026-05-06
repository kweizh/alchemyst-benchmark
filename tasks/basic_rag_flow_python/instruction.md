# Basic RAG Flow with Alchemyst AI (Python)

## Background
Create a Python script that uses Alchemyst AI to store a specific policy document and retrieve it using context search to answer a question.

## Requirements
- Read the policy document from `/home/user/project/policy.txt`.
- Use the Alchemyst AI Python SDK to add the document to the context engine.
- Assign the document the `context_type="resource"`, `source="documentation"`, and `scope="internal"`.
- Include `file_name: "policy.txt"` in the metadata.
- Perform a context search for the query "What is the return policy for electronics?" using a `similarity_threshold` of 0.7 and `scope="internal"`.
- Write the content of the first matching context chunk to `/home/user/project/output.txt`.

## Implementation Guide
1. Create a Python script `/home/user/project/rag.py`.
2. Initialize `AlchemystAI` with the `ALCHEMYST_AI_API_KEY` from the environment.
3. Read the contents of `/home/user/project/policy.txt`.
4. Call `client.v1.context.add()` to store the document.
5. Call `client.v1.context.search()` with the query.
6. Extract the content from the first item in the returned `contexts` list and write it to `/home/user/project/output.txt`.

## Constraints
- Project path: `/home/user/project`
- Log file: `/home/user/project/output.txt`
- You must use the `alchemystai` Python package.
- The `ALCHEMYST_AI_API_KEY` environment variable will be provided.