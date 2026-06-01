#!/usr/bin/env python3
"""
Alchemyst AI Document Update Cycle CLI.

Demonstrates the full update cycle for a document that is keyed by
`metadata.file_name`. Because Alchemyst rejects re-adding a document with
the same `file_name` (HTTP 409 Conflict), the safe pattern is:

    add v1  ->  (409 on naive re-add)  ->  delete by file_name  ->  add v2

Environment:
    ALCHEMYST_AI_API_KEY  - API key for the Alchemyst service (read by SDK).
    ZEALT_RUN_ID          - Per-run namespace to avoid collisions across runs.
"""

from __future__ import annotations

import os
import sys
import time
from typing import List

from alchemyst_ai import AlchemystAI, APIStatusError, ConflictError


# ---------------------------------------------------------------------------
# Content templates
# ---------------------------------------------------------------------------

V1_CONTENT_TEMPLATE = """\
Refund Policy Document (policy-marker: {marker})

This refund policy applies to all purchases made via our official online
store. Under this policy, customers may request a full refund within
30-day of the original purchase date. Refund requests submitted outside
of this window will not be honored.

policy-marker: {marker}
"""

V2_CONTENT_TEMPLATE = """\
Refund Policy Document (policy-marker: {marker})

This updated refund policy supersedes all prior refund policies for the
same product line. Under the new policy, customers may request a full
refund within 60-day of the original purchase date. The previous refund
window has been extended to 60-day for every customer effective
immediately. Refund requests submitted outside of this 60-day window
will not be honored.

policy-marker: {marker}
"""

# A throwaway document used to deliberately trigger the 409 Conflict.
# Crucially, this content does NOT mention the words "30-day" or "60-day"
# so that, even in the unlikely case Alchemyst persisted it, it would not
# pollute the v2 verification step.
CONFLICT_DOC_CONTENT_TEMPLATE = """\
Intentional conflict document for policy-marker: {marker}.
This payload exists only to provoke a duplicate-fileName conflict and
should never be persisted.
"""

