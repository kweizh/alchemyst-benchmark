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

    on_topic_docs = [
        "Company Refund Policy: All purchases can be refunded within 30 days of the original purchase date, provided the item is in its original condition and packaging. To initiate a refund, please contact our support team with your order number.",
        "Refunds and Returns: If you are not satisfied with your product, our refund policy allows you to request a full refund within 14 days of delivery. Digital goods are exempt from refunds once downloaded.",
        "How to get a refund: Customers seeking a refund must fill out the return authorization form. Once approved, the refund will be processed to the original payment method within 5-7 business days."
    ]

    off_topic_docs = [
        "Employee Vacation Policy: All full-time employees are entitled to 20 days of paid time off per year. Vacation requests must be submitted at least two weeks in advance and approved by your direct supervisor.",
        "Quarterly Financial Report Q3: The company saw a 15% increase in revenue this quarter, largely driven by the new product launch in the European market. Operating expenses remained stable.",
        "Office Safety Guidelines: In the event of a fire alarm, please proceed calmly to the nearest exit. Do not use the elevators. The designated assembly point is the parking lot across the street."
    ]

    all_docs = on_topic_docs + off_topic_docs

    print(f"Ingesting {len(all_docs)} documents with run_id: {run_id}", file=sys.stderr)

    for i, doc_content in enumerate(all_docs):
        metadata = {
            "file_name": f"doc_{i}_{run_id}.txt",
            "file_size": len(doc_content.encode("utf-8")),
            "file_type": "text/plain",
            "group_name": [run_id],
            "last_modified": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            client.v1.context.add(
                context_type="resource",
                documents=[{"content": doc_content}],
                scope="internal",
                source="probe_script",
                metadata=metadata
            )
        except Exception as e:
            print(f"Error adding document {i}: {e}", file=sys.stderr)

    # Wait for indexing
    print("Waiting for indexing to complete...", file=sys.stderr)
    time.sleep(10)

    query = "What is our company refund policy?"
    results = {}

    print("Probing thresholds...", file=sys.stderr)
    for threshold in sorted(args.thresholds):
        try:
            # Vary only similarity_threshold as instructed.
            # minimum_similarity_threshold is required by the SDK, so we keep it constant at 0.0.
            search_resp = client.v1.context.search(
                minimum_similarity_threshold=0.0,
                query=query,
                similarity_threshold=threshold,
                body_metadata={"groupName": [run_id]},
                scope="internal",
                metadata="true"
            )
            
            # The API should filter chunks, but if it doesn't we filter manually by score
            count = 0
            if search_resp.contexts:
                for c in search_resp.contexts:
                    if c.score is not None and c.score >= threshold:
                        count += 1
                    elif c.score is None:
                        count += 1
                        
            formatted_threshold = f"{threshold:.1f}"
            results[formatted_threshold] = count
            print(f"Threshold {formatted_threshold}: {count} chunks returned", file=sys.stderr)
        except Exception as e:
            print(f"Error searching at threshold {threshold}: {e}", file=sys.stderr)
            formatted_threshold = f"{threshold:.1f}"
            results[formatted_threshold] = 0

    # Print JSON result to stdout
    print(json.dumps(results))

if __name__ == "__main__":
    main()
