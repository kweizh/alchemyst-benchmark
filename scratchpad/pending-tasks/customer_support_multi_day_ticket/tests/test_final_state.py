import os
import subprocess
import pytest
import uuid

PROJECT_DIR = "/home/user/app"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "ticket_manager.py")

def test_script_exists():
    assert os.path.isfile(SCRIPT_PATH), f"Script not found at {SCRIPT_PATH}"

def test_add_and_get_memories():
    session_id = f"ticket_{uuid.uuid4().hex[:8]}"
    user_id = "customer_test"
    
    msg1 = "Day 1: I have a problem with my router."
    msg2 = "Day 2: The router is blinking red."
    
    # Run add msg1
    res1 = subprocess.run(
        ["python3", "ticket_manager.py", "add", user_id, session_id, msg1],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert res1.returncode == 0, f"Failed to add first message: {res1.stderr}\n{res1.stdout}"
    
    # Run add msg2
    res2 = subprocess.run(
        ["python3", "ticket_manager.py", "add", user_id, session_id, msg2],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert res2.returncode == 0, f"Failed to add second message: {res2.stderr}\n{res2.stdout}"
    
    # Run get
    res_get = subprocess.run(
        ["python3", "ticket_manager.py", "get", user_id, session_id],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert res_get.returncode == 0, f"Failed to get messages: {res_get.stderr}\n{res_get.stdout}"
    
    assert msg1 in res_get.stdout, f"Expected first message in output, got: {res_get.stdout}"
    assert msg2 in res_get.stdout, f"Expected second message in output, got: {res_get.stdout}"
