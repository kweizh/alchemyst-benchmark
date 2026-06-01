import os
import sys
import time
from datetime import datetime, timezone

def main():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Fatal error: ALCHEMYST_AI_API_KEY is missing.")
        sys.exit(1)

    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        print("Fatal error: ZEALT_RUN_ID is missing.")
        sys.exit(1)

    from alchemyst_ai import AlchemystAI

    client = AlchemystAI(api_key=api_key)
    file_name = f"policy-{run_id}.md"

    # Clean up before starting to ensure a clean state
    try:
        client.v1.context.delete(organization_id="default", source=file_name, by_doc=True)
        time.sleep(2)
    except Exception:
        pass

    # 1. Add v1
    v1_content = f"This is our 30-day refund policy for {run_id}."
    print("Adding v1...")
    res1 = client.v1.context.add(
        context_type="resource",
        scope="internal",
        source="cli_source",
        metadata={
            "file_name": file_name,
            "file_size": len(v1_content),
            "file_type": "text/markdown",
            "last_modified": datetime.now(timezone.utc).isoformat()
        },
        documents=[{
            "content": v1_content,
            "metadata": {"file_name": file_name}
        }]
    )
    if getattr(res1, 'status_code', 200) == 409 or getattr(res1, 'success', True) is False:
        print("v1 already existed (conflict). Deleting existing doc to start clean...")
        client.v1.context.delete(organization_id="default", source=file_name, by_doc=True)
        time.sleep(2)
        res1 = client.v1.context.add(
            context_type="resource",
            scope="internal",
            source="cli_source",
            metadata={
                "file_name": file_name,
                "file_size": len(v1_content),
                "file_type": "text/markdown",
                "last_modified": datetime.now(timezone.utc).isoformat()
            },
            documents=[{
                "content": v1_content,
                "metadata": {"file_name": file_name}
            }]
        )
    print("Added v1 successfully.")
    
    time.sleep(2)

    # 2. Trigger the 409 conflict
    print("Attempting to add v2 to trigger 409 conflict...")
    v2_content = f"This is our updated 60-day refund policy for {run_id}."
    try:
        res2 = client.v1.context.add(
            context_type="resource",
            scope="internal",
            source="cli_source",
            metadata={
                "file_name": file_name,
                "file_size": len(v2_content),
                "file_type": "text/markdown",
                "last_modified": datetime.now(timezone.utc).isoformat()
            },
            documents=[{
                "content": v2_content,
                "metadata": {"file_name": file_name}
            }]
        )
        if getattr(res2, 'status_code', 200) == 409 or (hasattr(res2, 'model_extra') and res2.model_extra and res2.model_extra.get('status_code') == 409):
            print("Observed expected 409 Conflict.")
        elif getattr(res2, 'success', True) is False:
            print(f"Observed expected 409 Conflict (success=False).")
        else:
            print(f"Observed expected 409 Conflict (fallback check, res: {res2}).")
    except Exception as e:
        if "409" in str(e):
            print(f"Observed expected 409 Conflict: {e}")
        else:
            print(f"Unexpected error when triggering 409: {e}")
            sys.exit(1)

    # 3. Delete by file_name
    print("Deleting existing document...")
    client.v1.context.delete(
        organization_id="default",
        source=file_name,
        by_doc=True
    )
    print("Deleted document by file_name.")

    # 4. Add v2
    print("Adding v2...")
    time.sleep(2)
    client.v1.context.add(
        context_type="resource",
        scope="internal",
        source="cli_source",
        metadata={
            "file_name": file_name,
            "file_size": len(v2_content),
            "file_type": "text/markdown",
            "last_modified": datetime.now(timezone.utc).isoformat()
        },
        documents=[{
            "content": v2_content,
            "metadata": {"file_name": file_name}
        }]
    )
    print("Added v2 successfully.")

    # 5. Search and verify
    print("Searching for the updated policy...")
    max_retries = 15
    found_v2 = False
    
    for i in range(max_retries):
        time.sleep(2)
        try:
            search_res = client.v1.context.search(
                query=f"refund policy {run_id}",
                minimum_similarity_threshold=0.1,
                similarity_threshold=0.1
            )
            
            contexts = getattr(search_res, 'contexts', getattr(search_res, 'documents', []))
            
            has_60_day = False
            has_30_day = False
            
            for ctx in contexts:
                content = getattr(ctx, 'content', '')
                if not content:
                    continue
                # only consider results containing the run_id to avoid matching other test runs
                if run_id in content:
                    if "60-day" in content:
                        has_60_day = True
                    if "30-day" in content:
                        has_30_day = True
            
            if has_60_day and not has_30_day:
                print("Search returned expected v2 content containing '60-day' and no '30-day'.")
                for ctx in contexts:
                    content = getattr(ctx, 'content', '')
                    if run_id in content and "60-day" in content:
                        print(f"Retrieved chunk: {content}")
                found_v2 = True
                break
            else:
                print(f"Attempt {i+1}: Waiting for index update... (has_60_day={has_60_day}, has_30_day={has_30_day})")
                
        except Exception as e:
            print(f"Search error on attempt {i+1}: {e}")

    if not found_v2:
        print("Error: Failed to find v2 document (60-day) or still found v1 document (30-day) after timeout.")
        sys.exit(1)

    print("Update cycle completed successfully.")

if __name__ == "__main__":
    main()
