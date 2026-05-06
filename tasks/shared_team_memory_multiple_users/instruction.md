# Shared Team Memory with Alchemyst AI

## Background
Alchemyst AI provides memory management across sessions and users. Using the same `session_id` across different `user_id` values creates a shared memory space for team conversations. In this task, you will create a Python script to simulate a shared team discussion and verify that memories added by different users in the same session can be retrieved by another user.

## Requirements
- Initialize the Alchemyst AI client using the `ALCHEMYST_AI_API_KEY` environment variable.
- Add a memory for user `alice` in session `team_discussion_001` with content `Alice: Let's use PostgreSQL for the new database.`
- Add a memory for user `bob` in session `team_discussion_001` with content `Bob: I agree, PostgreSQL is a solid choice.`
- Perform a memory search for user `charlie` in session `team_discussion_001`.
- Write the `content` of all retrieved memories to `/home/user/project/shared_memory.json` as a JSON array of strings.

## Implementation Guide
1. Ensure you have the `alchemystai` Python package installed.
2. Create a script at `/home/user/project/test_shared_memory.py`.
3. Use `alchemyst.v1.context.memory.add()` to store the memories for `alice` and `bob`.
4. Use `alchemyst.v1.context.memory.search()` for `charlie` in the same session.
5. Extract the `content` attribute from the returned memories and dump them to `shared_memory.json`.
6. Run the script to generate the output file.

## Constraints
- Project path: `/home/user/project`
- Output file: `/home/user/project/shared_memory.json`
- Script path: `/home/user/project/test_shared_memory.py`