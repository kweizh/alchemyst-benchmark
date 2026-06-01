#!/usr/bin/env python3
"""Idempotent ingest CLI for Alchemyst AI context engine.

Performs a single add attempt. On HTTP 409 (Conflict), deletes the
existing document for this run's source and retries the add exactly
once. Always exits 0 along the conflict-recovery path.
"""

from __future__ import annotations

import json
import os
import sys

from alchemyst_ai import AlchemystAI, APIStatusError


def _log(msg: str) -> None:
    print(msg, flush=True)


def main() -> int:
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("ERROR: ALCHEMYST_AI_API_KEY is not set", file=sys.stderr)
        return 2

    run_id = os.environ.get("ZEALT_RUN_ID")
    if not run_id:
        print("ERROR: ZEALT_RUN_ID is not set", file=sys.stderr)
        return 2

    # Disable the SDK's automatic 409 retry so we can observe and
    # explicitly handle the conflict.
    client = AlchemystAI(api_key=api_key, max_retries=0)

    # Both source and metadata.file_name must include the run_id so
    # that the dedup conflict is deterministic and resource-scoped.
    file_name = f"zealt-ingest-{run_id}.txt"
    source = f"zealt-ingest://{run_id}"
    content = (
        f"Idempotent ingest payload for run {run_id}. "
        "This document is used to validate the 409 conflict recovery path."
    )

    document = {"content": content}
    metadata = {"file_name": file_name}

    def do_add() -> None:
        client.v1.context.add(
            context_type="resource",
            scope="internal",
            source=source,
            documents=[document],
            metadata=metadata,
        )

    conflict_resolved = False
    try:
        do_add()
        _log(f"Add succeeded on first attempt for run_id={run_id}")
    except APIStatusError as exc:
        status = getattr(exc, "status_code", None)
        if status == 409:
            _log(
                f"Conflict detected (HTTP 409) for source={source}; "
                "deleting existing document and retrying add."
            )
            # Delete the conflicting document by source. by_doc=True
            # ensures we delete the document keyed by this source only.
            client.v1.context.delete(
                organization_id="",
                source=source,
                by_doc=True,
            )
            _log(f"Deleted existing document(s) for source={source}; retrying add.")
            do_add()
            _log("Retry add succeeded; conflict resolved.")
            conflict_resolved = True
        else:
            # Any non-409 API error surfaces as a non-zero exit.
            raise

    result = {"status": "ok", "conflict_resolved": conflict_resolved}
    _log("RESULT: " + json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
