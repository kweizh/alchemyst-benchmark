import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/myproject"
SCRIPT_PATH = os.path.join(PROJECT_DIR, "memory_test.py")

def test_script_exists():
    """Priority 3: Check if the script exists."""
    assert os.path.isfile(SCRIPT_PATH), f"Script not found at {SCRIPT_PATH}"

def test_script_execution_and_output():
    """Priority 1: Run the script and check output."""
    result = subprocess.run(
        ["python3", "memory_test.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"'python3 memory_test.py' failed: {result.stderr}"
    assert "User prefers Python over JavaScript." in result.stdout, \
        f"Expected memory content in stdout, got: {result.stdout}"

def test_memory_state_via_sdk():
    """Priority 1: Use a temporary python script to verify the memory state via SDK."""
    verifier_script = os.path.join(PROJECT_DIR, "verify_memory.py")
    script_content = '''
import os
import sys
from alchemyst_ai import AlchemystAI

def verify():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Missing API Key")
        sys.exit(1)
        
    alchemyst = AlchemystAI(api_key=api_key)
    
    # Check session A
    result_a = alchemyst.v1.context.memory.search(
        user_id="user_123",
        session_id="session_A"
    )
    
    a_found = False
    if result_a and hasattr(result_a, "memories") and result_a.memories:
        for mem in result_a.memories:
            if hasattr(mem, "content") and "User prefers Python over JavaScript." in mem.content:
                a_found = True
                
    if a_found:
        print("ERROR: Session A memory was not deleted.")
        sys.exit(1)
        
    # Check session B
    result_b = alchemyst.v1.context.memory.search(
        user_id="user_123",
        session_id="session_B"
    )
    
    b_found = False
    if result_b and hasattr(result_b, "memories") and result_b.memories:
        for mem in result_b.memories:
            if hasattr(mem, "content") and "User likes the Django framework." in mem.content:
                b_found = True
                
    if not b_found:
        print("ERROR: Session B memory not found.")
        sys.exit(1)
        
    print("SUCCESS")

if __name__ == "__main__":
    verify()
'''
    with open(verifier_script, "w") as f:
        f.write(script_content)
        
    result = subprocess.run(
        ["python3", "verify_memory.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    
    # Clean up the verifier script
    os.remove(verifier_script)
    
    assert result.returncode == 0, f"Memory state verification failed: {result.stdout} {result.stderr}"
    assert "SUCCESS" in result.stdout, f"Verification script did not output SUCCESS: {result.stdout}"
