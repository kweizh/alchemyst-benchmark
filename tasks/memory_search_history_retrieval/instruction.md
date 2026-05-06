# Memory Search and History Retrieval

## Background
Alchemyst AI provides memory management capabilities to store and retrieve conversation history using `user_id` and `session_id`. In this task, you will use the Python SDK to add memories to a session and then retrieve the memory history.

## Requirements
Write a Python script that stores two specific memories for a user and then retrieves them, saving the output to a log file.

## Implementation Guide
1. Create a Python script at `/home/user/project/memory_test.py`.
2. Initialize the `AlchemystAI` client. It will automatically use the `ALCHEMYST_AI_API_KEY` environment variable.
3. Use `alchemyst.v1.context.memory.add` to add a memory with `user_id="test_user_777"`, `session_id="session_A"`, and `content="User allergy: peanuts"`.
4. Use `alchemyst.v1.context.memory.add` to add a second memory with `user_id="test_user_777"`, `session_id="session_A"`, and `content="User preference: vegetarian"`.
5. Use `alchemyst.v1.context.memory.search` to retrieve the memories for `user_id="test_user_777"` and `session_id="session_A"`.
6. Iterate over the retrieved memories and write their `content` to `/home/user/project/output.log`, one per line.

## Constraints
- Project path: `/home/user/project`
- Log file: `/home/user/project/output.log`
- Use the `alchemystai` Python package.