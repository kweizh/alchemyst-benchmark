import os
import sys

def main():
    try:
        import alchemyst_ai
        from alchemyst_ai import AlchemystAI
        client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "dummy"))
        
        # Let's inspect the context_add_params.Document and context_add_params.Metadata
        import alchemyst_ai.types.v1.context_add_params as params
        print("Document:", params.Document.__annotations__)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
