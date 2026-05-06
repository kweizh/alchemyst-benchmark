import sys
import os
from alchemystai import AlchemystAI

def main():
    api_key = os.getenv("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.")
        sys.exit(1)

    alchemyst = AlchemystAI(api_key=api_key)

    if len(sys.argv) < 2:
        print("Usage: python ticket_manager.py <command> [args]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        if len(sys.argv) != 5:
            print("Usage: python ticket_manager.py add <user_id> <session_id> <message>")
            sys.exit(1)
        user_id = sys.argv[2]
        session_id = sys.argv[3]
        message = sys.argv[4]
        alchemyst.v1.context.memory.add({
            "user_id": user_id,
            "session_id": session_id,
            "content": message
        })
    elif command == "get":
        if len(sys.argv) != 4:
            print("Usage: python ticket_manager.py get <user_id> <session_id>")
            sys.exit(1)
        user_id = sys.argv[2]
        session_id = sys.argv[3]
        result = alchemyst.v1.context.memory.search(user_id=user_id, session_id=session_id)
        if hasattr(result, 'memories'):
            for memory in result.memories:
                print(memory.content)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
