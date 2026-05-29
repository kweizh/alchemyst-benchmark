# Multi-Session Memory with Alchemyst AI Python SDK

## Background
Alchemyst AI provides cross-session user memory management. You will create a Python CLI script that demonstrates storing a user preference in one session and retrieving it in a different session using the `alchemystai` Python SDK.

## Requirements
- Create a Python script that accepts user ID, two different session IDs, and a preference string as arguments.
- Use the Alchemyst AI Python SDK (`alchemystai`) to add the preference to the user's memory in Session A.
- Then, use the SDK to search/retrieve memory in Session B for the same user, querying for the preference.
- The script must print the retrieved memory content to standard output.

## Implementation Hints
- Read the API key from the `ALCHEMYST_AI_API_KEY` environment variable.
- Initialize the Alchemyst AI client.
- Use the memory management endpoints (e.g., `client.v1.context.memory.add` and `client.v1.context.memory.search`) to store and retrieve the preference.
- Both `userId` and `sessionId` are strictly required for memory operations.
- Ensure you wait briefly or handle any eventual consistency if needed, though typically it's fast.
- Use Python's `argparse` to handle the CLI arguments.

## Acceptance Criteria
- Project path: /home/user/alchemyst-memory
- Command: python3 run.py
- The command input argument format: `--user-id <user_id> --session-a <session_a_id> --session-b <session_b_id> --preference <preference_text>`
- The stdout should print the retrieved memory in the format: `Retrieved: <memory_content>` (the content should contain the preference text).

