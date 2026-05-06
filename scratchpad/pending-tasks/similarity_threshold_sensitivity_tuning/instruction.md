Your context engine is returning too many generic, loosely related documents when users ask highly specific technical questions, diluting the context window and confusing the LLM.

You need to modify an existing `v1.context.search` implementation to heavily restrict the retrieved chunks, ensuring high precision for a specific technical query.

**Constraints:**
- You MUST adjust the `similarity_threshold` parameter to a strict value of `0.85` or higher.
- Verify that the search results drop broad matches and only return exact or highly semantically similar chunks.