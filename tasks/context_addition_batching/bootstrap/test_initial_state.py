import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"
DOCS_DIR = "/home/user/docs"

def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_docs_directory_exists():
    assert os.path.isdir(DOCS_DIR), f"Docs directory {DOCS_DIR} does not exist."

def test_policy_files_exist():
    policies = ["policy1.md", "policy2.md", "policy3.md"]
    for policy in policies:
        path = os.path.join(DOCS_DIR, policy)
        assert os.path.isfile(path), f"Policy file {path} does not exist."

def test_policy1_content():
    path = os.path.join(DOCS_DIR, "policy1.md")
    with open(path) as f:
        content = f.read()
    assert "Refunds are processed within 30 days." in content, f"Expected initial content in {path}."

def test_policy2_content():
    path = os.path.join(DOCS_DIR, "policy2.md")
    with open(path) as f:
        content = f.read()
    assert "Support hours are 9 AM to 5 PM EST." in content, f"Expected initial content in {path}."

def test_policy3_content():
    path = os.path.join(DOCS_DIR, "policy3.md")
    with open(path) as f:
        content = f.read()
    assert "Contact us at support@example.com for urgent issues." in content, f"Expected initial content in {path}."

def test_alchemystai_sdk_installed():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"package.json not found in {PROJECT_DIR}."
    with open(package_json_path) as f:
        content = f.read()
    assert "@alchemystai/sdk" in content, "Expected @alchemystai/sdk to be in package.json."
