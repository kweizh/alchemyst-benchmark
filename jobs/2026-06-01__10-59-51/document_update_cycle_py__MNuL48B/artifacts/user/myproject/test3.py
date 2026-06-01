import os
import sys

def main():
    try:
        import alchemyst_ai
        import alchemyst_ai.types.v1.context_add_params as params
        print("params dir:", dir(params))
        import inspect
        print(inspect.getsource(params.Document))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
