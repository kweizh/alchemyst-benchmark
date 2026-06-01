import os
import sys
import argparse
from alchemyst_ai import AlchemystAI

def main():
    parser = argparse.ArgumentParser(description="Alchemyst AI Team Memory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add subcommand
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--user", required=True, help="User ID")
    add_parser.add_argument("--session", required=True, help="Session ID")
    add_parser.add_argument("--content", required=True, help="Memory content")

    # Search subcommand
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--user", required=True, help="User ID")
    search_parser.add_argument("--session", required=True, help="Session ID")
    search_parser.add_argument("--query", required=True, help="Search query")

    args = parser.parse_args()

    try:
        api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
        client = AlchemystAI(api_key=api_key)

        if args.command == "add":
            client.v1.context.memory.add({
                "user_id": args.user,
                "session_id": args.session,
                "content": args.content
            })
        elif args.command == "search":
            result = client.v1.context.memory.search(
                user_id=args.user,
                session_id=args.session,
                query=args.query,
                limit=20
            )
            for mem in result.memories:
                if hasattr(mem, 'content'):
                    print(mem.content)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
