#!/usr/bin/env python3
"""
Memory-Aware Chat Assistant CLI.

Uses Alchemyst AI (alchemystai==0.10.0) for long-term memory and OpenAI for
chat completions. On every turn, retrieves relevant prior memories via
client.v1.context.search(scope="internal", ...) and persists the new
exchange via client.v1.context.memory.add(...).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, List

from alchemyst_ai import AlchemystAI
from openai import OpenAI


SYSTEM_PROMPT = (
    "You are a helpful assistant. Use the retrieved memories to personalize "
    "answers. When relevant facts about the user (such as their name, "
    "preferences, or dietary restrictions) appear in the retrieved memories, "
    "you MUST reuse them in your reply so the conversation feels continuous."
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Memory-aware chat assistant CLI")
    p.add_argument("--turns", required=True, help="Path to a JSON file: list of user message strings")
    p.add_argument("--user-id", required=True, dest="user_id")
    p.add_argument("--session-id", required=True, dest="session_id")
    return p.parse_args()


def load_turns(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        raise ValueError(f"--turns file {path!r} must be a JSON list of strings")
    return data


def retrieve_memories(
    client: AlchemystAI, query: str, user_id: str, session_id: str
) -> List[str]:
    """Search Alchemyst memory for snippets relevant to `query`.

    Uses client.v1.context.search(scope="internal", ...) -- the only retrieval
    API available in alchemystai v0.10.0. (There is NO memory.search method.)
    """
    snippets: List[str] = []
    try:
        resp = client.v1.context.search(
            query=query,
            minimum_similarity_threshold=0.0,
            similarity_threshold=1.0,
            scope="internal",
            user_id=user_id,
            metadata="true",
            mode="standard",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] context.search failed: {exc}", file=sys.stderr)
        return snippets

    contexts = getattr(resp, "contexts", None) or []
    # Sort by score descending if available, then take the top N.
    def _score(c: Any) -> float:
        s = getattr(c, "score", None)
        return float(s) if s is not None else 0.0

    contexts_sorted = sorted(contexts, key=_score, reverse=True)
    for ctx in contexts_sorted[:10]:
        content = getattr(ctx, "content", None)
        if isinstance(content, str) and content.strip():
            snippets.append(content.strip())
    return snippets


def build_openai_messages(memories: List[str], user_message: str) -> List[dict]:
    messages: List[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if memories:
        memory_block = "\n".join(f"- {m}" for m in memories)
        messages.append(
            {
                "role": "system",
                "content": (
                    "Relevant memories retrieved from prior conversation "
                    "(use these facts to personalize your reply):\n"
                    f"{memory_block}"
                ),
            }
        )
    messages.append({"role": "user", "content": user_message})
    return messages


def call_openai(openai_client: OpenAI, messages: List[dict]) -> str:
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    resp = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.4,
    )
    return (resp.choices[0].message.content or "").strip()


def persist_turn(
    client: AlchemystAI,
    user_id: str,
    session_id: str,
    turn_index: int,
    user_message: str,
    assistant_reply: str,
) -> None:
    """Persist the new exchange to Alchemyst memory.

    Uses client.v1.context.memory.add(...). Content includes BOTH the user
    message and the assistant reply so later searches can recover them.
    """
    combined = (
        f"User said: {user_message}\n"
        f"Assistant said: {assistant_reply}"
    )
    contents = [
        {
            "content": combined,
            "role": "memory",
            "metadata": {
                "message_id": f"{session_id}-turn-{turn_index}",
                "user_id": user_id,
                "session_id": session_id,
                "turn": turn_index,
            },
        }
    ]
    try:
        client.v1.context.memory.add(
            contents=contents,
            session_id=session_id,
            metadata={"group_name": [user_id, session_id]},
            extra_body={"user_id": user_id, "userId": user_id},
        )
    except Exception as exc:  # noqa: BLE001
        print(f"[warn] memory.add failed for turn {turn_index}: {exc}", file=sys.stderr)


def main() -> int:
    args = parse_args()

    alchemyst_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    run_id = os.environ.get("ZEALT_RUN_ID")

    if not alchemyst_key:
        print("ALCHEMYST_AI_API_KEY is not set", file=sys.stderr)
        return 2
    if not openai_key:
        print("OPENAI_API_KEY is not set", file=sys.stderr)
        return 2
    if not run_id:
        print("ZEALT_RUN_ID is not set", file=sys.stderr)
        return 2

    # Apply the run-id suffix so concurrent runs do not collide.
    user_id = f"{args.user_id}-{run_id}"
    session_id = f"{args.session_id}-{run_id}"

    turns = load_turns(args.turns)

    alchemyst_client = AlchemystAI(api_key=alchemyst_key)
    openai_client = OpenAI(api_key=openai_key)

    transcript: List[dict] = []

    for i, user_message in enumerate(turns):
        memories = retrieve_memories(alchemyst_client, user_message, user_id, session_id)
        messages = build_openai_messages(memories, user_message)
        assistant_reply = call_openai(openai_client, messages)
        if not assistant_reply:
            assistant_reply = "(no reply)"

        # Single-line print with the required prefix.
        safe_reply = assistant_reply.replace("\r", " ").replace("\n", " ").strip()
        if not safe_reply:
            safe_reply = "(no reply)"
        print(f"ASSISTANT[{i}]: {safe_reply}")
        sys.stdout.flush()

        persist_turn(
            alchemyst_client,
            user_id=user_id,
            session_id=session_id,
            turn_index=i,
            user_message=user_message,
            assistant_reply=assistant_reply,
        )

        transcript.append({"turn": i, "user": user_message, "assistant": assistant_reply})

    transcript_path = "/home/user/myproject/transcript.json"
    with open(transcript_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
