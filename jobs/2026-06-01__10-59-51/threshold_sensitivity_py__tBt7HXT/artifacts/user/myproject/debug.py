import os
import sys
import time
import json
import argparse
from datetime import datetime, timezone
from alchemyst_ai import AlchemystAI

def main():
    parser = argparse.ArgumentParser(description="Threshold Sensitivity Probe")
    parser.add_argument("--thresholds", type=float, nargs="+", required=True, help="List of similarity thresholds")
    args = parser.parse_args()

    client = AlchemystAI()
    run_id = os.environ.get("ZEALT_RUN_ID", f"local-run-{int(time.time())}")

    print(f"run_id: {run_id}", file=sys.stderr)

    query = "What is our company refund policy?"

    search_resp = client.v1.context.search(
        minimum_similarity_threshold=0.9,
        query=query,
        similarity_threshold=1.0,
        body_metadata={"group_name": [run_id]},
        scope="internal"
    )
    print("With group_name:", len(search_resp.contexts) if search_resp.contexts else 0, file=sys.stderr)

    search_resp = client.v1.context.search(
        minimum_similarity_threshold=0.9,
        query=query,
        similarity_threshold=1.0,
        body_metadata={"groupName": [run_id]},
        scope="internal"
    )
    print("With groupName:", len(search_resp.contexts) if search_resp.contexts else 0, file=sys.stderr)

if __name__ == "__main__":
    main()
