import os
from alchemyst_ai import AlchemystAI

def main():
    # 1. Initialize the AlchemystAI client
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.")
        return

    client = AlchemystAI(api_key=api_key)

    user_id = "user_123"
    session_a = "session_A"
    session_b = "session_B"

    # 2. Add memory for session_A
    print(f"Adding memory for {user_id} and {session_a}...")
    client.v1.context.memory.add(
        session_id=session_a,
        contents=[{"content": "User prefers Python over JavaScript."}],
        extra_body={"user_id": user_id}
    )

    # 3. Add memory for session_B
    print(f"Adding memory for {user_id} and {session_b}...")
    client.v1.context.memory.add(
        session_id=session_b,
        contents=[{"content": "User likes the Django framework."}],
        extra_body={"user_id": user_id}
    )

    # 4. Search for memories for user_123 and session_A
    # We use a query that matches the content of session_A.
    print(f"Searching for memories for {user_id} and {session_a}...")
    search_response = client.v1.context.search(
        query="Python",
        user_id=user_id,
        minimum_similarity_threshold=0.1,
        similarity_threshold=1.0,
        body_metadata={"session_id": session_a}
    )

    # 5. Print the retrieved memory content
    print("Retrieved memory content:")
    if search_response.contexts:
        for context in search_response.contexts:
            print(context.content)
    else:
        print("No memories found.")

    # 6. Delete the memory for user_123 and session_A
    # Using session_a as memory_id based on SDK patterns.
    print(f"Deleting memory for {user_id} and {session_a}...")
    client.v1.context.memory.delete(
        memory_id=session_a,
        organization_id=None,
        user_id=user_id
    )
    print("Memory deleted successfully.")

if __name__ == "__main__":
    main()
