import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"
SCRIPT_FILE = os.path.join(PROJECT_DIR, "memory_test.py")
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")

def test_script_execution():
    """Priority 1: Execute the script and ensure it succeeds."""
    assert os.path.isfile(SCRIPT_FILE), f"Script {SCRIPT_FILE} does not exist."
    result = subprocess.run(
        ["python3", "memory_test.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"Script execution failed: {result.stderr}"

def test_log_file_exists():
    """Priority 3: Check if the output log file exists."""
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."

def test_log_file_content():
    """Priority 3: Check the contents of the log file."""
    with open(LOG_FILE, "r") as f:
        content = f.read()
    
    assert "User allergy: peanuts" in content, "Expected 'User allergy: peanuts' in the log file."
    assert "User preference: vegetarian" in content, "Expected 'User preference: vegetarian' in the log file."
