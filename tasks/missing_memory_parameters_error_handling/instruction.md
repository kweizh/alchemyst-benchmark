# Alchemyst AI Memory Error Handling

## Background
In Alchemyst AI, memory operations require both `user_id` and `session_id`. Omitting either of these parameters results in a `MISSING_PARAMETERS` error. It's important to properly handle these errors in an application.

## Requirements
- Create a Python script at `/home/user/test_memory_error.py`.
- The script must initialize the `AlchemystAI` client.
- The script must attempt to add a memory using `alchemyst.v1.context.memory.add` but intentionally omit the `user_id` parameter (only provide `session_id` and `content`).
- The script must catch the resulting exception.
- The script must write the string representation of the exception to `/home/user/error.log`.

## Implementation Guide
1. Import `AlchemystAI` from `alchemyst_ai`.
2. Initialize the client (you can use a dummy API key if the SDK allows, or the environment variable `ALCHEMYST_AI_API_KEY`).
3. Use a `try...except` block around `alchemyst.v1.context.memory.add({"session_id": "test_session", "content": "test content"})`.
4. In the `except` block, write `str(e)` to `/home/user/error.log`.

## Constraints
- Project path: /home/user
- Log file: /home/user/error.log
- Script path: /home/user/test_memory_error.py