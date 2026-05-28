import os
import json
import time
import sys
from alchemyst_ai import AlchemystAI

def main():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    run_id = os.environ.get("ZEALT_RUN_ID")

    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.")
        sys.exit(1)
    if not run_id:
        print("Error: ZEALT_RUN_ID environment variable is not set.")
        sys.exit(1)

    client = AlchemystAI(api_key=api_key)

    # Documents to ingest
    documents = [
        {
            "content": "Our refund policy allows for a full money-back guarantee within 30 days of purchase if you are not satisfied with the product.",
            "file_name": f"refund_policy_direct_1_{run_id}.md"
        },
        {
            "content": "To request a refund under our money-back policy, please contact support with your order number and reason for return.",
            "file_name": f"refund_policy_direct_2_{run_id}.md"
        },
        {
            "content": "Shipping takes 3-5 business days for domestic orders and up to 14 days for international shipping.",
            "file_name": f"shipping_info_{run_id}.md"
        },
        {
            "content": "We value your privacy. Our privacy policy outlines how we collect and use your data to improve our services.",
            "file_name": f"privacy_policy_{run_id}.md"
        },
        {
            "content": "If you receive a damaged item, please take a photo and send it to our customer support team for a replacement.",
            "file_name": f"damaged_items_{run_id}.md"
        }
    ]

    print(f"Ingesting {len(documents)} documents...")
    for doc in documents:
        try:
            client.v1.context.add(
                context_type="resource",
                documents=[{"content": doc["content"]}],
                source="docs",
                scope="internal",
                metadata={
                    "file_name": doc["file_name"],
                    "fileSize": len(doc["content"]),
                    "fileType": "text/markdown",
                    "lastModified": "2026-05-27T16:02:12Z"
                }
            )
            print(f"Successfully ingested: {doc['file_name']}")
        except Exception as e:
            print(f"Error ingesting {doc['file_name']}: {e}")
            sys.exit(1)

    # Brief pause to allow indexing
    print("Waiting for indexing...")
    time.sleep(10)

    query = "What is the refund policy?"

    # Search with threshold 0.5
    print(f"Searching with similarity_threshold=0.5...")
    try:
        res_0_5 = client.v1.context.search(
            query=query,
            scope="internal",
            similarity_threshold=0.5,
            minimum_similarity_threshold=0.0
        )
        count_0_5 = len(res_0_5.contexts) if res_0_5.contexts else 0
        print(f"Found {count_0_5} contexts.")
    except Exception as e:
        print(f"Error during search (0.5): {e}")
        sys.exit(1)

    # Search with threshold 0.9
    print(f"Searching with similarity_threshold=0.9...")
    try:
        res_0_9 = client.v1.context.search(
            query=query,
            scope="internal",
            similarity_threshold=0.9,
            minimum_similarity_threshold=0.0
        )
        count_0_9 = len(res_0_9.contexts) if res_0_9.contexts else 0
        print(f"Found {count_0_9} contexts.")
    except Exception as e:
        print(f"Error during search (0.9): {e}")
        sys.exit(1)

    # Prepare report
    report = {
        "query": query,
        "threshold_0_5_count": count_0_5,
        "threshold_0_9_count": count_0_9,
        "run_id": run_id
    }

    # Write to file
    report_path = "/workspace/threshold_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report written to {report_path}")

    # Final check
    if count_0_5 < count_0_9:
        print(f"Warning: threshold_0_5_count ({count_0_5}) is less than threshold_0_9_count ({count_0_9})")
        # Although the requirement says it MUST hold, if the API behaves weirdly I should know.
    
if __name__ == "__main__":
    main()
