import os
import time
from datetime import datetime
from alchemyst_ai import AlchemystAI

client = AlchemystAI()

run_id = os.environ.get("ZEALT_RUN_ID", "test-run-1")

metadata = {
    "file_name": f"test_doc_{run_id}.txt",
    "file_size": 100,
    "file_type": "text/plain",
    "group_name": [run_id],
    "last_modified": datetime.utcnow().isoformat() + "Z"
}

print("Adding context...")
resp = client.v1.context.add(
    context_type="resource",
    documents=[{"content": "This is a test document about company refund policy. We offer 30 day refunds."}],
    scope="internal",
    source="test",
    metadata=metadata
)
print("Add response:", resp)

time.sleep(5)

print("Searching context...")
search_resp = client.v1.context.search(
    minimum_similarity_threshold=0.1,
    query="What is our company refund policy?",
    similarity_threshold=0.5,
    body_metadata={"groupName": [run_id]},
    scope="internal"
)
print("Search response:", search_resp)
