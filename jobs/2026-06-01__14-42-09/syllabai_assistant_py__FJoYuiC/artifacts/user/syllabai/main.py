#!/usr/bin/env python3
"""SyllabAI Assistant: Course-Aware Q&A CLI.

Uses the Alchemyst AI Context Engine for ingesting and retrieving syllabus
chunks scoped per-course, and OpenAI Chat Completions for composing
student-friendly answers.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, List


def _get_alchemyst_client():
    from alchemyst_ai import AlchemystAI

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return AlchemystAI(api_key=api_key)


def _get_openai_client():
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=api_key)


def _file_name_for_course(course_id: str) -> str:
    return f"syllabus-{course_id}.md"


def ingest(path: str, course_id: str) -> None:
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    client = _get_alchemyst_client()

    file_name = _file_name_for_course(course_id)
    group_name = ["syllabus", course_id]

    document = {
        "content": content,
        "metadata": {
            "file_name": file_name,
            "group_name": group_name,
        },
    }

    try:
        client.v1.context.add(
            documents=[document],
            context_type="resource",
            source="syllabus",
            scope="internal",
            metadata={
                "file_name": file_name,
                "group_name": group_name,
            },
        )
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        # Gracefully handle conflicts so re-running the ingest is safe.
        if "409" in msg or "Conflict" in msg.lower():
            pass
        else:
            print(f"Error during ingest: {exc}", file=sys.stderr)
            sys.exit(1)

    print(f"Ingested syllabus for course: {course_id}")


def _extract_chunk_text(item: Any) -> str:
    """Pull a text snippet out of a search result item which may be
    a dict, a pydantic model, or another object shape."""
    if item is None:
        return ""
    if isinstance(item, str):
        return item
    # pydantic model -> dict
    if hasattr(item, "model_dump"):
        try:
            item = item.model_dump()
        except Exception:  # noqa: BLE001
            pass
    if isinstance(item, dict):
        for key in ("content", "text", "chunk", "page_content", "document"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value
            if isinstance(value, dict):
                nested = _extract_chunk_text(value)
                if nested:
                    return nested
        # Fallback to stringifying the whole dict
        return str(item)
    return str(item)


def _collect_contexts(response: Any) -> List[str]:
    """Extract a list of context chunk strings from a search response."""
    candidates: List[Any] = []

    if response is None:
        return []

    if hasattr(response, "model_dump"):
        try:
            response = response.model_dump()
        except Exception:  # noqa: BLE001
            pass

    if isinstance(response, dict):
        for key in ("contexts", "results", "data", "documents", "matches"):
            value = response.get(key)
            if isinstance(value, list):
                candidates = value
                break
        if not candidates:
            # Maybe response itself contains a single payload
            candidates = [response]
    elif isinstance(response, list):
        candidates = response
    else:
        candidates = [response]

    chunks: List[str] = []
    for item in candidates:
        text = _extract_chunk_text(item)
        if text:
            chunks.append(text)
    return chunks


def ask(question: str, course_id: str) -> None:
    client = _get_alchemyst_client()

    try:
        search_response = client.v1.context.search(
            query=question,
            similarity_threshold=0.5,
            scope="internal",
            metadata={"group_name": ["syllabus", course_id]},
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error during search: {exc}", file=sys.stderr)
        sys.exit(1)

    contexts = _collect_contexts(search_response)
    context_block = "\n\n---\n\n".join(contexts) if contexts else "(No syllabus context found.)"

    system_prompt = (
        "You are SyllabAI, a helpful course assistant. Answer the student's "
        "question using ONLY the provided syllabus context whenever it is "
        "relevant. Be concise, accurate, and student-friendly. If the answer "
        "is not present in the context, say what you can infer or state that "
        "the syllabus does not specify."
    )

    user_prompt = (
        f"Course ID: {course_id}\n\n"
        f"Syllabus context:\n{context_block}\n\n"
        f"Student question: {question}\n\n"
        "Answer the student's question based on the syllabus context above."
    )

    openai_client = _get_openai_client()
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error calling OpenAI: {exc}", file=sys.stderr)
        sys.exit(1)

    answer = (completion.choices[0].message.content or "").strip()
    # Normalize to a single line so the `Answer:` prefix stays on one line.
    answer_one_line = " ".join(answer.split())
    print(f"Answer: {answer_one_line}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="syllabai",
        description="Course-aware Q&A over a syllabus via Alchemyst AI + OpenAI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a syllabus markdown file.")
    ingest_parser.add_argument("path", help="Path to the syllabus markdown file.")
    ingest_parser.add_argument(
        "--course-id", required=True, help="Unique course identifier."
    )

    ask_parser = subparsers.add_parser("ask", help="Ask a question about the syllabus.")
    ask_parser.add_argument("question", help="The natural-language question to ask.")
    ask_parser.add_argument(
        "--course-id", required=True, help="Unique course identifier."
    )

    args = parser.parse_args()

    if args.command == "ingest":
        ingest(args.path, args.course_id)
    elif args.command == "ask":
        ask(args.question, args.course_id)
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
