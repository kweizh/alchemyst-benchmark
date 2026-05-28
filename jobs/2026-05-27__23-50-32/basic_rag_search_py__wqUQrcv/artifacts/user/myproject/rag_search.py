import os
from alchemyst_ai import AlchemystAI
from datetime import datetime

def main():
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    run_id = os.environ.get("ZEALT_RUN_ID", "default")
    
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY environment variable is not set.")
        return

    client = AlchemystAI(api_key=api_key)
    
    content = "Our refund policy: We offer a 30-day money back guarantee. Contact support@example.com to request a refund."
    file_name = f"refund-policy-{run_id}.md"
    
    # Ingest document
    try:
        client.v1.context.add(
            context_type="resource",
            documents=[{"content": content}],
            scope="internal",
            source="docs",
            metadata={
                "file_name": file_name,
                "file_size": float(len(content)),
                "file_type": "text/markdown",
                "last_modified": datetime.now().isoformat()
            }
        )
    except Exception as e:
        print(f"Add failed: {e}")
    
    # Search document
    try:
        response = client.v1.context.search(
            query="What is the refund policy?",
            similarity_threshold=0.7,
            minimum_similarity_threshold=0.0,
            scope="internal"
        )
        
        if response.contexts:
            top_match = response.contexts[0].content
            print(top_match)
            
            log_path = "/home/user/myproject/output.log"
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "w") as f:
                f.write(f"Top Match: {top_match}\n")
        else:
            # If search failed, we might want to try again with different parameters
            # but the requirement says top match content MUST be in log file.
            # If I can't get it from the API, I'll just write it if I'm sure it should be there.
            # But the task says "Run the script so that it actually ingests... and writes the log file."
            # and "After running the script... retrievable from the Alchemyst context engine".
            print("No matches found.")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    main()
