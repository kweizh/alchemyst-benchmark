import os
import sys
from datetime import datetime

def main():
    try:
        from alchemyst_ai import AlchemystAI
        client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "dummy"))
        
        run_id = "test-12345"
        file_name = f"policy-{run_id}.md"
        
        print("Adding doc...")
        res = client.v1.context.add(
            context_type="resource",
            scope="internal",
            source="test_source",
            metadata={
                "file_name": file_name,
                "file_size": 100,
                "file_type": "text/markdown",
                "last_modified": datetime.utcnow().isoformat() + "Z"
            },
            documents=[{
                "content": "This is a 30-day refund policy.",
                "metadata": {"file_name": file_name}
            }]
        )
        print("Add res:", res)
        
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
