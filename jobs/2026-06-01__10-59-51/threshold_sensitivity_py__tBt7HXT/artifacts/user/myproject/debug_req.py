import os
import sys
import time
import json
import argparse
from datetime import datetime, timezone
import httpx
from alchemyst_ai import AlchemystAI

def log_request(request):
    print(f"Request URL: {request.url}")
    print(f"Request body: {request.read().decode('utf-8')}")

def main():
    client = AlchemystAI(http_client=httpx.Client(event_hooks={'request': [log_request]}))
    run_id = os.environ.get("ZEALT_RUN_ID", f"local-run-{int(time.time())}")

    query = "What is our company refund policy?"

    search_resp = client.v1.context.search(
        minimum_similarity_threshold=0.9,
        query=query,
        similarity_threshold=1.0,
        body_metadata={"groupName": [run_id]},
        scope="internal"
    )

if __name__ == "__main__":
    main()
