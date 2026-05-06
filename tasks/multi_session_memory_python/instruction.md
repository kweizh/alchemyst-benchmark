# Alchemyst AI Python Memory Script

## Background
Create a Python script that uses the Alchemyst AI Python SDK to manage multi-session memories for a user.

## Requirements
- You have a Python project at `/home/user/myproject`.
- The `alchemystai` package is already installed in the environment.
- Create a script `memory_test.py` that:
  1. Initializes the `AlchemystAI` client using the `ALCHEMYST_AI_API_KEY` environment variable.
  2. Adds a memory for `user_id="user_123"` and `session_id="session_A"` with content `"User prefers Python over JavaScript."`.
  3. Adds another memory for `user_id="user_123"` and `session_id="session_B"` with content `"User likes the Django framework."`.
  4. Searches for memories for `user_id="user_123"` and `session_id="session_A"`.
  5. Prints the retrieved memory content to standard output.
  6. Deletes the memory for `user_id="user_123"` and `session_id="session_A"`.

## Constraints
- Project path: `/home/user/myproject`
- The script must be named `memory_test.py`.
- The script must run without errors and print the memory content from `session_A`.