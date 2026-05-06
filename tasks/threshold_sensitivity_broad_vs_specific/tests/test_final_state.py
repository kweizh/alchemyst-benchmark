import os
import json
import pytest

PROJECT_DIR = "/home/user/project"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "output.json")

def test_output_json_exists():
    """Priority 3: Check if output.json exists."""
    assert os.path.isfile(OUTPUT_FILE), f"Output file not found at {OUTPUT_FILE}"

def test_output_json_contents():
    """Priority 3: Verify the contents of output.json."""
    with open(OUTPUT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail("output.json is not valid JSON")
    
    assert "count_09" in data, "Missing 'count_09' in output.json"
    assert "count_05" in data, "Missing 'count_05' in output.json"
    assert isinstance(data["count_09"], int), "'count_09' should be an integer"
    assert isinstance(data["count_05"], int), "'count_05' should be an integer"
