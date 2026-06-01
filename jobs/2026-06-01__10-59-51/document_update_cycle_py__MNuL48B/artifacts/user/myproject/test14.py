import os
import sys
import time
from datetime import datetime, timezone

def main():
    try:
        from alchemyst_ai import AlchemystAI
        client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "dummy"))
        
        run_id = "test-409"
        file_name = f"policy-{run_id}.md"
        
        print("Adding doc 3...")
        res = client.v1.context.add(
            context_type="resource",
            scope="internal",
            source="cli_source",
            metadata={
                "file_name": file_name,
                "file_size": 200,
                "file_type": "text/markdown",
                "last_modified": datetime.now(timezone.utc).isoformat()
            },
            documents=[{
                "content": "Content 3",
                "metadata": {"file_name": file_name}
            }]
        )
        print("Add 3 res:", res)
        print("Add 3 vars:", vars(res))
        
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
