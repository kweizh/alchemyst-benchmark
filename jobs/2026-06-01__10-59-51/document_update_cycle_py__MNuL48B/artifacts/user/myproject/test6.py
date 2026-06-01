import os
import sys

def main():
    try:
        import alchemyst_ai
        import alchemyst_ai.types.v1.context_delete_params as params
        print("params dir:", dir(params))
        print("ContextDeleteParams:", params.ContextDeleteParams.__annotations__)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
