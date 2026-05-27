# Scope-Filtered Context Search with the Alchemyst AI Python SDK

## Background
[Alchemyst AI](https://getalchemystai.com/) is a Context Engine that organises ingested documents along several dimensions. One of those dimensions is `scope`, an enum with the values `internal` and `external` (default `internal`). Documents stored under one scope must not surface when a search is filtered by the other scope.

In this task you will use the official Python SDK (`alchemystai` package, imported as `alchemyst_ai`) to demonstrate this scope partitioning end-to-end against the real Alchemyst Cloud API.

## Requirements
- Write a Python 3.11 script that, in a single execution:
  1. Reads the `ZEALT_RUN_ID` environment variable and uses it (together with random UUID suffixes) to build collision-free `file_name` values so the script can be re-run safely.
  2. Ingests **four** documents via `client.v1.context.add(...)`:
     - Two documents with `scope="internal"`, whose content includes the marker `MARKER_INTERNAL_<run-id>`.
     - Two documents with `scope="external"`, whose content includes the marker `MARKER_EXTERNAL_<run-id>`.
     Each document's content should be a short, semantically-related paragraph (e.g. about a company knowledge-base entry) so that a single semantic search query can match all four before scope filtering is applied.
  3. Performs **two** searches via `client.v1.context.search(...)` against the same query string, one with `scope="internal"` and one with `scope="external"`.
  4. Writes a summary of the two searches to `/workspace/scope_report.json` using the schema described under *Acceptance Criteria*.
- The script must use the real Alchemyst Cloud API (no mocking). The `ALCHEMYST_AI_API_KEY` environment variable will be available in the container.

## Implementation Hints
- Install and import the SDK: `pip install alchemystai`, then `from alchemyst_ai import AlchemystAI`.
- Construct the client with `AlchemystAI(api_key=os.environ["ALCHEMYST_AI_API_KEY"])`.
- For each `add` call, set `context_type="resource"`, a meaningful `source` string, the appropriate `scope` value, and a `metadata` dict whose `file_name` is unique per run (include `ZEALT_RUN_ID` and a UUID suffix).
- For the two search calls, reuse the same `query` string, use a low-to-moderate `similarity_threshold` (e.g. `0.5`) so the documents are reliably returned, and only change the `scope` value between calls. The Alchemyst engine partitions results strictly by scope, so an `internal` search must not return `external` chunks and vice versa.
- `client.v1.context.search(...)` returns a Pydantic response object; convert it via `.model_dump()` / `.to_dict()` or iterate `result.contexts` to extract `id` and `content` fields.
- Make sure to flush/close the file after writing JSON, and exit with a non-zero status if any API call fails.

## Acceptance Criteria
- Project path: `/workspace`
- Script entrypoint: `python3 /workspace/run_scope_search.py`
- Output file: `/workspace/scope_report.json` containing a single JSON object with the following shape:
  ```json
  {
    "query": "<the query string used for both searches>",
    "run_id": "<value of ZEALT_RUN_ID>",
    "internal": {
      "count": <number of items returned by the internal-scope search>,
      "results": [
        { "id": "<context id>", "content": "<chunk content excerpt>" }
      ]
    },
    "external": {
      "count": <number of items returned by the external-scope search>,
      "results": [
        { "id": "<context id>", "content": "<chunk content excerpt>" }
      ]
    }
  }
  ```
- Both `internal.results` and `external.results` arrays must be non-empty.
- Each item in `internal.results` must contain the marker `MARKER_INTERNAL_<run-id>` in its `content` and must NOT contain `MARKER_EXTERNAL_<run-id>`.
- Each item in `external.results` must contain the marker `MARKER_EXTERNAL_<run-id>` in its `content` and must NOT contain `MARKER_INTERNAL_<run-id>`.
- `internal.count` and `external.count` must equal the lengths of their respective `results` arrays.
- All `file_name` metadata values created by the run must include the `ZEALT_RUN_ID` value as a substring so concurrent runs do not collide.

