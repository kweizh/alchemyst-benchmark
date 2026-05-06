# Rate Limit Resilience with Exponential Backoff

## Background
You are building an application using the Alchemyst AI Python SDK. During peak loads, your search operations may hit the 429 Rate Limit (1000 requests/minute). You need to implement a robust search loop with exponential backoff.

## Requirements
- Create a Python script `/home/user/app/search_loop.py`.
- Initialize the `AlchemystAI` client.
- Implement a function `robust_search(query)` that calls `alchemyst.v1.context.search(query=query, similarity_threshold=0.7, scope='internal')`.
- Wrap the search call in a manual exponential backoff retry loop: if an exception occurs whose string representation contains '429', retry up to 3 times. The delay should start at 1 second and double each retry (1s, 2s, 4s).
- The script must call `robust_search("What is the refund policy?")` 5 times in a row.
- Write the number of successful searches to `/home/user/app/output.log` in the format `Successful searches: 5`.

## Implementation Guide
1. Create `/home/user/app/search_loop.py`.
2. Import `os`, `time`, and `AlchemystAI` from `alchemyst_ai`.
3. Implement the `robust_search` function with the retry logic.
4. Execute the loop 5 times and log the success count.

## Constraints
- Project path: `/home/user/app`
- Log file: `/home/user/app/output.log`