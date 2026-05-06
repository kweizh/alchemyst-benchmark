import os
import datetime
from alchemyst_ai import AlchemystAI

def main():
    # Initialize AlchemystAI with the ALCHEMYST_AI_API_KEY from the environment
    api_key = os.environ.get("ALCHEMYST_AI_API_KEY")
    if not api_key:
        print("Error: ALCHEMYST_AI_API_KEY not found in environment.")
        return

    client = AlchemystAI(api_key=api_key)

    project_path = "/home/user/project"
    policy_path = f"{project_path}/policy.txt"
    output_path = f"{project_path}/output.txt"

    # Read the policy document
    try:
        with open(policy_path, "r") as f:
            content = f.read()
            file_size = os.path.getsize(policy_path)
    except FileNotFoundError:
        print(f"Error: {policy_path} not found.")
        return

    # Add the document to the context engine
    # Note: The API requires fileSize, fileType, and lastModified in the metadata
    print("Adding document to context...")
    try:
        client.v1.context.add(
            documents=[{"content": content}],
            context_type="resource",
            source="documentation",
            scope="internal",
            metadata={
                "file_name": "policy.txt",
                "file_size": float(file_size),
                "file_type": "text/plain",
                "last_modified": datetime.datetime.now().isoformat() + "Z"
            }
        )
    except Exception as e:
        print(f"Failed to add context: {e}")
        # Even if it fails (e.g. 402 Payment Required), we continue to show the logic
        pass

    # Perform a context search for the query "What is the return policy for electronics?"
    # using a similarity_threshold of 0.7 and scope="internal".
    # Note: minimum_similarity_threshold is also required by the SDK.
    print("Searching context...")
    try:
        search_results = client.v1.context.search(
            query="What is the return policy for electronics?",
            similarity_threshold=0.7,
            minimum_similarity_threshold=0.5,
            scope="internal"
        )

        # Extract the content from the first item in the returned contexts list
        # and write it to /home/user/project/output.txt
        if search_results and hasattr(search_results, 'contexts') and search_results.contexts:
            first_match = search_results.contexts[0].content
            with open(output_path, "w") as f:
                f.write(first_match)
            print(f"Successfully wrote match to {output_path}")
        else:
            print("No matches found or search results empty.")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    main()
