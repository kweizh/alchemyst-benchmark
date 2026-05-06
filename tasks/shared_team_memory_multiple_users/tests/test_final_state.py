import os
import json
import pytest

PROJECT_DIR = "/home/user/project"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "shared_memory.json")

def test_output_file_exists():
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} does not exist."

def test_output_file_content():
    with open(OUTPUT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail(f"File {OUTPUT_FILE} does not contain valid JSON.")
            
    assert isinstance(data, list), f"Expected JSON data to be a list, got {type(data)}."
    
    alice_msg = "Alice: Let's use PostgreSQL for the new database."
    bob_msg = "Bob: I agree, PostgreSQL is a solid choice."
    
    assert any(alice_msg in str(item) for item in data), \
        f"Expected to find Alice's message in the shared memory output, got: {data}"
        
    assert any(bob_msg in str(item) for item in data), \
        f"Expected to find Bob's message in the shared memory output, got: {data}"
