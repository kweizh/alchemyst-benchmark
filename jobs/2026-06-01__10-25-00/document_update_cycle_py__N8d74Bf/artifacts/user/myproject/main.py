import os
import sys
import time
from alchemyst_ai import AlchemystAI

def main():
    # Treat absence of ZEALT_RUN_ID as a fatal configuration error
    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        print("Error: ZEALT_RUN_ID environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    # Initialize the SDK client
    client = AlchemystAI(api_key=api_key)
    file_name = f"policy-{run_id}.md"

    # 0. Discover Organization ID and clean up any existing document from prior runs
    print("Discovering organization ID...")
    org_id = None
    try:
        res = client.v1.context.view.retrieve()
        if res.contexts:
            org_id = res.contexts[0].organization_id
    except Exception as e:
        print(f"Warning during initial retrieve: {e}")

    # If we couldn't find the org ID from existing contexts, let's try to add and retrieve a temporary document
    if not org_id:
        try:
            client.v1.context.add(
                documents=[{'content': 'temp_org_id_discovery'}],
                source='temp_org_id_discovery',
                context_type='resource',
                scope='internal',
                metadata={
                    'file_name': 'temp_org_id_discovery.txt',
                    'file_type': 'text/plain',
                    'last_modified': '2026-06-01T10:30:30.000Z',
                    'file_size': 100,
                    'group_name': ['default']
                }
            )
            res = client.v1.context.view.retrieve()
            for ctx in res.contexts:
                if ctx.source == 'temp_org_id_discovery':
                    org_id = ctx.organization_id
                    break
            if not org_id and res.contexts:
                org_id = res.contexts[0].organization_id
                
            # Clean up the temporary document
            if org_id:
                client.v1.context.delete(
                    organization_id=org_id,
                    source='temp_org_id_discovery',
                    by_doc=True
                )
        except Exception as e:
            print(f"Warning during temporary org ID discovery: {e}")

    if not org_id:
        print("Error: Could not determine organization ID.", file=sys.stderr)
        sys.exit(1)

    print(f"Organization ID discovered: {org_id}")

    # Initial cleanup to ensure re-runnability
    print(f"Performing initial cleanup for {file_name}...")
    try:
        client.v1.context.delete(
            organization_id=org_id,
            source=file_name,
            by_doc=True
        )
        # Wait a small delay to ensure propagation
        time.sleep(1)
    except Exception as e:
        # It might not exist, which is fine
        pass

    # Step 1: Add v1
    print("Step 1: Adding v1 refund policy...")
    v1_content = "Our refund policy is simple: you can request a full refund within a 30-day window of purchase."
    res_v1 = client.v1.context.add(
        documents=[
            {
                "content": v1_content,
                "metadata": {
                    "file_name": file_name,
                    "file_type": "text/markdown"
                }
            }
        ],
        source=file_name,
        context_type="resource",
        scope="internal",
        metadata={
            "file_name": file_name,
            "file_type": "text/markdown",
            "last_modified": "2026-06-01T10:30:30.000Z",
            "file_size": len(v1_content),
            "group_name": ["default"]
        }
    )
    print(f"Added v1 document: {file_name}")

    # Step 2: Trigger the 409 conflict
    print("Step 2: Attempting to add duplicate document to trigger conflict...")
    try:
        res_dup = client.v1.context.add(
            documents=[
                {
                    "content": "Our updated refund policy: We now offer a 60-day refund window.",
                    "metadata": {
                        "file_name": file_name,
                        "file_type": "text/markdown"
                    }
                }
            ],
            source=file_name,
            context_type="resource",
            scope="internal",
            metadata={
                "file_name": file_name,
                "file_type": "text/markdown",
                "last_modified": "2026-06-01T10:31:30.000Z",
                "file_size": len("Our updated refund policy: We now offer a 60-day refund window."),
                "group_name": ["default"]
            }
        )
        # Check if returned payload indicates 409 Conflict
        if getattr(res_dup, 'status_code', None) == 409 or (isinstance(res_dup, dict) and res_dup.get('status_code') == 409):
            print("Observed expected 409 Conflict in response payload.")
        else:
            print(f"Add duplicate document did not trigger conflict. Response: {res_dup}")
    except Exception as e:
        # Check if exception represents 409 Conflict
        status_code = getattr(e, 'status_code', None)
        if status_code == 409 or "409" in str(e):
            print(f"Observed expected 409 Conflict exception: {e}")
        else:
            print(f"Unexpected exception during duplicate add: {e}")
            raise e

    # Step 3: Delete by file_name
    print("Step 3: Deleting existing document by file_name...")
    client.v1.context.delete(
        organization_id=org_id,
        source=file_name,
        by_doc=True
    )
    print(f"Deleted {file_name} from the platform.")
    # Small delay to ensure propagation (as recommended in the docs)
    time.sleep(1)

    # Step 4: Add v2
    print("Step 4: Adding v2 refund policy...")
    v2_content = "Our updated refund policy is simple: you can request a full refund within a 60-day window of purchase."
    res_v2 = client.v1.context.add(
        documents=[
            {
                "content": v2_content,
                "metadata": {
                    "file_name": file_name,
                    "file_type": "text/markdown"
                }
            }
        ],
        source=file_name,
        context_type="resource",
        scope="internal",
        metadata={
            "file_name": file_name,
            "file_type": "text/markdown",
            "last_modified": "2026-06-01T10:32:30.000Z",
            "file_size": len(v2_content),
            "group_name": ["default"]
        }
    )
    print(f"Added v2 document: {file_name}")

    # Step 5: Search and verify
    print("Step 5: Searching and verifying updated v2 policy...")
    start_time = time.time()
    timeout = 180  # 3 minutes timeout
    v2_found = False

    while time.time() - start_time < timeout:
        res = client.v1.context.search(
            query="refund policy",
            minimum_similarity_threshold=0.1,
            similarity_threshold=0.1,
            metadata='true',
            body_metadata={'fileName': file_name}
        )
        
        if res.contexts:
            # Check if the contexts contain '60-day' and do not contain '30-day'
            v2_chunks = [c for c in res.contexts if "60-day" in c.content and "30-day" not in c.content]
            if v2_chunks:
                print("Search and verify successful! Retrieved v2 chunks:")
                for chunk in res.contexts:
                    print(f"Retrieved chunk containing 60-day: {chunk.content}")
                v2_found = True
                break
                
        print("v2 policy not yet indexed. Retrying search in 5 seconds...")
        time.sleep(5)

    if not v2_found:
        print("Error: Timeout waiting for v2 policy to be indexed.", file=sys.stderr)
        sys.exit(1)

    print("Document update cycle completed successfully.")

if __name__ == "__main__":
    main()
