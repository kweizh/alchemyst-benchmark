import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/alchemyst-memory"

def test_script_execution():
    """Run the script and verify it correctly stores and retrieves memory across sessions."""
    run_id = os.environ.get("ZEALT_RUN_ID", "default-run-id")
    
    script_path = os.path.join(PROJECT_DIR, "run.py")
    assert os.path.isfile(script_path), f"Script not found at {script_path}"

    user_id = f"user-{run_id}"
    session_a = f"session-a-{run_id}"
    session_b = f"session-b-{run_id}"
    preference = "I am allergic to peanuts"

    cmd = [
        "python3",
        script_path,
        "--user-id", user_id,
        "--session-a", session_a,
        "--session-b", session_b,
        "--preference", preference
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR
    )

    assert result.returncode == 0, f"Script execution failed with error: {result.stderr}"
    
    stdout = result.stdout
    assert "Retrieved:" in stdout, f"Expected 'Retrieved:' in stdout, got: {stdout}"
    assert preference in stdout, f"Expected preference '{preference}' in stdout, got: {stdout}"
