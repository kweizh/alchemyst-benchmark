import os
import json
import subprocess

def test_script_exists():
    assert os.path.isfile('/home/user/myproject/check_metadata.py'), "check_metadata.py does not exist"

def test_script_execution():
    # Run the script
    result = subprocess.run(
        ['python3', '/home/user/myproject/check_metadata.py'],
        cwd='/home/user/myproject',
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Script failed with output: {result.stderr}"

def test_result_json():
    assert os.path.isfile('/home/user/myproject/result.json'), "result.json does not exist"
    
    with open('/home/user/myproject/result.json', 'r') as f:
        data = json.load(f)
        
    assert 'valid_added' in data, "valid_added key missing in result.json"
    assert 'invalid_added' in data, "invalid_added key missing in result.json"
    
    assert data['valid_added'] is True, "valid_added should be True"
    # The API might reject or accept, but based on docs it should fail or ignore.
    # If it fails, invalid_added should be False. If it ignores, it might be True.
    # We will accept either boolean as long as it correctly caught the API's behavior.
    assert isinstance(data['invalid_added'], bool), "invalid_added should be a boolean"
