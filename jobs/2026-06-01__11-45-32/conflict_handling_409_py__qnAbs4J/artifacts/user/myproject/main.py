import json
import os
import sys

from alchemyst_ai import APIStatusError, AlchemystAI


def build_payload(run_id: str) -> tuple[dict, dict, str]:
    source = f"alchemyst://context/ingest/{run_id}"
    metadata = {
        "file_name": f"alchemyst_ingest_{run_id}.txt",
        "file_type": "text/plain",
    }
    document = {
        "content": f"Idempotent ingest payload for run {run_id}.",
    }
    return metadata, document, source


def main() -> int:
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    run_id = os.environ.get("ZEALT_RUN_ID")

    if not api_key:
        print("Missing ALCHEMYST_AI_API_KEY environment variable.", file=sys.stderr)
        return 1
    if not run_id:
        print("Missing ZEALT_RUN_ID environment variable.", file=sys.stderr)
        return 1

    client = AlchemystAI(api_key=api_key, max_retries=0)
    metadata, document, source = build_payload(run_id)

    try:
        client.v1.context.add(
            context_type="resource",
            documents=[document],
            scope="internal",
            source=source,
            metadata=metadata,
        )
        print('RESULT: {"status": "ok", "conflict_resolved": false}')
        return 0
    except APIStatusError as exc:
        if exc.status_code != 409:
            raise

    print("Conflict detected (409). Deleting existing document and retrying.")
    client.v1.context.delete(source=source, by_doc=True)
    client.v1.context.add(
        context_type="resource",
        documents=[document],
        scope="internal",
        source=source,
        metadata=metadata,
    )
    print('RESULT: {"status": "ok", "conflict_resolved": true}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
