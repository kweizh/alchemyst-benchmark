import argparse
import json
import os
import sys
from typing import Any, Iterable, List

from alchemyst_ai import AlchemystAI
from openai import OpenAI


def _extract_memory_snippets(search_response: Any, max_items: int = 5) -> List[str]:
    items: Iterable[Any] = []
    if hasattr(search_response, "data"):
        items = search_response.data or []
    elif isinstance(search_response, dict) and "data" in search_response:
        items = search_response.get("data") or []

    snippets: List[str] = []
    for item in items:
        content = None
        if hasattr(item, "content"):
            content = item.content
        elif isinstance(item, dict):
            content = item.get("content") or item.get("text")
        if content:
            snippets.append(str(content).strip())
        if len(snippets) >= max_items:
            break
    return snippets


def _build_messages(user_message: str, memory_snippets: List[str]) -> List[dict]:
    system_lines = [
        "You are a helpful assistant. Use the retrieved memories to personalize answers.",
    ]
    if memory_snippets:
        system_lines.append("Retrieved memories:")
        for snippet in memory_snippets:
            system_lines.append(f"- {snippet}")
    system_content = "\n".join(system_lines)
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message},
    ]


def run_chat(turns_path: str, user_id: str, session_id: str) -> None:
    run_id = os.getenv("ZEALT_RUN_ID")
    if not run_id:
        raise RuntimeError("ZEALT_RUN_ID environment variable is required.")

    alchemyst_api_key = os.getenv("ALCHEMYST_AI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not alchemyst_api_key:
        raise RuntimeError("ALCHEMYST_AI_API_KEY environment variable is required.")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required.")

    with open(turns_path, "r", encoding="utf-8") as handle:
        turns_data = json.load(handle)

    if not isinstance(turns_data, list) or not all(isinstance(t, str) for t in turns_data):
        raise ValueError("Turns JSON must be a list of user message strings.")

    user_id = f"{user_id}-{run_id}"
    session_id = f"{session_id}-{run_id}"

    alchemyst_client = AlchemystAI(api_key=alchemyst_api_key)
    openai_client = OpenAI(api_key=openai_api_key)

    transcript: List[dict] = []
    for index, user_message in enumerate(turns_data):
        search_response = alchemyst_client.v1.context.search(
            scope="internal",
            user_id=user_id,
            session_id=session_id,
            query=user_message,
        )
        memory_snippets = _extract_memory_snippets(search_response)
        messages = _build_messages(user_message, memory_snippets)

        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        assistant_reply = completion.choices[0].message.content.strip()

        alchemyst_client.v1.context.memory.add(
            user_id=user_id,
            session_id=session_id,
            content=f"User said: {user_message}\nAssistant said: {assistant_reply}",
        )

        print(f"ASSISTANT[{index}]: {assistant_reply}")
        transcript.append(
            {
                "turn": index,
                "user": user_message,
                "assistant": assistant_reply,
            }
        )

    transcript_path = os.path.join(os.path.dirname(__file__), "transcript.json")
    with open(transcript_path, "w", encoding="utf-8") as handle:
        json.dump(transcript, handle, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Memory-aware chat assistant using Alchemyst AI and OpenAI."
    )
    parser.add_argument("--turns", required=True, help="Path to turns JSON file")
    parser.add_argument("--user-id", required=True, help="User id for memory scope")
    parser.add_argument("--session-id", required=True, help="Session id for memory scope")
    args = parser.parse_args()

    try:
        run_chat(args.turns, args.user_id, args.session_id)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
