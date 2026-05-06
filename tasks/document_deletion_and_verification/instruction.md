# Update Document in Alchemyst AI

## Background
Alchemyst AI triggers a 409 Conflict if you attempt to add a document with an existing `file_name` in its metadata. To update a document, you must first delete the old version by its `file_name` and then add the new version.
You have a Python project at `/home/user/alchemyst_project`.

## Requirements
Write a Python script `update_doc.py` that updates a document in Alchemyst AI.
- The script should use the `alchemyst_ai` Python package.
- It must define a function `update_document(client, file_name, new_content)`.
- The function should delete the existing document with the given `file_name`.
- Then it should add the new document with the new content and the same `file_name`.

## Implementation Guide
1. Go to `/home/user/alchemyst_project`.
2. Create `update_doc.py` with the required function.
3. The `delete` method can be called via `client.v1.context.delete(metadata={"file_name": file_name})`.
4. The `add` method can be called via `client.v1.context.add(documents=[{"content": new_content, "metadata": {"file_name": file_name}}], context_type="resource", source="docs", scope="internal")`.

## Constraints
- Project path: `/home/user/alchemyst_project`
- Use Python 3.
- The script should not execute anything if imported, only define the function.

## Integrations
- Alchemyst AI