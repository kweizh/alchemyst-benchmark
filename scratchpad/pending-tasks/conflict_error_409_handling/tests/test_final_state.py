import os
import sys
import json
import time

def verify_final_state():
    log_file = "/home/user/myproject/output.log"
    if not os.path.exists(log_file):
        print(f"Log file {log_file} does not exist.")
        return False
        
    with open(log_file, "r") as f:
        content = f.read()
        if "Update successful" not in content:
            print("Log file does not contain 'Update successful'.")
            return False

    print("Final state verified.")
    return True

if __name__ == "__main__":
    if not verify_final_state():
        sys.exit(1)
