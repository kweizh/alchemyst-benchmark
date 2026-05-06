import os
import subprocess
import pytest

PROJECT_DIR = "/home/user"
LOG_FILE = "/home/user/error.log"

def test_script_execution():
    """Priority 1: Run the user script and verify it executes without crashing."""
    result = subprocess.run(
        ["python3", "test_memory_error.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, \
        f"'python3 test_memory_error.py' failed with error: {result.stderr}"

def test_error_log_exists():
    """Priority 3 fallback: basic file existence check."""
    assert os.path.isfile(LOG_FILE), \
        f"error.log not found at {LOG_FILE}"

def test_error_log_contents():
    """Priority 3 fallback: check that error log contains missing parameter indication."""
    with open(LOG_FILE) as f:
        content = f.read()
    
    assert len(content.strip()) > 0, "error.log is empty"
    # The error might mention MISSING_PARAMETERS or user_id missing
    assert "MISSING_PARAMETERS" in content or "user_id" in content.lower(), \
        f"Expected 'MISSING_PARAMETERS' or 'user_id' in error log, got: {content}"
