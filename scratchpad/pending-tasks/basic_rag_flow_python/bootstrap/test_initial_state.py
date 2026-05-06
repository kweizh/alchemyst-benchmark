import os
import shutil
import pytest

PROJECT_DIR = "/home/user/project"
POLICY_FILE = os.path.join(PROJECT_DIR, "policy.txt")

def test_python_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_policy_file_exists():
    assert os.path.isfile(POLICY_FILE), f"Policy file {POLICY_FILE} does not exist."
    with open(POLICY_FILE, "r") as f:
        content = f.read()
    assert "Electronics can be returned within 14 days" in content, "Policy file does not contain the expected electronics policy."