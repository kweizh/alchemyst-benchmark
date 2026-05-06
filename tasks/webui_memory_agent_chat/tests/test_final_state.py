import os
import subprocess
import time
import socket
import pytest
from pochi_verifier import PochiVerifier

PROJECT_DIR = "/home/user/app"

def wait_for_port(port, timeout=120):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(5)
    return False

@pytest.fixture(scope="module")
def start_app():
    # Verify project exists
    assert os.path.exists(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."
    
    # Build the app
    build_process = subprocess.run(
        ["npm", "run", "build"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    assert build_process.returncode == 0, f"npm run build failed: {build_process.stderr}"

    # Start the app
    process = subprocess.Popen(
        ["npm", "start"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for the app to be ready
    if not wait_for_port(3000):
        # Kill the process group before failing
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("App failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

def test_alchemyst_memory_chat(start_app):
    reason = "The application should allow users to chat, and the AI must remember preferences across sessions for the same user, but isolate memories between different users."
    truth = "Navigate to http://localhost:3000. Find the input fields with id 'userId', 'sessionId', 'prompt', and 'submit' button. Set 'userId' to 'test_user_alice' and 'sessionId' to 'session_a'. Set 'prompt' to 'Hi, my favorite color is magenta.' and click submit. Wait for the response to populate in the element with id 'response'. Then, set 'prompt' to 'What is my favorite color?' and click submit. Verify that the response contains 'magenta'. Next, change 'sessionId' to 'session_b' (keep 'userId' as 'test_user_alice'). Set 'prompt' to 'What is my favorite color?' and click submit. Verify that the response still contains 'magenta'. Finally, change 'userId' to 'test_user_bob' and 'sessionId' to 'session_a'. Set 'prompt' to 'What is my favorite color?' and click submit. Verify that the response does NOT contain 'magenta'."

    verifier = PochiVerifier()
    result = verifier.verify(
        reason=reason,
        truth=truth,
        use_browser_agent=True,
        trajectory_dir="/logs/verifier/pochi/test_alchemyst_memory_chat"
    )
    assert result.status == "pass", f"Browser verification failed: {result.reason}"
