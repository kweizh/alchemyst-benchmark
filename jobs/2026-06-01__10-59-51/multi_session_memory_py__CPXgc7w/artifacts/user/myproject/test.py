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

    client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY"))

    session_a = args.user_id + "-prefs"

    # 1. Write memory
    print(f"Adding memory for session {session_a}...")
    try:
        res = client.v1.context.memory.add(
            session_id=session_a,
            contents=[{
                "content": "User said: I'm vegan and allergic to peanuts",
                "metadata": {"user_id": args.user_id}
            }],
            metadata={"user_id": args.user_id}
        )
        print("Add response:", res)
    except Exception as e:
        print("Error adding memory:", e)

    # 2. Search memory
    print(f"Searching memory under session {args.session_id} for user {args.user_id}...")
    try:
        res = client.v1.context.search(
            query=args.query,
            minimum_similarity_threshold=0.0,
            similarity_threshold=1.0,
            scope="internal",
            user_id=args.user_id,
            mode="standard",
            metadata="true"
        )
        print("Search response:", res)
    except Exception as e:
        print("Error searching memory:", e)

if __name__ == "__main__":
    main()
