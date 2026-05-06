import os
import subprocess
import time
import socket
import pytest
import json
import urllib.request
import urllib.error

PROJECT_DIR = "/home/user/syllabai"

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(2)
    return False

@pytest.fixture(scope="module")
def start_app():
    assert os.path.isfile(os.path.join(PROJECT_DIR, "server.js")), "server.js not found."
    
    # Start the app
    process = subprocess.Popen(
        ["node", "server.js"],
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
        pytest.fail("Server failed to start and listen on port 3000.")

    yield

    # Shut down the app
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_server_js_exists():
    assert os.path.isfile(os.path.join(PROJECT_DIR, "server.js")), "server.js does not exist."

def test_upload_endpoint(start_app):
    import urllib.request
    import email.generator
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    msg = MIMEMultipart("form-data")
    part = MIMEText("Syllabus: Midterm is 30%", "plain")
    part.add_header("Content-Disposition", 'form-data; name="file"; filename="test.txt"')
    msg.attach(part)
    
    boundary = msg.get_boundary()
    body = msg.as_string().split(f"--{boundary}\n", 1)[1]
    
    req = urllib.request.Request("http://localhost:3000/upload", data=body.encode('utf-8'))
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected 200 OK, got {response.status}"
            data = json.loads(response.read().decode('utf-8'))
            assert data.get("text") == "Syllabus: Midterm is 30%", f"Expected text 'Syllabus: Midterm is 30%', got {data}"
    except urllib.error.URLError as e:
        pytest.fail(f"Upload request failed: {e}")

def test_context_add_endpoint(start_app):
    payload = {
        "documents": [
            {
                "content": "Syllabus: Midterm is 30%",
                "fileName": "test.txt",
                "name": "Test Syllabus"
            }
        ],
        "source": "user-upload",
        "context_type": "resource"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request("http://localhost:3000/context/add", data=data)
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected 200 OK, got {response.status}"
            res_data = json.loads(response.read().decode('utf-8'))
            assert res_data.get("success") is True, f"Expected success: true, got {res_data}"
    except urllib.error.URLError as e:
        pytest.fail(f"Context add request failed: {e}")

def test_chat_generate_endpoint(start_app):
    payload = {
        "chat_history": [
            {
                "type": "human",
                "id": "1",
                "lc_kwargs": {
                    "content": "What is the midterm weight?"
                }
            }
        ]
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request("http://localhost:3000/chat/generate", data=data)
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            assert response.status == 200, f"Expected 200 OK, got {response.status}"
            res_data = json.loads(response.read().decode('utf-8'))
            assert "result" in res_data, "Response missing 'result' key"
            assert "response" in res_data["result"], "Response missing 'result.response' key"
            assert "kwargs" in res_data["result"]["response"], "Response missing 'result.response.kwargs' key"
            assert "content" in res_data["result"]["response"]["kwargs"], "Response missing 'result.response.kwargs.content' key"
            content = res_data["result"]["response"]["kwargs"]["content"]
            assert isinstance(content, str) and len(content) > 0, "Content should be a non-empty string"
    except urllib.error.URLError as e:
        pytest.fail(f"Chat generate request failed: {e}")
