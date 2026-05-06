# Context Arithmetic: Union Filtering with Alchemyst AI

## Background
Alchemyst AI uses Context Arithmetic to filter documents. By default, specifying multiple tags in `groupName` performs an INTERSECTION (AND). To perform a UNION (OR) across different groups (e.g., retrieving documents from either `["eng", "v1"]` OR `["eng", "v2"]`), you must perform multiple searches and combine the results, or search a broader group and filter locally.

## Requirements
Write a Python script `/home/user/project/search_union.py` that:
1. Initializes the Alchemyst AI client using the `ALCHEMYST_AI_API_KEY` environment variable.
2. Ingests three documents (context_type: 'resource', source: 'docs', scope: 'internal') with the following content and metadata:
   - Doc 1: Content: "Engineering V1 Architecture", Metadata: `file_name`: "v1.md", `group_name`: `["eng", "v1"]`
   - Doc 2: Content: "Engineering V2 Architecture", Metadata: `file_name`: "v2.md", `group_name`: `["eng", "v2"]`
   - Doc 3: Content: "Sales Playbook", Metadata: `file_name`: "sales.md", `group_name`: `["sales"]`
3. Implements a function `union_search(query: str, groups: list[list[str]]) -> list[str]` that takes a query and a list of group combinations, performs searches for each group combination (with `similarity_threshold=0.1` and `scope='internal'`), and returns a deduplicated list of document contents.
4. Calls `union_search("Architecture", [["eng", "v1"], ["eng", "v2"]])` and writes the resulting JSON array of strings to `/home/user/project/output.json`.

## Constraints
- Project path: `/home/user/project`
- Output file: `/home/user/project/output.json`
- The output JSON file must contain exactly the two engineering document contents.