import os
import subprocess
import json
import pytest

PROJECT_DIR = "/home/user/project"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "output.json")

def test_script_execution():
    """Verify that the script runs successfully."""
    script_path = os.path.join(PROJECT_DIR, "search_union.py")
    assert os.path.isfile(script_path), f"Script not found at {script_path}"
    
    result = subprocess.run(["python3", "search_union.py"], cwd=PROJECT_DIR, capture_output=True, text=True)
    assert result.returncode == 0, f"Script execution failed: {result.stderr}"

def test_output_file_exists_and_contains_results():
    """Verify that output.json exists and contains exactly the two engineering documents."""
    # We depend on script execution, but pytest runs tests in order if not parallelized. 
    # Better to run the script in a fixture or just assume test_script_execution runs first.
    # Actually, in Harbor, the user agent will run the script, so test_final_state just verifies the output.
    # But truth says: Setup: `python3 search_union.py`
    # So we should run it here if it hasn't been run, or just run it.
    
    # Run the script to generate the output
    subprocess.run(["python3", "search_union.py"], cwd=PROJECT_DIR, capture_output=True, text=True)
    
    assert os.path.isfile(OUTPUT_FILE), f"Output file not found at {OUTPUT_FILE}"
    
    with open(OUTPUT_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            pytest.fail(f"Output file {OUTPUT_FILE} is not valid JSON.")
            
    assert isinstance(data, list), "Output should be a JSON list."
    assert len(data) == 2, f"Output list should contain exactly 2 items, found {len(data)}"
    
    assert "Engineering V1 Architecture" in data, "Expected 'Engineering V1 Architecture' in output."
    assert "Engineering V2 Architecture" in data, "Expected 'Engineering V2 Architecture' in output."
    assert "Sales Playbook" not in data, "Did not expect 'Sales Playbook' in output."