SOURCE = "zealt.update-cycle"
SCOPE = "internal"
CONTEXT_TYPE = "resource"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fatal(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def add_document(client: AlchemystAI, file_name: str, content: str) -> None:
    """Add a single document via the Context Add API."""
    client.v1.context.add(
        context_type=CONTEXT_TYPE,
        scope=SCOPE,
        source=SOURCE,
        documents=[
            {
                "content": content,
                "metadata": {"file_name": file_name},
            }
        ],
    )


def delete_by_file_name(client: AlchemystAI, file_name: str) -> None:
    """
    Delete every document whose `metadata.file_name` matches `file_name`.

    The Python SDK exposes `client.v1.context.delete(**params)`. The shape
    differs from the TypeScript SDK: in the Python SDK, when `by_doc=True`,
    the `source` field carries the document identifier (the file_name). The
    `organization_id` kwarg is required by the SDK's typed signature; the
    backend accepts an empty string when the API key already scopes the
    request to the calling organization.
    """
    client.v1.context.delete(
        organization_id="",
        source=file_name,
        by_doc=True,
        by_id=False,
    )


def search_until_v2(
    client: AlchemystAI,
    query: str,
    marker: str,
    expected_substring: str,
    forbidden_substring: str,
    timeout_seconds: float = 180.0,
    poll_interval_seconds: float = 2.0,
) -> List[str]:
    """
    Poll the Search API until at least one returned chunk for our marker
    contains `expected_substring` and no returned chunk for our marker
    contains `forbidden_substring`.

    Returns the list of chunks that belong to our marker (i.e. our document).
    """
    deadline = time.monotonic() + timeout_seconds
    attempt = 0
    last_chunks: List[str] = []

    while True:
        attempt += 1
        resp = client.v1.context.search(
            query=query,
            minimum_similarity_threshold=0.0,
            similarity_threshold=1.0,
        )

        all_chunks = [
            (ctx.content or "") for ctx in (resp.contexts or []) if ctx.content
        ]
        # Restrict to chunks that belong to *our* document by checking for the
        # unique policy-marker we embedded into the content. This protects us
        # from any noise that other documents in the namespace might add.
        our_chunks = [c for c in all_chunks if marker in c]
        last_chunks = our_chunks

        has_expected = any(expected_substring in c for c in our_chunks)
        has_forbidden = any(forbidden_substring in c for c in our_chunks)

        if has_expected and not has_forbidden:
            return our_chunks

        if time.monotonic() >= deadline:
            raise RuntimeError(
                f"Timed out after {timeout_seconds:.0f}s waiting for search to "
                f"return chunks containing {expected_substring!r} and excluding "
                f"{forbidden_substring!r} for marker {marker!r}. "
                f"Last seen chunks ({len(our_chunks)}): {our_chunks!r}"
            )

        time.sleep(poll_interval_seconds)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        _fatal("ALCHEMYST_AI_API_KEY environment variable is required.")

    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        _fatal("ZEALT_RUN_ID environment variable is required.")

    file_name = f"policy-{run_id}.md"
    marker = f"policy-{run_id}"
    v1_content = V1_CONTENT_TEMPLATE.format(marker=marker)
    v2_content = V2_CONTENT_TEMPLATE.format(marker=marker)
    conflict_content = CONFLICT_DOC_CONTENT_TEMPLATE.format(marker=marker)

    print(f"=== Alchemyst AI document update cycle ===")
    print(f"run_id   = {run_id}")
    print(f"file_name = {file_name}")

    # The SDK reads the API key from ALCHEMYST_AI_API_KEY by default; we
    # still pass it explicitly so the failure mode for a missing key is the
    # _fatal() above rather than a less obvious SDK error.
    client = AlchemystAI(api_key=api_key)

    # -----------------------------------------------------------------
    # Re-runnable pre-cleanup: best-effort delete of any prior state for
    # this run_id. We intentionally swallow errors here because the
    # document may not exist yet on the first run.
    # -----------------------------------------------------------------
    print(f"[pre-cleanup] Deleting any prior document for file_name={file_name} ...")
    try:
        delete_by_file_name(client, file_name)
        print(f"[pre-cleanup] Pre-existing document (if any) cleared for {file_name}.")
    except APIStatusError as e:
        print(
            f"[pre-cleanup] Pre-cleanup returned status {e.status_code}; "
            f"continuing (this is expected on a clean environment)."
        )
    # Small grace period for the backend to settle.
    time.sleep(1.0)

    # -----------------------------------------------------------------
    # Step 1: Add v1.
    # -----------------------------------------------------------------
    add_document(client, file_name, v1_content)
    print(f"[step 1] Added v1 document as file_name={file_name}.")

    # -----------------------------------------------------------------
    # Step 2: Deliberately re-add with the same file_name to provoke the
    # documented 409 Conflict. The SDK retries 409s by default; disable
    # retries here so the conflict surfaces immediately.
    # -----------------------------------------------------------------
    print(
        f"[step 2] Attempting a conflicting re-add of file_name={file_name} "
        f"to verify the 409 Conflict guard ..."
    )
    no_retry_client = client.with_options(max_retries=0)
    try:
        no_retry_client.v1.context.add(
            context_type=CONTEXT_TYPE,
            scope=SCOPE,
            source=SOURCE,
            documents=[
                {
                    "content": conflict_content,
                    "metadata": {"file_name": file_name},
                }
            ],
        )
        # If we get here the backend silently accepted a duplicate, which
        # contradicts the documented behaviour but is not necessarily fatal.
        print(
            "[step 2] WARNING: Expected an HTTP 409 Conflict on re-add but the "
            "request unexpectedly succeeded. Continuing anyway."
        )
    except ConflictError as e:
        print(
            f"[step 2] Observed expected HTTP 409 Conflict on duplicate "
            f"file_name={file_name} (message: {e.message!s})."
        )
    except APIStatusError as e:
        if e.status_code == 409:
            print(
                f"[step 2] Observed expected HTTP 409 Conflict on duplicate "
                f"file_name={file_name}."
            )
        else:
            raise

    # -----------------------------------------------------------------
    # Step 3: Delete by file_name.
    # -----------------------------------------------------------------
    delete_by_file_name(client, file_name)
    print(f"[step 3] Deleted existing document(s) with file_name={file_name}.")
    # Give the backend a moment to propagate the delete before re-adding.
    time.sleep(2.0)

    # -----------------------------------------------------------------
    # Step 4: Add v2.
    # -----------------------------------------------------------------
    add_document(client, file_name, v2_content)
    print(f"[step 4] Added v2 document as file_name={file_name}.")

    # -----------------------------------------------------------------
    # Step 5: Search and verify the v2 content is what comes back.
    # -----------------------------------------------------------------
    query = (
        f"What is the refund window stated in the refund policy document "
        f"with policy-marker {marker}?"
    )
    print(f"[step 5] Searching context for the updated refund policy ...")
    chunks = search_until_v2(
        client,
        query=query,
        marker=marker,
        expected_substring="60-day",
        forbidden_substring="30-day",
        timeout_seconds=180.0,
        poll_interval_seconds=2.0,
    )

    for i, chunk in enumerate(chunks, start=1):
        # Collapse the chunk to a single line so the required substring
        # `60-day` appears on a single search-result line.
        single_line = " ".join(chunk.split())
        print(f"[search-result {i}] {single_line}")

    print("[done] Update cycle completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
