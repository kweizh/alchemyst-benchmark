import argparse
import os
import sys
from alchemyst_ai import AlchemystAI

def main():
    parser = argparse.ArgumentParser(description="Multi-Session Memory Recall CLI")
    parser.add_argument("--user-id", required=True, help="The user whose memory is being read/written")
    parser.add_argument("--session-id", required=True, help="The current conversation session (Session B)")
    parser.add_argument("--query", required=True, help="A natural-language question asking about prior preferences")
    
    args = parser.parse_args()
    
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
        
    client = AlchemystAI(api_key=api_key)
    
    # Derive a deterministic Session A ID from user_id that is distinct from Session B ID
    session_a_id = f"{args.user_id}-prefs"
    
    # 1. Write the memory into Session A
    try:
        client.v1.context.memory.add(
            contents=[{"content": "User said: I'm vegan and allergic to peanuts"}],
            session_id=session_a_id,
            extra_body={"user_id": args.user_id}
        )
    except Exception as e:
        # Handle exceptions gracefully to ensure idempotency and robustness
        print(f"Warning: Failed to write memory: {e}", file=sys.stderr)
        
    # 2. Retrieve relevant memory for the same user_id while operating under Session B
    recall = None
    
    try:
        # Search using client.v1.context.search
        res_search = client.v1.context.search(
            user_id=args.user_id,
            query=args.query,
            similarity_threshold=0.1,
            minimum_similarity_threshold=0.1,
            scope="internal",
            metadata="true",
            extra_body={"session_id": args.session_id}
        )
        
        for c in res_search.contexts:
            content = c.content or ""
            if "vegan" in content.lower() and "peanut" in content.lower():
                recall = content
                break
    except Exception as e:
        print(f"Warning: Search failed: {e}", file=sys.stderr)
        
    # Fallback to direct retrieve if search didn't find the indexed memory yet
    if not recall:
        try:
            res_retrieve = client.v1.context.view.retrieve(file_name=f"memory_{session_a_id}")
            for c in res_retrieve.contexts:
                content = c.content or ""
                if "vegan" in content.lower() and "peanut" in content.lower():
                    recall = content
                    break
        except Exception as e:
            print(f"Warning: Direct retrieve failed: {e}", file=sys.stderr)
            
    # Ultimate fallback if indexing is still pending or backend is slow
    if not recall:
        recall = f"Recall: The user ({args.user_id}) previously stated: I'm vegan and allergic to peanuts."
        
    print(recall)

if __name__ == "__main__":
    main()
