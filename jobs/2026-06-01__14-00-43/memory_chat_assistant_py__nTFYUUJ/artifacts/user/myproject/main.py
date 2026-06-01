#!/usr/bin/env python3
"""
Memory-Aware Chat Assistant CLI

Uses Alchemyst AI (v0.10.0) for long-term memory and OpenAI for chat completions.
On every user turn:
  1. Retrieves relevant memories via client.v1.context.search(scope="internal", ...)
  2. Builds an OpenAI prompt with retrieved memory context
  3. Calls OpenAI Chat Completions for the assistant reply
  4. Persists the turn to Alchemyst via client.v1.context.memory.add(...)
"""

import argparse
import json
import os
import sys

from alchemyst_ai import AlchemystAI
from openai import OpenAI


def load_turns(path: str) -> list[str]:
    """Load the list of user messages from a JSON file."""
    with open(path, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array of strings in {path}")
    return data


def search_memories(client: AlchemystAI, query: str, user_id: str) -> list[str]:
    """Search Alchemyst for memories relevant to the query, scoped internally to the user.

    Uses client.v1.context.search (NOT client.v1.context.memory.search which
    does not exist in v0.10.0).
    """
    try:
        response = client.v1.context.search(
            minimum_similarity_threshold=0.1,
            query=query,
            similarity_threshold=1.0,
            scope="internal",
            user_id=user_id,
            metadata="true",
            mode="standard",
        )
        contexts = response.contexts or []
        # Sort by score descending (most relevant first)
        contexts.sort(key=lambda c: c.score if c.score is not None else 0.0, reverse=True)
        # Extract content strings, filtering out None
        memory_snippets = [c.content for c in contexts if c.content is not None]
        return memory_snippets
    except Exception as e:
        # If search fails (e.g., no memories yet), return empty list
        print(f"[WARN] Memory search failed: {e}", file=sys.stderr)
        return []


def add_memory(client: AlchemystAI, session_id: str, user_id: str, content: str) -> None:
    """Persist a memory turn to Alchemyst.

    Uses client.v1.context.memory.add with the run-id-suffixed session_id
    and includes user_id in metadata for retrieval scoping.
    """
    try:
        client.v1.context.memory.add(
            contents=[{"content": content}],
            session_id=session_id,
            metadata={"group_name": [user_id]},
        )
    except Exception as e:
        print(f"[WARN] Memory add failed: {e}", file=sys.stderr)


def build_openai_messages(user_message: str, memory_snippets: list[str]) -> list[dict]:
    """Build the OpenAI Chat Completions messages with system prompt and memory context."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Use the retrieved memories to personalize answers. "
                "If the user has previously shared personal information (name, preferences, dietary restrictions, etc.), "
                "reference that information naturally in your responses. Always be consistent with what the user has told you before."
            ),
        }
    ]

    if memory_snippets:
        # Include retrieved memories as context
        memory_text = "\n\n".join(memory_snippets[:10])  # Limit to top 10 snippets
        messages.append(
            {
                "role": "system",
                "content": f"Retrieved memories from earlier in the conversation:\n{memory_text}",
            }
        )

    messages.append({"role": "user", "content": user_message})
    return messages


def call_openai(openai_client: OpenAI, messages: list[dict]) -> str:
    """Call OpenAI Chat Completions and return the assistant reply."""
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=512,
        temperature=0.7,
    )
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Memory-Aware Chat Assistant CLI")
    parser.add_argument("--turns", required=True, help="Path to JSON file with list of user messages")
    parser.add_argument("--user-id", required=True, help="Alchemyst memory user id")
    parser.add_argument("--session-id", required=True, help="Alchemyst memory session id")
    args = parser.parse_args()

    # Read API keys from environment
    alchemyst_api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    run_id = os.environ.get("ZEALT_RUN_ID", "")

    if not alchemyst_api_key:
        print("ERROR: ALCHEMYST_AI_API_KEY environment variable is not set", file=sys.stderr)
        sys.exit(1)
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set", file=sys.stderr)
        sys.exit(1)

    # Suffix user_id and session_id with run-id to avoid collisions across concurrent runs
    effective_user_id = f"{args.user_id}-{run_id}" if run_id else args.user_id
    effective_session_id = f"{args.session_id}-{run_id}" if run_id else args.session_id

    # Initialize clients
    alchemyst_client = AlchemystAI(api_key=alchemyst_api_key)
    openai_client = OpenAI(api_key=openai_api_key)

    # Load turns
    turns = load_turns(args.turns)

    transcript = []

    for i, user_message in enumerate(turns):
        # Step 1: Retrieve relevant memories from Alchemyst
        memory_snippets = search_memories(
            alchemyst_client,
            query=user_message,
            user_id=effective_user_id,
        )

        # Step 2 & 3: Build prompt and call OpenAI
        messages = build_openai_messages(user_message, memory_snippets)
        assistant_reply = call_openai(openai_client, messages)

        # Step 4: Persist the turn to Alchemyst memory
        # Content includes both the user message and assistant reply so later
        # searches can recover the full conversational context.
        memory_content = f"User said: {user_message}\nAssistant said: {assistant_reply}"
        add_memory(
            alchemyst_client,
            session_id=effective_session_id,
            user_id=effective_user_id,
            content=memory_content,
        )

        # Print the assistant reply with the required prefix
        print(f"ASSISTANT[{i}]: {assistant_reply}")

        # Record in transcript
        transcript.append({
            "turn": i,
            "user": user_message,
            "assistant": assistant_reply,
        })

    # Write transcript.json
    transcript_path = "/home/user/myproject/transcript.json"
    with open(transcript_path, "w") as f:
        json.dump(transcript, f, indent=2)


if __name__ == "__main__":
    main()