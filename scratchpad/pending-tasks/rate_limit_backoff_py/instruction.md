# Rate Limit Resilience with Alchemyst AI Python SDK

## Background
Production RAG systems frequently issue bursts of search requests against the Alchemyst AI Context Engine. When request volume exceeds the platform limit (1000 requests/minute), the API responds with HTTP `429 RateLimit`. A resilient client must transparently retry these requests using exponential backoff so end users see no failures.

Your job is to write a Python script that exercises the Alchemyst AI Python SDK's built-in retry capabilities by ingesting a small corpus and then hammering the search endpoint with a burst of concurrent requests. The script must accurately track retry behavior and emit a structured report.

## Requirements
- Ingest exactly 3 documents into the Alchemyst AI Context Engine using `client.v1.context.add` (Python SDK).
- Each ingested document must use a per-run-unique `file_name` in metadata (UUID-based) so concurrent task runs do not collide with `409 Conflict`.
- After ingestion, fire exactly 20 concurrent `client.v1.context.search` requests against the same query using threads or asyncio.
- Use the SDK's documented retry capability (e.g., `client.with_options(max_retries=...)`) to automatically retry `429 RateLimit` responses with exponential backoff.
- Set `max_retries` to at least 5 so transient rate-limit responses are handled gracefully.
- For every search attempt (including each retry), record whether it observed a 429 and the wall-clock time spent waiting before its successful response.
- Write a JSON report to `/home/user/myproject/backoff_report.json` summarizing the burst.
- All 20 search requests must eventually succeed.

## Implementation Hints
- Read the run-id from the `ZEALT_RUN_ID` environment variable and use it inside each document's `file_name` (e.g., `f"rl-doc-{run_id}-{uuid4().hex}.txt"`).
- Read `ALCHEMYST_AI_API_KEY` from the environment (already set in the task environment).
- Concurrency can be achieved with `concurrent.futures.ThreadPoolExecutor`, `asyncio.gather` with `AsyncAlchemystAI`, or a similar primitive.
- Use `client.with_options(max_retries=...)` (or pass `max_retries=` to the client constructor) to control the SDK's automatic retry of `429` responses.
- To capture whether a 429 was observed without disabling retries, you can wrap each call with `time.perf_counter()` around the SDK call. A request that takes substantially longer than the baseline median latency very likely retried; alternatively, you can subclass/monkeypatch the SDK's HTTP layer or use `with_raw_response` plus a manual loop. Either approach is acceptable as long as the final report is accurate.
- The simplest robust approach is: perform each search in a manual try/except loop using `client.with_options(max_retries=0)` so you fully control the backoff and can count 429s precisely; use `alchemyst_ai.RateLimitError` to detect 429s; sleep using exponential backoff (e.g., `base * 2**attempt + jitter`); record the maximum backoff delay actually slept across all attempts.
- Whichever strategy you choose, the four fields in the report must be populated truthfully.

## Acceptance Criteria
- Project path: /home/user/myproject
- Log file: /home/user/myproject/backoff_report.json
- Entrypoint command: `python3 /home/user/myproject/run.py`
- The script must read `run-id` from the `ZEALT_RUN_ID` environment variable and use it to disambiguate document `file_name` values.
- Exactly 3 documents are ingested via `client.v1.context.add`; each document has a metadata `file_name` containing the current `run-id`.
- Exactly 20 concurrent search requests are issued.
- The file `/home/user/myproject/backoff_report.json` must exist after the script completes successfully.
- The JSON file must contain exactly these top-level fields with the documented types:
  ```json
  {
    "total_requests": number,
    "successful_requests": number,
    "encountered_429": number,
    "max_backoff_delay_seconds": number
  }
  ```
- `total_requests` must equal `20`.
- `successful_requests` must equal `total_requests` (all 20 search calls eventually succeed).
- `encountered_429` must be a non-negative integer (0 is acceptable if no rate limit was hit during the run).
- `max_backoff_delay_seconds` must be a non-negative number (0 is acceptable if no retry was required).

