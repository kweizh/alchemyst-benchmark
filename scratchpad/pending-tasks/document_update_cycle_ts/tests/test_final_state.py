import os
import pytest

def test_output_log_exists():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id is not None, "ZEALT_RUN_ID environment variable is not set."
    
    log_path = "/home/user/alchemyst-task/output.log"
    assert os.path.isfile(log_path), f"Log file not found at {log_path}."
    
    with open(log_path, "r") as f:
        content = f.read()
        
    expected_msg = f"Update cycle successful: policy-{run_id}.md"
    assert expected_msg in content, f"Expected success message '{expected_msg}' not found in log file. Content: {content}"

def test_alchemyst_context_updated():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id is not None, "ZEALT_RUN_ID environment variable is not set."
    
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    assert api_key is not None, "ALCHEMYST_AI_API_KEY environment variable is not set."
    
    try:
        from alchemystai import Alchemyst
    except ImportError:
        pytest.fail("alchemystai Python SDK is not installed in the verification environment.")
        
    client = Alchemyst(api_key=api_key)
    
    # Search for the document
    group_name = f"update-test-{run_id}"
    
    # We use a broad query to fetch the document
    response = client.v1.context.search(
        query="refund policy",
        similarity_threshold=0.1,
        metadata={"group_name": [group_name]}
    )
    
    chunks = response.get("chunks", []) if isinstance(response, dict) else getattr(response, "chunks", [])
    
    assert len(chunks) > 0, f"No documents found in group {group_name}."
    
    all_text = " ".join([chunk.get("text", "") if isinstance(chunk, dict) else getattr(chunk, "text", "") for chunk in chunks])
    
    expected_new = "Updated refund policy: 60-day refunds."
    expected_old = "Old refund policy: 30-day refunds."
    
    assert expected_new in all_text, f"Expected new content '{expected_new}' not found in search results. Found: {all_text}"
    assert expected_old not in all_text, f"Old content '{expected_old}' was found in search results, meaning it was not properly deleted."
