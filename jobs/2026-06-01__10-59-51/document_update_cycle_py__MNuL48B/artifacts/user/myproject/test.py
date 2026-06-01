import os
import sys

def main():
    try:
        import alchemyst_ai
        from alchemyst_ai import AlchemystAI
        
        client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "dummy"))
        print("SDK imported successfully.")
        
        print("Delete signature:", dir(client.v1.context.delete))
        import inspect
        print(inspect.signature(client.v1.context.delete))
        print(inspect.signature(client.v1.context.add))
        print(inspect.signature(client.v1.context.search))
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
