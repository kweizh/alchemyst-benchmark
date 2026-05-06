import os
import time
from alchemyst_ai import AlchemystAI

def robust_search(client, query):
    """
    Performs a search using the AlchemystAI SDK with exponential backoff for 429 errors.
    
    Args:
        client: An instance of AlchemystAI.
        query: The search query string.
        
    Returns:
        bool: True if search was successful, False otherwise.
    """
    retries = 0
    delay = 1 # Initial delay in seconds
    
    while retries <= 3:
        try:
            # Call the search API as specified in the requirements
            # Note: minimum_similarity_threshold is added to satisfy the SDK's requirement
            client.v1.context.search(
                query=query,
                similarity_threshold=0.7,
                minimum_similarity_threshold=0.7,
                scope='internal'
            )
            return True
        except Exception as e:
            error_msg = str(e)
            # Check for 429 Rate Limit error in the exception message
            if '429' in error_msg and retries < 3:
                time.sleep(delay)
                retries += 1
                delay *= 2 # Exponential backoff: 1s, 2s, 4s
            else:
                # For other errors or if max retries reached, exit the loop
                return False
    return False

def main():
    # Initialize the AlchemystAI client
    client = AlchemystAI()
    
    success_count = 0
    query = "What is the refund policy?"
    
    # Execute the search 5 times in a row
    for _ in range(5):
        if robust_search(client, query):
            success_count += 1
            
    # Write the number of successful searches to the log file
    log_path = "/home/user/app/output.log"
    with open(log_path, "w") as f:
        f.write(f"Successful searches: {success_count}")

if __name__ == "__main__":
    main()
