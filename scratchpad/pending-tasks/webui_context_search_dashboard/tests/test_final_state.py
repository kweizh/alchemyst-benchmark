import os
import subprocess
import time
import socket
import pytest
from pochi_verifier import PochiVerifier

PROJECT_DIR = "/home/user/dashboard"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(5)
    return False

@pytest.fixture(scope="module")
def start_app():
    # Build the app
    subprocess.run(["npm", "run", "build"], cwd=PROJECT_DIR, check=True)
    
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

def test_alchemyst_dashboard(start_app):
    reason = "The application should feature a fully functional dashboard for ingesting and searching documents using Alchemyst AI."
    truth = "Navigate to http://localhost:3000. In the Ingest form, enter content 'Refund policy: 30 days no questions asked.', file name 'refund_v1.txt', and group name 'support,policies'. Click the Ingest button. Verify that the element with id `ingest-success` appears. In the Ingest form, submit the EXACT SAME file name 'refund_v1.txt' with content 'Refund policy: 15 days only.' and group name 'support,policies'. Click the Ingest button. Verify that the element with id `ingest-success` appears again (verifying the 409 conflict handling works). In the Search form, enter query 'How many days for refund?', and group name 'support,policies'. Click the Search button. Verify that the `search-results` div contains both '30 days' and '15 days' text (or at least one of them, proving the search works and filtering by groupName succeeds). In the Search form, enter query 'How many days for refund?' and group name 'engineering'. Click the Search button. Verify that the `search-results` div does NOT contain the refund policy text (proving Context Arithmetic intersection filtering works)."

    verifier = PochiVerifier()
    result = verifier.verify(
        reason=reason,
        truth=truth,
        use_browser_agent=True,
        trajectory_dir="/logs/verifier/pochi/test_alchemyst_dashboard"
    )
    assert result.status == "pass", f"Browser verification failed: {result.reason}"
