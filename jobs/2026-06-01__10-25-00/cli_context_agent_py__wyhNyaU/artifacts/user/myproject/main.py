#!/usr/bin/env python3
import os
import sys
import datetime
import mimetypes
from alchemyst_ai import AlchemystAI, ConflictError
from openai import OpenAI

# Base directory of the project
BASE_DIR = "/home/user/myproject"

def main():
    # 1. Subcommand validation
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <subcommand> [args...]", file=sys.stderr)
        print("Subcommands: ingest <file>, ask <question>", file=sys.stderr)
        sys.exit(1)

    subcommand = sys.argv[1]

    # 2. Environment variable validation
    alchemyst_api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if not alchemyst_api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # 3. Handle subcommands
    if subcommand == "ingest":
        if len(sys.argv) < 3:
            print("Error: Please provide a file to ingest.", file=sys.stderr)
            print("Usage: python3 main.py ingest <file>", file=sys.stderr)
            sys.exit(1)

        input_path = sys.argv[2]
        # Resolve relative path from BASE_DIR
        if not os.path.isabs(input_path):
            filepath = os.path.join(BASE_DIR, input_path)
        else:
            filepath = input_path

        if not os.path.exists(filepath):
            print(f"Error: File not found at {filepath}", file=sys.stderr)
            sys.exit(1)

        # Read the file content
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {e}", file=sys.stderr)
            sys.exit(1)

        # Retrieve file stats for metadata
        try:
            file_size = os.path.getsize(filepath)
            
            # Guess mime type
            file_type, _ = mimetypes.guess_type(filepath)
            if not file_type:
                file_type = "text/markdown" if filepath.endswith(".md") else "text/plain"
                
            # Get last modified timestamp as ISO string
            mtime = os.path.getmtime(filepath)
            last_modified = datetime.datetime.fromtimestamp(mtime).isoformat()
        except Exception as e:
            print(f"Error retrieving file stats: {e}", file=sys.stderr)
            sys.exit(1)

        # Retrieve ZEALT_RUN_ID
        zealt_run_id = os.environ.get("ZEALT_RUN_ID", "")
        basename = os.path.basename(filepath)
        
        # Incorporate ZEALT_RUN_ID into the file_name metadata
        if zealt_run_id:
            file_name_metadata = f"notes/{basename}-{zealt_run_id}"
        else:
            file_name_metadata = f"notes/{basename}"

        # Initialize Alchemyst AI Client
        client = AlchemystAI(api_key=alchemyst_api_key)

        try:
            # Call Alchemyst AI to add the document
            client.v1.context.add(
                context_type="resource",
                documents=[{"content": content}],
                scope="internal",
                source="cli-notes",
                metadata={
                    "file_name": file_name_metadata,
                    "file_size": float(file_size),
                    "file_type": file_type,
                    "last_modified": last_modified
                }
            )
            print(f"Successfully ingested {filepath} into Alchemyst Context Engine.")
            sys.exit(0)
        except ConflictError as e:
            # Handle ConflictError gracefully for idempotency / re-runnability
            print(f"File {filepath} already ingested (ConflictError handled gracefully).")
            sys.exit(0)
        except Exception as e:
            print(f"Error adding context to Alchemyst: {e}", file=sys.stderr)
            sys.exit(1)

    elif subcommand == "ask":
        if len(sys.argv) < 3:
            print("Error: Please provide a question to ask.", file=sys.stderr)
            print("Usage: python3 main.py ask <question>", file=sys.stderr)
            sys.exit(1)

        # Join trailing tokens to support both quoted and unquoted questions
        question = " ".join(sys.argv[2:])

        # Initialize clients
        alchemyst_client = AlchemystAI(api_key=alchemyst_api_key)
        openai_client = OpenAI(api_key=openai_api_key)

        # Search context
        try:
            search_response = alchemyst_client.v1.context.search(
                query=question,
                scope="internal",
                minimum_similarity_threshold=0.0,
                similarity_threshold=0.7
            )
        except Exception as e:
            print(f"Error searching context in Alchemyst: {e}", file=sys.stderr)
            sys.exit(1)

        # Extract and concatenate content
        contexts = search_response.contexts or []
        content_blocks = []
        for ctx in contexts:
            if ctx.content:
                content_blocks.append(ctx.content)

        # Prepare prompt for OpenAI
        if content_blocks:
            grounding_context = "\n---\n".join(content_blocks)
            user_content = (
                f"Grounding Context:\n{grounding_context}\n\n"
                f"Question: {question}\n\n"
                f"Answer:"
            )
        else:
            user_content = (
                f"Grounding Context: [No relevant context was found in Alchemyst AI]\n\n"
                f"Question: {question}\n\n"
                f"Answer:"
            )

        system_content = (
            "You are a context-aware terminal assistant. Answer the user's question "
            "using the provided grounding context. If the grounding context is empty or "
            "does not contain the answer, answer based on your general knowledge but "
            "clearly mention that no relevant context was found in the database."
        )

        # Call OpenAI Chat Completions
        try:
            chat_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content}
                ]
            )
            answer = chat_response.choices[0].message.content
            print(answer)
            sys.exit(0)
        except Exception as e:
            print(f"Error calling OpenAI API: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        print(f"Error: Unknown subcommand '{subcommand}'", file=sys.stderr)
        print("Available subcommands: ingest, ask", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
