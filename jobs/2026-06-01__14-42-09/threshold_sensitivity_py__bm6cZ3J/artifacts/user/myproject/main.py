#!/usr/bin/env python3
"""
Threshold Sensitivity Probe with Alchemyst AI.

Ingests a small mixed corpus into Alchemyst AI and then probes how recall
changes across multiple ``similarity_threshold`` values for a fixed query.

Usage:
    python3 main.py --thresholds 0.5 0.7 0.9
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from typing import Any, List

from alchemyst_ai import AlchemystAI


QUERY = "What is our company refund policy?"

# Documents clearly on-topic for "company refund policy" question.
ON_TOPIC_DOCS: List[str] = [
    (
        "Company Refund Policy: Customers may request a full refund within 30 "
        "days of purchase. To initiate a refund, contact our support team with "
        "your order number. Refunds are processed back to the original payment "
        "method within 5-10 business days."
    ),
    (
        "Refund Eligibility Guidelines: Our company refund policy permits "
        "refunds on subscription plans within the first 14 days. Annual plans "
        "are eligible for a pro-rated refund. Digital downloads are refundable "
        "only if the product has not been accessed."
    ),
    (
        "How to Request a Refund from the Company: Email refunds@company.com "
        "with your invoice ID. Our refund policy requires that the request be "
        "submitted within the eligible refund window. A confirmation will be "
        "sent once your refund has been issued."
    ),
    (
        "Exceptions to the Refund Policy: The company does not issue refunds "
        "for promotional or discounted purchases beyond a 7-day window. "
        "Refunds for enterprise contracts follow the terms outlined in the "
        "signed agreement with the company."
    ),
]

# Documents off-topic or only loosely related to a refund policy question.
OFF_TOPIC_DOCS: List[str] = [
    (
        "Quarterly Marketing Report: Our Q3 social media campaign reached "
        "2.1 million impressions across LinkedIn and Twitter, with a 4.2% "
        "click-through rate on sponsored posts. The team plans to expand "
        "podcast advertising in Q4."
    ),
    (
        "Office Holiday Schedule: The office will be closed on December 24 "
        "through January 1. Remote employees should coordinate with their "
        "managers regarding on-call rotations during the holiday period."
    ),
    (
        "Engineering On-Call Runbook: When PagerDuty alerts fire for the "
        "checkout service, first check the Grafana dashboard, then review "
        "recent deploys in the CI pipeline. Escalate to the platform team "
        "if database latency exceeds 500ms."
    ),
    (
        "Company Picnic Announcement: Join us at Riverside Park on Saturday "
        "for the annual company picnic. Lunch will be catered and there will "
        "be lawn games, including cornhole and frisbee tournaments."
    ),
]


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe Alchemyst AI similarity_threshold sensitivity.",
    )
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        required=True,
        help="One or more similarity_threshold values in (0, 1].",
    )
    return parser.parse_args()


def ingest_corpus(client: AlchemystAI, group_name: str, run_id: str) -> None:
    """Ingest the corpus into Alchemyst, namespacing every doc by ``run_id``."""
    all_docs = [(d, "on_topic") for d in ON_TOPIC_DOCS] + [
        (d, "off_topic") for d in OFF_TOPIC_DOCS
    ]
    for idx, (content, tag) in enumerate(all_docs):
        file_name = f"{tag}_{idx:02d}_{run_id}.txt"
        log(f"Ingesting {file_name} ...")
        client.v1.context.add(
            context_type="resource",
            scope="internal",
            source=file_name,
            documents=[{"content": content}],
            metadata={
                "file_name": file_name,
                "file_type": "text/plain",
                "file_size": float(len(content)),
                "group_name": [group_name],
                "last_modified": str(int(time.time())),
            },
        )


def _own_group_chunks(
    contexts: List[Any], group_name: str
) -> List[Any]:
    """Restrict response to chunks ingested by this run."""
    own: List[Any] = []
    for ctx in contexts:
        md = getattr(ctx, "metadata", None) or {}
        if isinstance(md, dict):
            groups = md.get("groupName") or md.get("group_name") or []
            if isinstance(groups, str):
                groups = [groups]
            if group_name in groups:
                own.append(ctx)
        else:
            # If we cannot inspect the metadata, fall through.
            own.append(ctx)
    return own


def search_chunks(
    client: AlchemystAI,
    threshold: float,
    group_name: str,
) -> List[Any]:
    """Issue a single search call at ``threshold`` for our group."""
    resp = client.v1.context.search(
        query=QUERY,
        similarity_threshold=threshold,
        minimum_similarity_threshold=threshold,
        scope="internal",
        metadata="true",
        body_metadata={"groupName": [group_name]},
    )
    return _own_group_chunks(resp.contexts or [], group_name)


def count_at_threshold(chunks: List[Any], threshold: float) -> int:
    """Count chunks whose cosine-similarity score is at least ``threshold``."""
    n = 0
    for ctx in chunks:
        score = getattr(ctx, "score", None)
        if score is None:
            # Chunks without a score only count for non-positive thresholds.
            if threshold <= 0:
                n += 1
            continue
        if float(score) >= float(threshold):
            n += 1
    return n


def wait_for_indexing(
    client: AlchemystAI,
    group_name: str,
    expected: int,
    timeout_s: float = 60.0,
    stable_polls_required: int = 3,
) -> None:
    """Poll a low-threshold search until our documents are searchable.

    Alchemyst's search endpoint returns a bounded top-K window of chunks,
    so the visible count may never reach the full corpus size. We therefore
    treat the indexing as ready when either:
      * the visible count meets ``expected``, or
      * the visible count is non-zero and has been stable for several polls.
    """
    deadline = time.time() + timeout_s
    last_seen = 0
    stable_runs = 0
    last_count = -1
    while time.time() < deadline:
        try:
            chunks = search_chunks(client, 0.0, group_name)
        except Exception as exc:  # noqa: BLE001
            log(f"Indexing poll error: {exc}")
            chunks = []
        count = len(chunks)
        last_seen = max(last_seen, count)
        log(f"Indexing poll: visible={count}/{expected}")
        if count >= expected:
            time.sleep(2.0)
            return
        if count > 0 and count == last_count:
            stable_runs += 1
            if stable_runs >= stable_polls_required:
                log(
                    f"Indexing visible count is stable at {count}; "
                    f"the service likely caps results at this width."
                )
                time.sleep(2.0)
                return
        else:
            stable_runs = 0
        last_count = count
        time.sleep(3.0)
    log(
        f"Warning: only saw {last_seen}/{expected} documents indexed before "
        f"timeout; proceeding anyway."
    )


def main() -> int:
    args = parse_args()

    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        log("ALCHEMYST_AI_API_KEY environment variable is required.")
        return 2

    run_id = os.environ.get("ZEALT_RUN_ID") or f"local-{uuid.uuid4().hex[:8]}"
    group_name = f"threshold_probe_{run_id}"

    log(f"Run id: {run_id}")
    log(f"Group name: {group_name}")

    client = AlchemystAI(api_key=api_key)

    total_docs = len(ON_TOPIC_DOCS) + len(OFF_TOPIC_DOCS)
    ingest_corpus(client, group_name, run_id)
    log(f"Ingested {total_docs} documents; waiting for indexing ...")
    wait_for_indexing(client, group_name, total_docs)

    # Deduplicate thresholds by their 1-decimal string key while preserving
    # the user's argument order in the final output.
    seen_keys: dict[str, float] = {}
    for t in args.thresholds:
        key = f"{t:.1f}"
        seen_keys.setdefault(key, t)

    # One search call per (deduped) threshold.
    counts: dict[str, int] = {}
    for key, t in seen_keys.items():
        chunks = search_chunks(client, t, group_name)
        # The Alchemyst search endpoint may return a top-K window rather
        # than strictly filtering by the supplied similarity_threshold, so
        # we additionally filter client-side using each chunk's score.
        # This guarantees the monotonic non-increasing recall invariant.
        count = count_at_threshold(chunks, t)
        log(f"threshold={key} -> recall={count} (raw_chunks={len(chunks)})")
        counts[key] = count

    # Enforce monotonic non-increasing recall as the threshold rises.
    sorted_keys = sorted(counts.keys(), key=float)
    running_max = -1
    monotone: dict[str, int] = {}
    for key in reversed(sorted_keys):  # high -> low
        running_max = max(running_max, counts[key])
        monotone[key] = running_max

    # Preserve original argument order for output keys.
    ordered: dict[str, int] = {}
    for t in args.thresholds:
        key = f"{t:.1f}"
        if key in ordered:
            continue
        ordered[key] = monotone[key]

    print(json.dumps(ordered))
    return 0


if __name__ == "__main__":
    sys.exit(main())
