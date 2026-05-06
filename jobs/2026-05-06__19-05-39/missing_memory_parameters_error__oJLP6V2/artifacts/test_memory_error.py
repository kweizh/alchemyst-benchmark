import os
from alchemyst_ai import AlchemystAI

def test_memory_error():
    # Initialize the client with a dummy API key if not set in environment
    api_key = os.getenv("ALCHEMYST_AI_API_KEY", "dummy_key")
    alchemyst = AlchemystAI(api_key=api_key)

    log_file_path = "/home/user/error.log"

    try:
        # Intentionally omit user_id to trigger MISSING_PARAMETERS error
        # Passing contents and session_id as per the implementation guide's logic
        alchemyst.v1.context.memory.add(
            session_id="test_session",
            contents=[{"content": "test content"}]
        )
    except Exception as e:
        # The requirement is to write the string representation of the exception to the log
        # Given the environment, we might get a 401/402/404 because of the dummy key,
        # but the task is to catch the exception and log it.
        # If we wanted to simulate MISSING_PARAMETERS specifically, we would need a valid API key
        # and a backend that validates user_id.
        # However, the instructions say "attempt to add... but intentionally omit the user_id parameter... catch the resulting exception".
        with open(log_file_path, "w") as f:
            f.write(str(e))
        print(f"Exception caught and written to {log_file_path}")
    else:
        print("No exception was raised. This was unexpected.")

if __name__ == "__main__":
    test_memory_error()
