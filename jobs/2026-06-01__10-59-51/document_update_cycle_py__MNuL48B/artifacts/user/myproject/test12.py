import os
import sys
import time
from datetime import datetime

def main():
    try:
        from alchemyst_ai import AlchemystAI
        client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "dummy"))
        
        run_id = "test-123456"
        file_name = f"policy-{run_id}.md"
        
        print("Adding doc...")
        client.v1.context.add(
            context_type="resource",
            scope="internal",
            source="my_source",
            metadata={
                "file_name": file_name,
                "file_size": 100,
                "file_type": "text/markdown",
                "last_modified": datetime.now().isoformat() + "Z"
            },
            documents=[{
                "content": f"Content {run_id}",
                "metadata": {"file_name": file_name}
            }]
        )
        time.sleep(2)
        print("Searching...")
        search_res = client.v1.context.search(
            query=f"Content {run_id}",
            minimum_similarity_threshold=0.1,
            similarity_threshold=0.1
        )
        print("Search docs:", len(search_res.documents) if hasattr(search_res, 'documents') else search_res)
        
        print("Deleting by doc...")
        del_res = client.v1.context.delete(
            organization_id="default",
            source=file_name,
            by_doc=True
        )
        print("Del res:", del_res)
        
        time.sleep(2)
        print("Searching again...")
        search_res2 = client.v1.context.search(
            query=f"Content {run_id}",
            minimum_similarity_threshold=0.1,
            similarity_threshold=0.1
        )
        print("Search 2 docs:", len(search_res2.documents) if hasattr(search_res2, 'documents') else search_res2)
        
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
