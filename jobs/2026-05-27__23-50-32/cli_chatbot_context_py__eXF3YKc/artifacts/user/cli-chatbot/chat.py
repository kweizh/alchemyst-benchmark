import os
import sys
import argparse
from alchemyst_ai import AlchemystAI
from openai import OpenAI

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description="Context-Aware CLI Chatbot")
    parser.add_argument("question", help="The user message")
    args = parser.parse_args()

    # Read environment variables
    run_id = os.environ.get("ZEALT_RUN_ID")
    alchemyst_api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if not run_id:
        print("Error: ZEALT_RUN_ID environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not alchemyst_api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Derive userId and sessionId
    user_id = f"cli-user-{run_id}"
    session_id = f"cli-session-{run_id}"

    # Initialize clients
    # AlchemystAI client automatically uses ALCHEMYST_AI_API_KEY if not provided
    alchemyst = AlchemystAI(api_key=alchemyst_api_key)
    openai = OpenAI(api_key=openai_api_key)

    # 1. Search Alchemyst for snippets relevant to the current message
    snippets = []
    try:
        search_response = alchemyst.v1.context.search(
            query=args.question,
            user_id=user_id,
            minimum_similarity_threshold=0.0,
            similarity_threshold=1.0,
            extra_body={"session_id": session_id}
        )
        if search_response.contexts:
            snippets = [ctx.content for ctx in search_response.contexts if ctx.content]
    except Exception:
        # Fallback if search fails or no context exists yet
        pass

    # 2. Build OpenAI chat completion request
    system_content = "You are a helpful assistant."
    if snippets:
        system_content += "\n\nUse the following context from previous parts of this conversation to inform your answer:\n"
        system_content += "\n---\n".join(snippets)

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": args.question}
    ]

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        assistant_reply = completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Print only the assistant's reply text on stdout
    print(assistant_reply)

    # 4. Store the new turn back into Alchemyst
    try:
        turn_text = f"User: {args.question}\nAssistant: {assistant_reply}"
        alchemyst.v1.context.memory.add(
            session_id=session_id,
            contents=[{"content": turn_text}],
            extra_body={"user_id": user_id}
        )
    except Exception:
        # Silently fail for storage to keep stdout clean for the reply
        pass

if __name__ == "__main__":
    main()
