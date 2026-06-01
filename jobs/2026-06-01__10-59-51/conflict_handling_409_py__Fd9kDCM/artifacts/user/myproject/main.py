import os
import sys
import json
from alchemyst_ai import AlchemystAI, APIStatusError

def main():
    api_key = os.getenv("ALCHEMYST_AI_API_KEY")
    run_id = os.getenv("ZEALT_RUN_ID")
    
    if not api_key:
        print("Missing ALCHEMYST_AI_API_KEY", file=sys.stderr)
        sys.exit(1)
        
    if not run_id:
        print("Missing ZEALT_RUN_ID", file=sys.stderr)
        sys.exit(1)
        
    client = AlchemystAI(api_key=api_key, max_retries=0)
    
    file_name = f"doc_{run_id}.txt"
    source = f"source_{run_id}"
    
    conflict_resolved = False
    
    def attempt_add():
        return client.v1.context.add(
            context_type="resource",
            scope="internal",
            source=source,
            metadata={"file_name": file_name},
            documents=[{"content": "This is a test document for idempotent ingest."}]
        )

    try:
        attempt_add()
    except APIStatusError as e:
        if e.status_code == 409:
            print(f"Conflict detected for source {source}, resolving...", file=sys.stderr)
            client.v1.context.delete(source=source, by_doc=True, organization_id="default")
            attempt_add()
            conflict_resolved = True
        else:
            raise
            
    res = {"status": "ok", "conflict_resolved": conflict_resolved}
    print(f"RESULT: {json.dumps(res)}")

if __name__ == "__main__":
    main()
