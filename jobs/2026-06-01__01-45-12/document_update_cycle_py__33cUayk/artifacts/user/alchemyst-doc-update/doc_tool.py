import os
import sys
import time
import argparse
from alchemyst_ai import AlchemystAI

def main():
    parser = argparse.ArgumentParser(description="Alchemyst AI Document Update Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--content", required=True)

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("--content", required=True)

    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--query", required=True)

    args = parser.parse_args()

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    run_id = os.environ.get("ZEALT_RUN_ID")

    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if not run_id:
        print("Error: ZEALT_RUN_ID not set", file=sys.stderr)
        sys.exit(1)

    client = AlchemystAI(api_key=api_key)
    file_name = f"refunds-{run_id}.md"

    if args.command == "add":
        client.v1.context.add(
            documents=[{"content": args.content, "metadata": {"file_name": file_name}}],
            context_type="resource",
            source="docs",
            scope="internal"
        )
    elif args.command == "update":
        # Delete half of update
        try:
            # Based on SDK inspection, organization_id and source are required.
            # metadata is passed via extra_body as it is not a direct parameter in delete signature.
            client.v1.context.delete(
                organization_id="",
                source="docs",
                by_doc=True,
                extra_body={"metadata": {"file_name": file_name}}
            )
        except Exception:
            # Proceed even if delete fails (e.g. document didn't exist)
            pass
        
        # Propagation delay
        time.sleep(2)
        
        # Add half of update
        client.v1.context.add(
            documents=[{"content": args.content, "metadata": {"file_name": file_name}}],
            context_type="resource",
            source="docs",
            scope="internal"
        )
    elif args.command == "search":
        # Based on SDK signature, minimum_similarity_threshold and similarity_threshold are required.
        # body_metadata is used to filter by file_name as metadata is a boolean Literal in search signature.
        result = client.v1.context.search(
            query=args.query,
            similarity_threshold=0.5,
            minimum_similarity_threshold=0.0,
            scope="internal",
            body_metadata={"file_name": file_name}
        )
        if result.contexts:
            for ctx in result.contexts:
                if ctx.content:
                    print(ctx.content)

if __name__ == "__main__":
    main()
