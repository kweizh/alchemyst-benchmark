import os
import subprocess
import pytest
import json

PROJECT_DIR = "/home/user/project"
BATCH_ADD_SCRIPT = os.path.join(PROJECT_DIR, "batch_add.ts")

def test_batch_add_script_exists():
    assert os.path.isfile(BATCH_ADD_SCRIPT), f"The script {BATCH_ADD_SCRIPT} does not exist."

def test_documents_added_to_alchemyst():
    """Priority 1: Use a verification script to query Alchemyst AI via SDK."""
    verify_script = os.path.join(PROJECT_DIR, "verify_context.ts")
    script_content = """
import { AlchemystClient } from '@alchemystai/sdk';

async function verify() {
  const client = new AlchemystClient({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
  const result = await client.v1.context.search({
    query: "policy",
    similarity_threshold: 0.0,
    metadata: { groupName: ["support"] }
  });
  
  const files = result.chunks.map((chunk: any) => chunk.metadata?.file_name || chunk.metadata?.fileName);
  console.log(JSON.stringify(files));
}

verify().catch(console.error);
"""
    with open(verify_script, "w") as f:
        f.write(script_content)

    result = subprocess.run(
        ["npx", "tsx", "verify_context.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Verification script failed: {result.stderr}\\n{result.stdout}"
    
    try:
        # It's possible the output has other logs, find the JSON array
        lines = result.stdout.strip().split('\\n')
        json_line = next(line for line in reversed(lines) if line.startswith('['))
        files = json.loads(json_line)
    except (json.JSONDecodeError, StopIteration):
        pytest.fail(f"Failed to parse JSON output from verify script: {result.stdout}")
        
    assert "policy1.md" in files, f"policy1.md was not found in Alchemyst AI context. Found: {files}"
    assert "policy2.md" in files, f"policy2.md was not found in Alchemyst AI context. Found: {files}"
    assert "policy3.md" in files, f"policy3.md was not found in Alchemyst AI context. Found: {files}"
