import os
import sys

def main():
    try:
        from alchemyst_ai import AlchemystAI
        client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "dummy"))
        
        run_id = "test-12345"
        file_name = f"policy-{run_id}.md"
        
        print("Deleting doc...")
        del_res = client.v1.context.delete(
            organization_id="default",
            source=file_name,
            by_doc=True
        )
        print("Del res:", del_res)
        
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
