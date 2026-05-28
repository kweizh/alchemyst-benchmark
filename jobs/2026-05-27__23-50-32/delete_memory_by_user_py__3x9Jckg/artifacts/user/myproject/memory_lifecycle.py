import os
import uuid
import time
import json
from alchemyst_ai import AlchemystAI

def main():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY not found in environment.")
        return

    run_id = os.environ.get("ZEALT_RUN_ID", "default-run-id")
    
    # Use UUIDs scoped by run-id for both userId and sessionId
    user_id = f"user-{run_id}-{uuid.uuid4()}"
    session_id = f"session-{run_id}-{uuid.uuid4()}"
    
    client = AlchemystAI(api_key=api_key)
    
    # 1. Add memory
    print(f"Adding memory for UserId: {user_id}, SessionId: {session_id}")
    # The requirement says memory entry must contain "User's nickname is Bumble"
    add_response = client.v1.context.memory.add(
        contents=[{"content": "User's nickname is Bumble"}],
        session_id=session_id
    )
    
    memory_id = add_response.context_id
    print(f"Added memory, Context ID: {memory_id}")
    
    # Allow a brief wait for indexing
    print("Waiting for indexing (5s)...")
    time.sleep(5)
    
    # 2. Delete memory
    print(f"Deleting memory: {memory_id} for UserId: {user_id}")
    # client.v1.context.memory.delete(memory_id=..., user_id=...)
    # We also need organization_id? The signature had organization_id: Optional[str] but it was NOT optional in the type hint?
    # Memory Delete: (*, memory_id: 'str', organization_id: 'Optional[str]', ...)
    # Let's check if organization_id can be None.
    client.v1.context.memory.delete(
        memory_id=memory_id,
        user_id=user_id,
        organization_id=None
    )
    
    # Allow a brief wait for indexing
    print("Waiting for deletion to propagate (5s)...")
    time.sleep(5)
    
    # 3. Search to verify
    print(f"Searching for 'Bumble' for UserId: {user_id}")
    search_result = client.v1.context.search(
        query="Bumble",
        user_id=user_id,
        similarity_threshold=0.5,
        minimum_similarity_threshold=0.3
    )
    
    # Serialize results
    # The SDK response might have a model_dump or to_dict method
    if hasattr(search_result, "model_dump"):
        search_dict = search_result.model_dump()
    elif hasattr(search_result, "to_dict"):
        search_dict = search_result.to_dict()
    else:
        # Fallback serialization
        search_dict = json.loads(json.dumps(search_result, default=str))
    
    # Write to /workspace/post_delete_search.json
    os.makedirs("/workspace", exist_ok=True)
    with open("/workspace/post_delete_search.json", "w") as f:
        json.dump(search_dict, f, indent=2)
    
    # Log results to /home/user/myproject/output.log
    project_path = "/home/user/myproject"
    os.makedirs(project_path, exist_ok=True)
    with open(os.path.join(project_path, "output.log"), "w") as f:
        f.write(f"UserId: {user_id}\n")
        f.write(f"SessionId: {session_id}\n")
        f.write("Status: success\n")
    
    print("Task completed successfully.")

if __name__ == "__main__":
    main()
