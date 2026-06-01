import argparse
from alchemyst import AlchemystAI

def main():
    parser = argparse.ArgumentParser(description="Alchemyst AI Memory CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a memory")
    add_parser.add_argument("--user-id", required=True, help="User ID")
    add_parser.add_argument("--session-id", required=True, help="Session ID")
    add_parser.add_argument("--content", required=True, help="Memory content")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search memories")
    search_parser.add_argument("--user-id", required=True, help="User ID")
    search_parser.add_argument("--session-id", required=True, help="Session ID")

    args = parser.parse_args()

    # Initialize the AlchemystAI client
    client = AlchemystAI()

    if args.command == "add":
        client.v1.context.memory.add(
            user_id=args.user_id,
            session_id=args.session_id,
            content=args.content
        )
    elif args.command == "search":
        result = client.v1.context.memory.search(
            user_id=args.user_id,
            session_id=args.session_id
        )
        # Iterate through the memories in the result and print their content
        for memory in result.memories:
            print(memory.content)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
