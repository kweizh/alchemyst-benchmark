import os
import pytest
from alchemystai import Alchemyst

LOG_FILE = "/home/user/alchemyst-rag/output.log"

def test_output_log_exists():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."

def test_output_log_content():
    with open(LOG_FILE, "r") as f:
        content = f.read()
    assert "Retrieved Policy: Policy: 30-day refunds for all electronics" in content, \
        f"Expected log to contain retrieved policy, got: {content}"

def test_document_ingested_in_alchemyst():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is missing."
    
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key, "ALCHEMYST_AI_API_KEY environment variable is missing."
    
    client = Alchemyst(api_key=api_key)
    
    result = client.v1.context.search(
        query="refund policy for electronics",
        similarity_threshold=0.5
    )
    
    expected_file_name = f"refunds-{run_id}.md"
    assert expected_file_name in str(result), \
        f"Expected document with file_name {expected_file_name} not found in search results. Got: {result}"