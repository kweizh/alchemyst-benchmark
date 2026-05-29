import os
import shutil

PROJECT_DIR = "/home/user/alchemyst-task"

def test_node_binary_available():
    assert shutil.which("node") is not None, "node binary not found in PATH."

def test_tsc_binary_available():
    assert shutil.which("tsc") is not None, "tsc binary not found in PATH."

def test_project_dir_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."

def test_package_json_exists():
    package_json_path = os.path.join(PROJECT_DIR, "package.json")
    assert os.path.isfile(package_json_path), f"package.json not found at {package_json_path}."
