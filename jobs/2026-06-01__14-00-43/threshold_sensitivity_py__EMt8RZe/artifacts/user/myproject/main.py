#!/usr/bin/env python3
"""Threshold Sensitivity Probe for Alchemyst AI.

Ingests a small corpus of on-topic and off-topic documents, then probes how
recall changes across multiple similarity_threshold values.
"""

import argparse
import json
import os
import sys
import time

from alchemyst_ai import AlchemystAI

# ---------------------------------------------------------------------------
# Corpus definition
# ---------------------------------------------------------------------------
# Probe query: "What is our company refund policy?"
# On-topic documents (4) deal directly with refund/return policies.
# Off-topic documents (4) are unrelated business topics.

PROBE_QUERY = "What is our company refund policy?"

ON_TOPIC_DOCUMENTS = [
    {
        "content": (
            "Company Refund Policy: Customers may request a full refund within 30 days "
            "of purchase for any product purchased through our online store. To initiate "
            "a refund, contact our support team at refunds@example.com with your order "
            "number. Refunds are processed within 5-7 business days and credited back "
            "to the original payment method."
        ),
    },
    {
        "content": (
            "Return and Exchange Guidelines: Our company allows returns within 30 days "
            "of delivery. Items must be in their original packaging and unused condition. "
            "We offer a full refund, exchange, or store credit. Shipping costs for "
            "returns are the responsibility of the customer unless the item was "
            "defective or we made an error in your order."
        ),
    },
    {
        "content": (
            "Refund Processing Timeline: Once we receive your returned item, our "
            "warehouse team inspects it within 2 business days. Approved refunds are "
            "processed within 3-5 business days. If you paid by credit card, please "
            "allow an additional 2-3 billing cycles for the credit to appear on your "
            "statement. Digital product refunds are issued immediately upon approval."
        ),
    },
    {
        "content": (
            "Money-Back Guarantee: We stand behind our products with a 60-day "
            "money-back guarantee. If you are not completely satisfied, return the "
            "product for a full refund of the purchase price. No questions asked. "
            "This guarantee applies to all physical products and annual subscription "
            "plans. Monthly subscriptions are eligible for prorated refunds."
        ),
    },
]

OFF_TOPIC_DOCUMENTS = [
    {
        "content": (
            "Office Snack Procurement Policy: The break room snack budget is $200 per "
            "month. The office manager is responsible for ordering snacks every Monday. "
            "Preferred vendors include SnackBox Co. and FreshBite Deliveries. Requests "
            "for specific snacks should be submitted via the #snack-requests Slack "
            "channel by Friday each week."
        ),
    },
    {
        "content": (
            "Employee Parking Allocation: Parking spots in the underground garage are "
            "assigned based on seniority. New hires are placed on a waitlist and "
            "typically receive a spot within 6 months. Carpool participants receive "
            "priority allocation. Visitor parking is available on levels P1 and P2 "
            "with a 4-hour maximum stay."
        ),
    },
    {
        "content": (
            "Annual Company Picnic Planning: The summer company picnic is scheduled "
            "for the third Saturday of July each year. The events committee handles "
            "venue booking, catering, and activity planning. Budget allocation is "
            "$50 per employee. Activities include volleyball, relay races, and a "
            "raffle with prizes donated by local businesses."
        ),
    },
    {
        "content": (
            "Network Security Protocol: All employees must use the company VPN when "
            "accessing internal resources remotely. Passwords must be changed every "
            "90 days and must include uppercase, lowercase, numbers, and special "
            "characters. Multi-factor authentication is required for all admin-level "
            "accounts. Suspicious activity should be reported to security@example.com."
        ),
    },
]

ALL_DOCUMENTS = ON_TOPIC_DOCUMENTS + OFF_TOPIC_DOCUMENTS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_group_name(run_id: str) -> str:
    """Return a group name that includes the run id for isolation."""
    return f"threshold-probe-{run_id}"


def ingest_documents(client: AlchemystAI, run_id: str) -> None:
    """Add all corpus documents to Alchemyst AI."""
    group = build_group_name(run_id)

    for idx, doc in enumerate(ALL_DOCUMENTS):
        file_name = f"doc-{idx}-{run_id}.txt"
        client.v1.context.add(
            context_type="resource",
            documents=[doc],
            scope="internal",
            source="threshold-sensitivity-probe",
            metadata={
                "file_name": file_name,
                "file_type": "text/plain",
                "file_size": len(doc["content"].encode("utf-8")),
                "group_name": [group],
                "last_modified": "2025-06-01T12:00:00.000Z",
            },
        )
        print(f"[stderr] Ingested {file_name}", file=sys.stderr)


def wait_for_indexing(seconds: int = 10) -> None:
    """Pause to allow the Alchemyst backend to index newly added documents."""
    print(f"[stderr] Waiting {seconds}s for indexing...", file=sys.stderr)
    time.sleep(seconds)


def search_with_threshold(
    client: AlchemystAI,
    threshold: float,
    run_id: str,
) -> int:
    """Execute a search at the given minimum similarity threshold and return the chunk count."""
    group = build_group_name(run_id)

    response = client.v1.context.search(
        minimum_similarity_threshold=threshold,
        query=PROBE_QUERY,
        similarity_threshold=1.0,
        scope="internal",
        metadata="true",
        body_metadata={"group_name": [group]},
    )

    contexts = response.contexts or []
    return len(contexts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe Alchemyst AI threshold sensitivity"
    )
    parser.add_argument(
        "--thresholds",
        nargs="+",
        type=float,
        required=True,
        help="One or more similarity threshold values (e.g. 0.5 0.7 0.9)",
    )
    args = parser.parse_args()

    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    client = AlchemystAI()

    # 1. Ingest corpus
    ingest_documents(client, run_id)

    # 2. Wait for indexing
    wait_for_indexing(seconds=10)

    # 3. Probe each threshold
    results: dict[str, int] = {}
    for t in args.thresholds:
        count = search_with_threshold(client, t, run_id)
        key = f"{t:.1f}"
        results[key] = count
        print(f"[stderr] threshold={key} → {count} chunks", file=sys.stderr)

    # 4. Verify monotonicity (warn but don't fail)
    sorted_thresholds = sorted(args.thresholds)
    for i in range(len(sorted_thresholds) - 1):
        low_key = f"{sorted_thresholds[i]:.1f}"
        high_key = f"{sorted_thresholds[i + 1]:.1f}"
        if results[low_key] < results[high_key]:
            print(
                f"[stderr] WARNING: monotonicity violated: "
                f"threshold {low_key} → {results[low_key]} but "
                f"threshold {high_key} → {results[high_key]}",
                file=sys.stderr,
            )

    # 5. Print result JSON to stdout (nothing else on stdout)
    print(json.dumps(results))


if __name__ == "__main__":
    main()