# Multi-Day Customer Support Ticket

## Background
You are building a customer support bot using Alchemyst AI. The bot needs to remember user context across multiple days for the same support ticket. You need to write a Python script that stores user messages into Alchemyst AI memory and retrieves them.

## Requirements
Write a Python script `/home/user/app/ticket_manager.py` with the following CLI commands:
1. `python ticket_manager.py add <user_id> <session_id> <message>`: Stores the message in Alchemyst AI memory for the specified user and session.
2. `python ticket_manager.py get <user_id> <session_id>`: Retrieves all memories for the user and session, and prints them to stdout, each on a new line.

## Implementation Guide
- Use the `alchemystai` Python package.
- Initialize `AlchemystAI` with the `ALCHEMYST_AI_API_KEY` environment variable.
- For `add`, use `alchemyst.v1.context.memory.add({"user_id": user_id, "session_id": session_id, "content": message})`.
- For `get`, use `alchemyst.v1.context.memory.search(user_id=user_id, session_id=session_id)`. Iterate over the `memories` attribute of the result and print the `content` of each memory.

## Constraints
- Project path: `/home/user/app`
- The script must be named `ticket_manager.py`.
- You don't need to call an LLM, just store and retrieve the raw messages.