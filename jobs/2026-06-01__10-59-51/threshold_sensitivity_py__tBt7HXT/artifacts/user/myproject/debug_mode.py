import os
import sys
import time
from alchemyst_ai import AlchemystAI

def main():
    client = AlchemystAI()
    run_id = os.environ.get("ZEALT_RUN_ID", f"local-run-{int(time.time())}")

    query = "What is our company refund policy?"

    search_resp = client.v1.context.search(
        minimum_similarity_threshold=0.9,
        query=query,
        similarity_threshold=0.9,
        body_metadata={"groupName": [run_id]},
        scope="internal",
        mode="standard"
    )
    print("Chunks returned:", len(search_resp.contexts) if search_resp.contexts else 0)

if __name__ == "__main__":
    main()
