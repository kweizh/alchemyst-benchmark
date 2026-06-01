import os
import sys
import time
import json
import argparse
from datetime import datetime, timezone
import httpx
from alchemyst_ai import AlchemystAI

def main():
    client = AlchemystAI()
    run_id = os.environ.get("ZEALT_RUN_ID", f"local-run-{int(time.time())}")

    query = "What is our company refund policy?"

    search_resp = client.v1.context.search(
        minimum_similarity_threshold=0.9,
        query=query,
        similarity_threshold=1.0,
        body_metadata={"groupName": [run_id]},
        scope="internal",
        metadata="true"
    )
    for c in search_resp.contexts:
        print(f"Score: {c.score}")

if __name__ == "__main__":
    main()
