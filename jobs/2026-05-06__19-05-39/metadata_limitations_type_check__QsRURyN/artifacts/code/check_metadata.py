import os
import json
from alchemyst_ai import AlchemystAI

def main():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    client = AlchemystAI(api_key=api_key)

    results = {
        "valid_added": False,
        "invalid_added": False
    }

    # 1. Valid metadata
    try:
        client.v1.context.add(
            context_type="resource",
            source="docs",
            scope="internal",
            documents=[{"content": "Valid metadata test"}],
            metadata={
                "file_name": "valid.txt",
                "version": 1,
                "group_name": ["group1"],
                "file_size": 1024,
                "file_type": "text/plain",
                "last_modified": "2023-10-27T10:00:00Z"
            }
        )
        results["valid_added"] = True
    except Exception as e:
        print(f"Error adding valid metadata: {e}")
        results["valid_added"] = False

    # 2. Invalid metadata
    try:
        client.v1.context.add(
            context_type="resource",
            source="docs",
            scope="internal",
            documents=[{"content": "Invalid metadata test"}],
            metadata={
                "file_name": "invalid.txt",
                "nested_data": {"key": "value"},
                "file_size": 1024,
                "file_type": "text/plain",
                "last_modified": "2023-10-27T10:00:00Z"
            }
        )
        results["invalid_added"] = True
    except Exception as e:
        print(f"Error adding invalid metadata: {e}")
        results["invalid_added"] = False

    # Write result.json
    output_path = "/home/user/myproject/result.json"
    with open(output_path, "w") as f:
        json.dump(results, f)
    
    print(f"Results written to {output_path}: {results}")

if __name__ == "__main__":
    main()
