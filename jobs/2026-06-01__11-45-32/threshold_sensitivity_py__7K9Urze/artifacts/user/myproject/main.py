import argparse
import json
import os
import sys
import time
from datetime import datetime

from alchemyst_ai import AlchemystAI


PROBE_QUERY = "What is our company refund policy?"
SCOPE = "internal"


def parse_thresholds() -> list[float]:
    parser = argparse.ArgumentParser(
        description="Probe Alchemyst AI context search threshold sensitivity."
    )
    parser.add_argument(
        "--thresholds",
        nargs="+",
        type=float,
        required=True,
        help="One or more similarity thresholds in the range (0, 1].",
    )
    args = parser.parse_args()

    thresholds = []
    for value in args.thresholds:
        if value <= 0 or value > 1:
            parser.error("Thresholds must be in the range (0, 1].")
        thresholds.append(value)
    return thresholds


def build_documents(run_id: str) -> list[dict[str, str]]:
    return [
        {
            "content": (
                "Refund Policy: Customers can request a full refund within 30 days of "
                "purchase if the product is unused and in original packaging."
            ),
            "file_stub": "refund_policy_overview",
        },
        {
            "content": (
                "Our company refund policy allows exchanges or refunds within 14 days "
                "for digital subscriptions when less than 20% of the service has been used."
            ),
            "file_stub": "refund_policy_subscription",
        },
        {
            "content": (
                "Support FAQ: To process a refund, submit the order number and reason "
                "for return. Refunds are issued back to the original payment method."
            ),
            "file_stub": "refund_policy_faq",
        },
        {
            "content": (
                "Q3 marketing plan: Focus on expanding inbound lead generation, SEO optimization, "
                "and webinar campaigns targeting enterprise buyers."
            ),
            "file_stub": "marketing_plan",
        },
        {
            "content": (
                "Warehouse update: The new fulfillment center will increase shipping capacity by "
                "20% and improve delivery times across the Midwest region."
            ),
            "file_stub": "warehouse_update",
        },
        {
            "content": (
                "Employee handbook excerpt: PTO accrues biweekly and must be approved two weeks in "
                "advance for planned leave requests."
            ),
            "file_stub": "employee_handbook",
        },
    ]


def ingest_documents(client: AlchemystAI, run_id: str, group_name: str) -> None:
    timestamp = datetime.utcnow().isoformat() + "Z"
    documents = build_documents(run_id)

    for index, doc in enumerate(documents, start=1):
        file_name = f"{doc['file_stub']}_{run_id}_{index}.txt"
        content = doc["content"]
        client.v1.context.add(
            context_type="resource",
            documents=[{"content": content}],
            scope=SCOPE,
            source="threshold-sensitivity-probe",
            metadata={
                "file_name": file_name,
                "file_type": "text/plain",
                "file_size": float(len(content.encode("utf-8"))),
                "last_modified": timestamp,
                "group_name": [group_name],
            },
        )


def search_thresholds(
    client: AlchemystAI, thresholds: list[float], group_name: str
) -> dict[float, int]:
    results: dict[float, int] = {}

    for threshold in thresholds:
        response = client.v1.context.search(
            query=PROBE_QUERY,
            similarity_threshold=threshold,
            minimum_similarity_threshold=0.0,
            scope=SCOPE,
            body_metadata={"groupName": [group_name]},
        )
        contexts = response.contexts or []
        results[threshold] = len(contexts)
    return results


def assert_monotonic(counts: dict[float, int]) -> None:
    sorted_items = sorted(counts.items(), key=lambda item: item[0])
    previous_count = None
    for threshold, count in sorted_items:
        if previous_count is not None and count > previous_count:
            raise ValueError(
                "Recall must be monotonically non-increasing as thresholds increase. "
                f"Threshold {threshold} returned {count}, which is greater than "
                f"the previous count {previous_count}."
            )
        previous_count = count


def format_output(counts: dict[float, int]) -> dict[str, int]:
    output: dict[str, int] = {}
    for threshold, count in counts.items():
        key = f"{threshold:.1f}"
        if key in output:
            raise ValueError(
                "Thresholds must be distinct when rounded to one decimal place. "
                f"Duplicate key detected for {key}."
            )
        output[key] = count
    return output


def main() -> None:
    thresholds = parse_thresholds()
    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        print("ZEALT_RUN_ID must be set in the environment.", file=sys.stderr)
        sys.exit(1)

    client = AlchemystAI()
    group_name = f"refund-policy-probe-{run_id}"

    ingest_documents(client, run_id, group_name)
    print("Documents ingested. Waiting for indexing...", file=sys.stderr)
    time.sleep(6)

    counts = search_thresholds(client, thresholds, group_name)
    try:
        assert_monotonic(counts)
        output = format_output(counts)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(output))


if __name__ == "__main__":
    main()
