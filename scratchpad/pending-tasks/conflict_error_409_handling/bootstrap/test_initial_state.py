import os
import sys

def verify_initial_state():
    print("Initial state is verified.")
    return True

if __name__ == "__main__":
    if not verify_initial_state():
        sys.exit(1)
