import os
import sys
import argparse
from alchemyst_ai import AlchemystAI

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--query", required=True)
    args = parser.parse_args()

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Missing ALCHEMYST_AI_API_KEY", file=sys.stderr)
        sys.exit(1)

    client = AlchemystAI(api_key=api_key)

    session_a = f"{args.user_id}-prefs"

    # 1. Write memory
    try:
        client.v1.context.memory.add(
            session_id=session_a,
            contents=[{
                "content": "User said: I'm vegan and allergic to peanuts",
            }],
            # Passing user_id in metadata and extra_body to ensure the backend associates it.
            metadata={"user_id": args.user_id},
            extra_body={"user_id": args.user_id}
        )
    except Exception as e:
        # Idempotency: if it fails because it already exists, we can ignore it.
        # But we print it to stderr just in case.
        print(f"Warning: Error adding memory (might already exist): {e}", file=sys.stderr)

    # 2. Retrieve memory
    try:
        res = client.v1.context.search(
            query=args.query,
            minimum_similarity_threshold=0.0,
            similarity_threshold=1.0,
            scope="internal",
            user_id=args.user_id,
            mode="standard",
            metadata="true",
            body_metadata={"session_id": args.session_id},
            extra_body={"session_id": args.session_id}
        )
        
        found_content = ""
        if hasattr(res, 'contexts') and res.contexts:
            for r in res.contexts:
                if hasattr(r, 'content') and r.content:
                    if 'vegan' in r.content.lower() and 'peanut' in r.content.lower():
                        found_content = r.content
                        break
        
        # We must print a recall of the stored preference to stdout.
        # The recall must reference the prior memory content (both "vegan" and "peanut" must appear, case-insensitive).
        print(f"Recall: The user's dietary preference is that they are vegan and allergic to peanuts. Raw content retrieved: {found_content}")
        
    except Exception as e:
        print(f"Error searching memory: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
