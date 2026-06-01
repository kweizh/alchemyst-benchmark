import os
import sys
import json
from alchemyst_ai import AlchemystAI, APIStatusError

def main():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
        
    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        print("Error: ZEALT_RUN_ID environment variable not set", file=sys.stderr)
        sys.exit(1)

    # Namespace identifiers
    file_name = f"file_{run_id}.txt"
    source = f"file_{run_id}.txt"  # Set source to be the same as file_name so delete works perfectly

    client = AlchemystAI(api_key=api_key, max_retries=0)

    conflict_detected = False
    res = None

    try:
        # First attempt
        res = client.v1.context.add(
            context_type="resource",
            documents=[{"content": f"Idempotent ingest document for run {run_id}"}],
            scope="internal",
            source=source,
            metadata={
                "file_name": file_name,
                "file_size": 1024,
                "file_type": "text/plain",
                "last_modified": "2026-06-01T10:45:10Z"
            }
        )
        
        # Check if response returned 409 in body
        if res and (getattr(res, "status_code", None) == 409 or getattr(res, "detail", None) == "Conflict"):
            conflict_detected = True

    except APIStatusError as e:
        if e.status_code == 409:
            conflict_detected = True
        else:
            # Re-raise any other API error to exit with non-zero status
            raise

    if conflict_detected:
        print(f"Conflict detected for run-id {run_id}. Entering recovery path...", file=sys.stderr)
        
        # Delete the conflicting document
        client.v1.context.delete(
            organization_id="",
            source=file_name,
            by_doc=True
        )
        
        # Retry the add call exactly once
        res = client.v1.context.add(
            context_type="resource",
            documents=[{"content": f"Idempotent ingest document for run {run_id}"}],
            scope="internal",
            source=source,
            metadata={
                "file_name": file_name,
                "file_size": 1024,
                "file_type": "text/plain",
                "last_modified": "2026-06-01T10:45:10Z"
            }
        )
        
        # Ensure retry succeeded (it shouldn't be a conflict anymore)
        if res and (getattr(res, "status_code", None) == 409 or getattr(res, "detail", None) == "Conflict"):
            print("Error: Retry also resulted in a conflict!", file=sys.stderr)
            sys.exit(1)
            
        print(f"RESULT: {json.dumps({'status': 'ok', 'conflict_resolved': True})}")
    else:
        print(f"RESULT: {json.dumps({'status': 'ok', 'conflict_resolved': False})}")

if __name__ == "__main__":
    main()
