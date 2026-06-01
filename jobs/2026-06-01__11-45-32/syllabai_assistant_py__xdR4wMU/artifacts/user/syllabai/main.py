#!/usr/bin/env python3
import argparse
import os
import sys
from typing import Iterable, List

from alchemyst_ai import AlchemystAI
from openai import OpenAI


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _extract_contents(results: Iterable) -> List[str]:
    contents: List[str] = []
    for item in results:
        content = None
        if isinstance(item, dict):
            content = item.get("content") or item.get("text") or item.get("chunk")
        else:
            content = getattr(item, "content", None) or getattr(item, "text", None) or getattr(
                item, "chunk", None
            )
        if content:
            contents.append(content)
    return contents


def _get_search_results(search_response) -> List[str]:
    if isinstance(search_response, dict):
        results = search_response.get("data") or search_response.get("results") or []
    else:
        results = getattr(search_response, "data", None) or getattr(search_response, "results", None) or []
    return _extract_contents(results)


def ingest_syllabus(path: str, course_id: str) -> None:
    _get_env("ZEALT_RUN_ID")
    api_key = _get_env("ALCHEMYST_AI_API_KEY")

    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()

    file_name = f"syllabus-{course_id}"
    documents = [
        {
            "content": content,
            "metadata": {
                "file_name": file_name,
                "group_name": ["syllabus", course_id],
            },
        }
    ]

    client = AlchemystAI(api_key=api_key)
    try:
        client.v1.context.add(
            documents=documents,
            context_type="resource",
            source="syllabus",
            scope="internal",
        )
    except Exception as exc:  # noqa: BLE001
        status_code = getattr(exc, "status_code", None) or getattr(exc, "status", None)
        if status_code == 409 or "409" in str(exc):
            print(f"Syllabus already ingested for course: {course_id}")
            return
        raise

    print(f"Ingested syllabus for course: {course_id}")


def ask_question(question: str, course_id: str) -> None:
    _get_env("ZEALT_RUN_ID")
    alchemyst_key = _get_env("ALCHEMYST_AI_API_KEY")
    openai_key = _get_env("OPENAI_API_KEY")

    context_client = AlchemystAI(api_key=alchemyst_key)
    search_response = context_client.v1.context.search(
        query=question,
        similarity_threshold=0.5,
        scope="internal",
        metadata={"group_name": ["syllabus", course_id]},
    )

    context_chunks = _get_search_results(search_response)
    context_text = "\n\n".join(context_chunks) if context_chunks else "No relevant syllabus context found."

    prompt = (
        "You are a helpful course assistant. Use the syllabus context to answer the student's question. "
        "If the context is insufficient, say so clearly.\n\n"
        f"Syllabus context:\n{context_text}\n\n"
        f"Student question: {question}"
    )

    openai_client = OpenAI(api_key=openai_key)
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You answer questions about a course syllabus."},
            {"role": "user", "content": prompt},
        ],
    )

    answer = completion.choices[0].message.content.strip()
    print(f"Answer: {answer}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SyllabAI Assistant CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest a course syllabus")
    ingest_parser.add_argument("path", help="Path to the syllabus markdown file")
    ingest_parser.add_argument("--course-id", required=True, help="Course identifier")

    ask_parser = subparsers.add_parser("ask", help="Ask a question about a course")
    ask_parser.add_argument("question", help="Question to ask about the syllabus")
    ask_parser.add_argument("--course-id", required=True, help="Course identifier")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ingest":
        ingest_syllabus(args.path, args.course_id)
    elif args.command == "ask":
        ask_question(args.question, args.course_id)
    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
