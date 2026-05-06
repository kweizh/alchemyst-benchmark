import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/app"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "output.txt")

def test_script_execution():
    """Verify that the script executes successfully and outputs the expected file."""
    result = subprocess.run(
        ["npx", "tsx", "index.ts"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"Script execution failed: {result.stderr}"

def test_output_file_exists_and_content():
    """Verify that output.txt exists and contains the expected content."""
    assert os.path.isfile(OUTPUT_FILE), f"Output file {OUTPUT_FILE} not found."
    
    with open(OUTPUT_FILE, "r") as f:
        content = f.read()
    
    assert "Engineering department guidelines" in content, \
        f"Expected 'Engineering department guidelines' in output.txt, got: {content}"