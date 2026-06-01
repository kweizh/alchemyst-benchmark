#!/usr/bin/env python3
"""Context-aware terminal assistant using Alchemyst AI + OpenAI."""

import os
import sys

import alchemyst_ai
from alchemyst_ai import AlchemystAI
from openai import OpenAI


def get_alchemyst_client() -> AlchemystAI:
    api_key = os.environ["ALCHEMYST_AI_API_KEY"]
    return AlchemystAI(api_key=api_key)


def get_openai_client() -> OpenAI:
    api_key = os.environ["OPENAI_API_KEY"]
    return OpenAI(api_key=api_key)


def get_zealt_run_id() -> str:
    return os.environ.get("ZEALT_RUN_ID", "default")


def cmd_ingest(file_path: str) -> None:
    """Ingest a local file into the Alchemyst context engine."""
    # Resolve relative paths from the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(file_path):
        full_path = os.path.join(project_dir, file_path)
    else:
        full_path = file_path

    full_path = os.path.normpath(full_path)

    if not os.path.isfile(full_path):
        print(f"Error: file not found: {full_path}", file=sys.stderr)
        sys.exit(1)

    with open(full_path, "r", encoding="utf-8") as f:
        content = f.read()

    file_size = os.path.getsize(full_path)
    basename = os.path.basename(file_path)
    zealt_run_id = get_zealt_run_id()

    # Namespace file_name with ZEALT_RUN_ID to avoid 409 conflicts across runs
    unique_file_name = f"{basename}-{zealt_run_id}"

    client = get_alchemyst_client()

    try:
        response = client.with_options(max_retries=0).v1.context.add(
            context_type="resource",
            documents=[{"content": content}],
            scope="internal",
            source="cli-notes",
            metadata={
                "file_name": unique_file_name,
                "file_type": "text/markdown" if file_path.endswith(".md") else "text/plain",
                "file_size": file_size,
            },
        )
        print(f"Ingested '{file_path}' successfully (context_id: {response.context_id})")
    except alchemyst_ai.APIStatusError as e:
        if e.status_code == 409:
            print(f"Document '{unique_file_name}' already exists in Alchemyst (idempotent)")
        else:
            print(f"Error ingesting file: {e}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error ingesting file: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_ask(question: str) -> None:
    """Ask a question grounded on ingested context."""
    client = get_alchemyst_client()

    # Search Alchemyst for relevant context
    search_result = client.v1.context.search(
        query=question,
        scope="internal",
        similarity_threshold=1.0,
        minimum_similarity_threshold=0.3,
    )

    contexts = search_result.contexts or []

    # Build grounding block from retrieved contexts
    if contexts:
        context_block = "\n\n".join(
            f"[Context {i+1}]: {ctx.content}"
            for i, ctx in enumerate(contexts)
            if ctx.content
        )
    else:
        context_block = None

    # Build OpenAI prompt
    openai_client = get_openai_client()

    if context_block:
        system_message = (
            "You are a helpful assistant. Answer the user's question based on the "
            "following context retrieved from the user's notes. If the context does "
            "not contain enough information to answer the question, say so honestly.\n\n"
            f"{context_block}"
        )
    else:
        system_message = (
            "You are a helpful assistant. No relevant context was found in the "
            "user's notes to answer this question. Answer based on your general "
            "knowledge, but note that no supporting context was available."
        )

    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question},
        ],
    )

    answer = completion.choices[0].message.content
    print(answer)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <ingest|ask> <args...>", file=sys.stderr)
        sys.exit(1)

    subcommand = sys.argv[1]

    if subcommand == "ingest":
        if len(sys.argv) < 3:
            print("Usage: python3 main.py ingest <file>", file=sys.stderr)
            sys.exit(1)
        file_path = sys.argv[2]
        cmd_ingest(file_path)

    elif subcommand == "ask":
        if len(sys.argv) < 3:
            print("Usage: python3 main.py ask <question>", file=sys.stderr)
            sys.exit(1)
        # Join all remaining args as the question (allows unquoted multi-word questions)
        question = " ".join(sys.argv[2:])
        cmd_ask(question)

    else:
        print(f"Unknown subcommand: {subcommand}", file=sys.stderr)
        print("Usage: python3 main.py <ingest|ask> <args...>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()