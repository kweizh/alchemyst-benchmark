import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/app"
SCRIPT_FILE = os.path.join(PROJECT_DIR, "search_loop.py")
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")

def test_script_exists():
    assert os.path.isfile(SCRIPT_FILE), f"Script file {SCRIPT_FILE} does not exist."

def test_script_execution():
    result = subprocess.run(["python3", "search_loop.py"], cwd=PROJECT_DIR, capture_output=True, text=True)
    assert result.returncode == 0, f"Script execution failed: {result.stderr}"

def test_log_file_exists():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist."

def test_log_file_content():
    with open(LOG_FILE, "r") as f:
        content = f.read()
    assert "Successful searches: 5" in content, f"Log file does not contain 'Successful searches: 5', got: {content}"
