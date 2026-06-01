#!/usr/bin/env python3
"""SyllabAI Assistant: Course-Aware Q&A CLI with Alchemyst AI Context Engine."""

import argparse
import os
import sys
import time

from alchemyst_ai import AlchemystAI
from openai import OpenAI


def get_alchemyst_client() -> AlchemystAI:
    """Create an Alchemyst AI client using the ALCHEMYST_AI_API_KEY env var."""
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return AlchemystAI(api_key=api_key)


def get_openai_client() -> OpenAI:
    """Create an OpenAI client using the OPENAI_API_KEY env var."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return OpenAI(api_key=api_key)


def cmd_ingest(args):
    """Ingest a syllabus markdown file into the Alchemyst context engine."""
    course_id = args.course_id
    syllabus_path = args.syllabus

    # Read the syllabus file
    try:
        with open(syllabus_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {syllabus_path}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    if not content.strip():
        print("Error: Syllabus file is empty.", file=sys.stderr)
        sys.exit(1)

    client = get_alchemyst_client()

    # Derive file_name from course_id to make it unique per ingestion
    file_name = f"syllabus-{course_id}"

    # Build metadata with group_name containing both "syllabus" and the course_id
    metadata = {
        "file_name": file_name,
        "group_name": ["syllabus", course_id],
    }

    # Build the document
    documents = [{"content": content}]

    try:
        response = client.v1.context.add(
            context_type="resource",
            documents=documents,
            scope="internal",
            source="syllabus",
            metadata=metadata,
        )
        print(f"Ingested syllabus for course: {course_id}")
    except Exception as e:
        error_str = str(e)
        # Handle 409 Conflict gracefully - document already exists
        if "409" in error_str or "Conflict" in error_str:
            # Update file_name to avoid collision and retry
            file_name_updated = f"syllabus-{course_id}-{int(time.time())}"
            metadata["file_name"] = file_name_updated
            try:
                response = client.v1.context.add(
                    context_type="resource",
                    documents=documents,
                    scope="internal",
                    source="syllabus",
                    metadata=metadata,
                )
                print(f"Ingested syllabus for course: {course_id}")
            except Exception as retry_e:
                print(f"Error ingesting syllabus: {retry_e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Error ingesting syllabus: {e}", file=sys.stderr)
            sys.exit(1)


def cmd_ask(args):
    """Ask a question about a course using the Alchemyst context engine and OpenAI."""
    course_id = args.course_id
    question = args.question

    client = get_alchemyst_client()

    # Search for relevant context chunks, filtered by course_id
    try:
        search_response = client.v1.context.search(
            query=question,
            minimum_similarity_threshold=0.3,
            similarity_threshold=1.0,
            scope="internal",
            body_metadata={"group_name": ["syllabus", course_id]},
        )
    except Exception as e:
        print(f"Error searching context: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract context chunks from the response
    contexts = search_response.contexts or []
    context_text = ""
    if contexts:
        context_parts = []
        for ctx in contexts:
            if ctx.content:
                context_parts.append(ctx.content)
        context_text = "\n\n---\n\n".join(context_parts)

    if not context_text:
        context_text = "No relevant syllabus context was found."

    # Build the prompt for OpenAI
    system_prompt = (
        "You are a helpful course assistant. Answer the student's question based on "
        "the provided syllabus context. If the context doesn't contain enough information "
        "to answer the question, say so clearly. Be concise and student-friendly."
    )

    user_prompt = f"Course syllabus context:\n\n{context_text}\n\nStudent question: {question}"

    # Call OpenAI Chat Completions
    openai_client = get_openai_client()

    try:
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        answer = completion.choices[0].message.content
        print(f"Answer: {answer}")
    except Exception as e:
        print(f"Error calling OpenAI: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="SyllabAI Assistant: Course-Aware Q&A CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Ingest subcommand
    ingest_parser = subparsers.add_parser("ingest", help="Ingest a syllabus file")
    ingest_parser.add_argument("syllabus", help="Path to the syllabus Markdown file")
    ingest_parser.add_argument(
        "--course-id", required=True, help="Unique course identifier"
    )

    # Ask subcommand
    ask_parser = subparsers.add_parser("ask", help="Ask a question about a course")
    ask_parser.add_argument("question", help="The question to ask")
    ask_parser.add_argument(
        "--course-id", required=True, help="Unique course identifier"
    )

    args = parser.parse_args()

    if args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "ask":
        cmd_ask(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()