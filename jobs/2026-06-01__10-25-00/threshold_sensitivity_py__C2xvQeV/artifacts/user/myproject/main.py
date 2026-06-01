import os
import sys
import json
import time
import argparse
from alchemyst_ai import AlchemystAI

def log(message):
    print(message, file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Threshold Sensitivity Probe with Alchemyst AI")
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        required=True,
        help="One or more threshold values in the range (0, 1]"
    )
    args = parser.parse_args()

    # Read environment variables
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        log("Error: ALCHEMYST_AI_API_KEY environment variable is not set.")
        sys.exit(1)

    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        log("Error: ZEALT_RUN_ID environment variable is not set.")
        sys.exit(1)

    log(f"Initializing Alchemyst AI client...")
    client = AlchemystAI(api_key=api_key)

    # Define corpus
    log("Preparing corpus...")
    documents = [
        # On-topic documents
        {
            "content": "Our company refund policy allows customers to request a full refund within 30 days of purchase. To be eligible for a refund, the product must be unused and in its original packaging. Please contact support to initiate the process."
        },
        {
            "content": "Refund Policy Details: All digital software purchases are eligible for a 100% money-back guarantee if requested within 14 days. No refunds are provided after 14 days or if the license key has been activated. Refund requests are processed within 5 business days."
        },
        {
            "content": "Standard Company Refund Policy: Physical merchandise can be returned for a full refund or store credit within 45 days of the shipping date. Return shipping fees are covered by the company if the item was defective or damaged upon arrival. Otherwise, the customer is responsible for return shipping costs."
        },
        # Off-topic / loosely related documents
        {
            "content": "Our company remote work policy allows employees to work from anywhere in the world for up to 90 days per calendar year. Employees must maintain core working hours from 10 AM to 4 PM EST and ensure stable internet connectivity."
        },
        {
            "content": "Annual Performance Review Guidelines: Performance evaluations are conducted every December. Employees and managers will collaborate on self-assessments, peer reviews, and goal setting for the upcoming fiscal year. Compensation adjustments are finalized in January."
        },
        {
            "content": "Office Security and Visitor Protocol: All visitors must sign in at the front desk and receive a temporary visitor badge. Employees are responsible for escorting their guests at all times while inside the building. Tailgating at secure entryways is strictly prohibited."
        }
    ]

    metadata = {
        "file_name": f"corpus_{run_id}.txt",
        "file_size": 1024.0,
        "file_type": "text/plain",
        "group_name": [run_id],
        "last_modified": "2026-06-01T10:31:17Z"
    }

    # Ingest documents
    log(f"Ingesting {len(documents)} documents under group_name '{run_id}'...")
    try:
        add_response = client.v1.context.add(
            context_type="resource",
            documents=documents,
            scope="internal",
            source="sensitivity-probe-cli",
            metadata=metadata
        )
        log(f"Ingestion successful. Status: {add_response.statusText if hasattr(add_response, 'statusText') else add_response}")
    except Exception as e:
        log(f"Error during document ingestion: {e}")
        sys.exit(1)

    # Wait for indexing to complete
    wait_time = 5
    log(f"Waiting {wait_time} seconds for indexing to complete...")
    time.sleep(wait_time)

    # Perform probe queries
    probe_query = "What is our company refund policy?"
    results = {}

    log(f"Probing thresholds: {args.thresholds}")
    for threshold in args.thresholds:
        # We enforce similarity_threshold and minimum_similarity_threshold in the API call
        # but also perform client-side filtering on the returned scores to guarantee correctness.
        try:
            search_response = client.v1.context.search(
                query=probe_query,
                similarity_threshold=threshold,
                minimum_similarity_threshold=min(threshold, 0.1),
                scope="internal",
                metadata="true",
                body_metadata={"groupName": [run_id]}
            )
            contexts = search_response.contexts or []
            
            # Filter the contexts where score >= threshold
            filtered_contexts = [
                c for c in contexts 
                if c.score is not None and c.score >= threshold
            ]
            
            recall_count = len(filtered_contexts)
            threshold_key = f"{threshold:.1f}"
            results[threshold_key] = recall_count
            log(f"Threshold {threshold:.1f} (raw: {threshold}): found {len(contexts)} contexts, {recall_count} met threshold.")
        except Exception as e:
            log(f"Error probing threshold {threshold}: {e}")
            sys.exit(1)

    # Print final JSON object to stdout
    print(json.dumps(results))

if __name__ == "__main__":
    main()
