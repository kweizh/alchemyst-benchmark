import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"
OUTPUT_FILE = os.path.join(PROJECT_DIR, "output.txt")
SCRIPT_FILE = os.path.join(PROJECT_DIR, "rag.py")

def test_script_exists():
    assert os.path.isfile(SCRIPT_FILE), f"rag.py not found at {SCRIPT_FILE}"

def test_script_execution():
    result = subprocess.run(
        ["python3", "rag.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"Script execution failed: {result.stderr}"

def test_output_file_exists():
    assert os.path.isfile(OUTPUT_FILE), f"Output file not found at {OUTPUT_FILE}"

def test_output_file_content():
    with open(OUTPUT_FILE, "r") as f:
        content = f.read()
    assert "Electronics can be returned within 14 days" in content, \
        f"Expected electronics policy snippet in output.txt, got: {content}"