The enterprise knowledge base contains thousands of documents mixed between engineering, marketing, and support, across multiple product versions. 

You need to perform a context search using the Python SDK that retrieves technical documentation strictly applicable to the new v2 product release.

**Constraints:**
- You MUST utilize "Context Arithmetic" metadata filtering to perform an intersection search.
- The search query must strictly return results that are tagged with BOTH `['eng', 'v2']` in their `group_name` metadata, completely excluding `['eng', 'v1']` or standalone `['v2']` documents.