import os
import sys
import time
from typing import List

import alchemyst_ai
from alchemyst_ai import AlchemystAI


def require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def safe_delete(client: AlchemystAI, organization_id: str, source: str) -> None:
    try:
        client.v1.context.delete(
            organization_id=organization_id,
            source=source,
            by_doc=True,
            by_id=False,
        )
    except alchemyst_ai.APIStatusError:
        pass


def poll_for_v2_content(
    client: AlchemystAI,
    file_name: str,
    query: str,
    timeout_seconds: int = 90,
    interval_seconds: int = 2,
) -> List[str]:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        response = client.v1.context.search(
            minimum_similarity_threshold=0.2,
            similarity_threshold=0.8,
            query=query,
            scope="internal",
            body_metadata={"file_name": file_name},
        )
        contexts = response.contexts or []
        matches = []
        for context in contexts:
            content = (context.content or "").strip()
            if not content:
                continue
            if "60-day" in content and "30-day" not in content:
                matches.append(content)
        if matches:
            return matches
        time.sleep(interval_seconds)

    raise TimeoutError("Timed out waiting for 60-day policy to be indexed.")


def main() -> None:
    run_id = require_env("ZEALT_RUN_ID")
    api_key = require_env("ALCHEMYST_AI_API_KEY")
    organization_id = (
        os.environ.get("ALCHEMYST_AI_ORGANIZATION_ID")
        or os.environ.get("ALCHEMYST_AI_ORG_ID")
        or "default"
    )

    file_name = f"policy-{run_id}.md"
    source = file_name

    client = AlchemystAI(api_key=api_key, max_retries=0)

    safe_delete(client, organization_id, source)

    v1_content = (
        "# Refund Policy\n\n"
        "Customers are eligible for a 30-day refund window from the date of purchase.\n"
    )
    v2_content = (
        "# Refund Policy\n\n"
        "Customers are eligible for a 60-day refund window from the date of purchase.\n"
    )

    client.v1.context.add(
        context_type="resource",
        documents=[{"content": v1_content, "metadata": {"file_name": file_name}}],
        scope="internal",
        source=source,
    )
    print(f"Added v1 document: {file_name}")

    try:
        client.v1.context.add(
            context_type="resource",
            documents=[{"content": v2_content, "metadata": {"file_name": file_name}}],
            scope="internal",
            source=source,
        )
        print("Unexpectedly added duplicate document without conflict.")
        sys.exit(1)
    except alchemyst_ai.ConflictError:
        print(f"Observed expected 409 Conflict when re-adding {file_name}.")
    except alchemyst_ai.APIStatusError as exc:
        if exc.status_code == 409:
            print(f"Observed expected 409 Conflict when re-adding {file_name}.")
        else:
            raise

    client.v1.context.delete(
        organization_id=organization_id,
        source=source,
        by_doc=True,
        by_id=False,
    )
    print(f"Deleted existing document by file_name: {file_name}")

    client.v1.context.add(
        context_type="resource",
        documents=[{"content": v2_content, "metadata": {"file_name": file_name}}],
        scope="internal",
        source=source,
    )
    print(f"Added v2 document: {file_name}")

    try:
        matches = poll_for_v2_content(
            client,
            file_name=file_name,
            query="What is the refund policy window?",
        )
    except TimeoutError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    for content in matches:
        print(f"Search result: {content}")


if __name__ == "__main__":
    main()
