#!/usr/bin/env python3
import os
import sys
import json
import argparse
from alchemyst_ai import AlchemystAI
from openai import OpenAI

def main():
    parser = argparse.ArgumentParser(description="Memory-Aware Chat Assistant CLI")
    parser.add_argument("--turns", required=True, help="Path to the JSON file containing user turns")
    parser.add_argument("--user-id", required=True, help="The Alchemyst memory user ID")
    parser.add_argument("--session-id", required=True, help="The Alchemyst memory session ID")
    args = parser.parse_args()

    # 1. Validate API keys and environment variables
    alchemyst_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not alchemyst_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print("Error: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    zealt_run_id = os.environ.get("ZEALT_RUN_ID")
    if not zealt_run_id:
        print("Error: ZEALT_RUN_ID environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # 2. Suffix IDs with ZEALT_RUN_ID
    run_id_user_id = f"{args.user_id}-{zealt_run_id}"
    run_id_session_id = f"{args.session_id}-{zealt_run_id}"

    # 3. Initialize SDK clients
    try:
        alchemyst_client = AlchemystAI(api_key=alchemyst_key)
    except Exception as e:
        print(f"Error initializing AlchemystAI client: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        openai_client = OpenAI(api_key=openai_key)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Load turns JSON
    try:
        with open(args.turns, "r", encoding="utf-8") as f:
            turns = json.load(f)
    except Exception as e:
        print(f"Error reading turns file '{args.turns}': {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(turns, list):
        print("Error: The turns JSON file must contain a list of strings.", file=sys.stderr)
        sys.exit(1)

    transcript = []

    # 5. Process each turn in order
    for turn_index, user_message in enumerate(turns):
        # Step 5a: Search Alchemyst memories relevant to the current user message
        contexts = []
        try:
            # We use minimum_similarity_threshold=0.0 and similarity_threshold=1.0
            # to retrieve all potential context matches, then filter by session_id in Python.
            search_res = alchemyst_client.v1.context.search(
                query=user_message,
                minimum_similarity_threshold=0.0,
                similarity_threshold=1.0,
                scope="internal",
                user_id=run_id_user_id,
                metadata="true"
            )
            if search_res.contexts:
                contexts.extend(search_res.contexts)
        except Exception as e:
            print(f"Warning: Alchemyst message search failed on turn {turn_index}: {e}", file=sys.stderr)

        try:
            # To ensure prior turns of the same conversation are always recoverable,
            # we also do a history search with query="User said"
            search_res_hist = alchemyst_client.v1.context.search(
                query="User said",
                minimum_similarity_threshold=0.0,
                similarity_threshold=1.0,
                scope="internal",
                user_id=run_id_user_id,
                metadata="true"
            )
            if search_res_hist.contexts:
                contexts.extend(search_res_hist.contexts)
        except Exception as e:
            print(f"Warning: Alchemyst history search failed on turn {turn_index}: {e}", file=sys.stderr)

        # Filter contexts by session_id in Python
        target_file_name = f"memory_{run_id_session_id}"
        relevant_contexts = []
        for c in contexts:
            if c.metadata and c.metadata.get("file_name") == target_file_name:
                if c.content:
                    relevant_contexts.append(c.content)

        # Step 5b: Build prompt for OpenAI Chat Completions
        system_instruction = "You are a helpful assistant. Use the retrieved memories to personalize answers."
        if relevant_contexts:
            # Deduplicate the contexts while preserving order
            unique_contexts = list(dict.fromkeys(relevant_contexts))
            context_str = "\n".join([f"- {ctx}" for ctx in unique_contexts])
            system_instruction += f"\n\nRetrieved memories (prior conversation context):\n{context_str}"

        # Step 5c: Call OpenAI Chat Completions
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            assistant_reply = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI on turn {turn_index}: {e}", file=sys.stderr)
            assistant_reply = "I'm sorry, I encountered an error processing your request."

        # Step 5d: Print reply to stdout with the exact prefix ASSISTANT[<turn_index>]:
        # Replace newlines with spaces to ensure exactly one line to stdout
        clean_reply = assistant_reply.replace("\n", " ").strip()
        print(f"ASSISTANT[{turn_index}]: {clean_reply}")

        # Step 5e: Persist the new turn to Alchemyst memory
        memory_content = f"User said: {user_message}\nAssistant said: {assistant_reply}"
        try:
            alchemyst_client.v1.context.memory.add(
                contents=[{"content": memory_content}],
                session_id=run_id_session_id,
                extra_body={"user_id": run_id_user_id}
            )
        except Exception as e:
            print(f"Warning: Failed to persist memory to Alchemyst on turn {turn_index}: {e}", file=sys.stderr)

        # Step 5f: Add to transcript
        transcript.append({
            "turn": turn_index,
            "user": user_message,
            "assistant": assistant_reply
        })

    # 6. Write transcript to /home/user/myproject/transcript.json
    try:
        transcript_path = "/home/user/myproject/transcript.json"
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript, f, indent=2)
    except Exception as e:
        print(f"Error writing transcript: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
