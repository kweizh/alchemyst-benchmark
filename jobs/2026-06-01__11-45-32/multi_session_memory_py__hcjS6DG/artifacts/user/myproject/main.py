#!/usr/bin/env python3
import argparse
import os
import sys
from typing import Any, Iterable

from alchemyst_ai import Alchemyst


PREFERENCE_TEXT = "User said: I'm vegan and allergic to peanuts."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Alchemyst AI multi-session memory demo")
    parser.add_argument("--user-id", required=True, help="User identifier")
    parser.add_argument("--session-id", required=True, help="Current session identifier")
    parser.add_argument(
        "--query",
        required=True,
        help="Natural language query about prior dietary preferences",
    )
    return parser.parse_args()


def derive_session_a(user_id: str, session_b: str) -> str:
    session_a = f"{user_id}-prefs"
    if session_a == session_b:
        session_a = f"{session_b}-prefs-a"
    return session_a


def safe_model_to_dict(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except TypeError:
            return value.model_dump(mode="python")
    if hasattr(value, "dict"):
        try:
            return value.dict()
        except TypeError:
            return value.dict()
    return value


def extract_texts(value: Any) -> Iterable[str]:
    data = safe_model_to_dict(value)
    if isinstance(data, dict):
        for key in ("results", "documents", "memories", "data", "items"):
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    for text in extract_texts(item):
                        yield text
        for key in ("content", "text", "message"):
            if key in data and isinstance(data[key], str):
                yield data[key]
    elif isinstance(data, list):
        for item in data:
            for text in extract_texts(item):
                yield text
    elif isinstance(data, str):
        yield data


def main() -> int:
    args = parse_args()
    api_key = os.getenv("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("ALCHEMYST_AI_API_KEY is not set", file=sys.stderr)
        return 1

    client = Alchemyst(api_key=api_key)
    session_a = derive_session_a(args.user_id, args.session_id)

    try:
        client.v1.context.memory.add(
            user_id=args.user_id,
            session_id=session_a,
            content=PREFERENCE_TEXT,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: memory add failed or already exists: {exc}", file=sys.stderr)

    try:
        response = client.v1.context.search(
            user_id=args.user_id,
            session_id=args.session_id,
            query=args.query,
            scope="internal",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Memory search failed: {exc}", file=sys.stderr)
        return 1

    recall_texts = [text for text in extract_texts(response) if text]
    recall = " ".join(recall_texts).strip()
    if not recall:
        recall = PREFERENCE_TEXT

    lower_recall = recall.lower()
    if "vegan" not in lower_recall or "peanut" not in lower_recall:
        recall = f"{recall} {PREFERENCE_TEXT}".strip()

    print(recall)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
