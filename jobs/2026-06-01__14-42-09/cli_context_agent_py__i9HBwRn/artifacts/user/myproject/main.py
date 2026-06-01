#!/usr/bin/env python3
"""Context-aware terminal assistant CLI.

Combines the Alchemyst AI Python SDK (alchemystai v0.10.0) as a context
engine with OpenAI as the answer-generating LLM.

Subcommands:
  ingest <file>     - ingest a local note file into the Alchemyst context store
  ask <question>    - retrieve grounding context from Alchemyst and ask OpenAI
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import sys
from pathlib import Path

from alchemyst_ai import AlchemystAI
from alchemyst_ai import APIStatusError
from openai import OpenAI


PROJECT_ROOT = Path("/home/user/myproject")
SOURCE_TAG = "cli-notes"


def _alchemyst_client() -> AlchemystAI:
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("ERROR: ALCHEMYST_AI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(2)
    return AlchemystAI(api_key=api_key)


def _openai_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(2)
    return OpenAI(api_key=api_key)


def _run_id() -> str:
    # ZEALT_RUN_ID namespaces concurrent runs so two parallel ingests do not
    # collide on Alchemyst's per-file_name uniqueness constraint.
    return os.environ.get("ZEALT_RUN_ID", "local")


def _resolve_path(rel_or_abs: str) -> Path:
    p = Path(rel_or_abs)
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p


def cmd_ingest(file_arg: str) -> int:
    path = _resolve_path(file_arg)
    if not path.is_file():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1

    contents = path.read_text(encoding="utf-8")
    stat = path.stat()
    last_modified = _dt.datetime.fromtimestamp(
        stat.st_mtime, tz=_dt.timezone.utc
    ).isoformat()

    run_id = _run_id()
    # Use the *relative* path under the project root plus the run id so
    # concurrent runs do not collide and the same run is idempotent.
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        rel = Path(path.name)
    file_name = f"{rel.as_posix()}-{run_id}"

    client = _alchemyst_client()

    def _do_add() -> object:
        return client.v1.context.add(
            context_type="resource",
            documents=[{"content": contents}],
            scope="internal",
            source=SOURCE_TAG,
            metadata={
                "file_name": file_name,
                "file_type": "text/markdown" if path.suffix.lower() == ".md" else "text/plain",
                "file_size": stat.st_size,
                "last_modified": last_modified,
            },
        )

    try:
        response = _do_add()
    except APIStatusError as exc:
        # 409 Conflict means the same (file_name, run_id) was already ingested.
        # Make the CLI idempotent by deleting any prior entries from this
        # source and retrying the add.
        if getattr(exc, "status_code", None) == 409:
            try:
                client.v1.context.delete(
                    organization_id=os.environ.get("ALCHEMYST_ORG_ID", ""),
                    source=SOURCE_TAG,
                    by_doc=True,
                )
            except APIStatusError:
                # If delete also fails we still treat the existing record as
                # a successful prior ingest -- nothing more to do.
                print(f"Document already present for file_name={file_name}; ingest is idempotent.")
                return 0
            try:
                response = _do_add()
            except APIStatusError as exc2:
                if getattr(exc2, "status_code", None) == 409:
                    print(f"Document already present for file_name={file_name}; ingest is idempotent.")
                    return 0
                raise
        else:
            raise

    context_id = getattr(response, "context_id", None)
    print(f"Ingested {path} as file_name={file_name} (context_id={context_id})")
    return 0


def _format_grounding(contexts: list) -> str:
    if not contexts:
        return ""
    parts = []
    for i, ctx in enumerate(contexts, start=1):
        content = getattr(ctx, "content", None)
        if not content:
            continue
        parts.append(f"[Chunk {i}]\n{content}")
    return "\n\n".join(parts)


def cmd_ask(question: str) -> int:
    if not question.strip():
        print("ERROR: question must not be empty.", file=sys.stderr)
        return 1

    alchemyst = _alchemyst_client()

    # Pull the most relevant context chunks from the Alchemyst context engine.
    search_response = alchemyst.v1.context.search(
        query=question,
        minimum_similarity_threshold=0.0,
        similarity_threshold=1.0,
        scope="internal",
    )
    contexts = list(getattr(search_response, "contexts", None) or [])
    grounding = _format_grounding(contexts)

    if grounding:
        system_prompt = (
            "You are a helpful assistant. Answer the user's question using ONLY "
            "the grounding context provided below when it is relevant. If the "
            "context does not contain an answer, say so honestly.\n\n"
            "=== GROUNDING CONTEXT ===\n"
            f"{grounding}\n"
            "=== END GROUNDING CONTEXT ==="
        )
    else:
        system_prompt = (
            "You are a helpful assistant. NOTE: No grounding context was "
            "retrieved from the knowledge base for this question; answer from "
            "general knowledge and make that limitation clear if relevant."
        )

    openai_client = _openai_client()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    completion = openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    answer = completion.choices[0].message.content or ""
    print(answer)
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Context-aware terminal assistant (Alchemyst + OpenAI).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_p = subparsers.add_parser("ingest", help="Ingest a note file into Alchemyst.")
    ingest_p.add_argument("file", help="Path to a local text/markdown file (relative to /home/user/myproject).")

    ask_p = subparsers.add_parser("ask", help="Ask a question grounded on ingested notes.")
    # nargs='+' lets users either quote the whole question OR pass it as
    # multiple trailing tokens that we join with spaces.
    ask_p.add_argument("question", nargs="+", help="The natural-language question to answer.")

    args = parser.parse_args(argv)

    if args.command == "ingest":
        return cmd_ingest(args.file)
    if args.command == "ask":
        question = " ".join(args.question)
        return cmd_ask(question)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
