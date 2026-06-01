import os
from alchemyst_ai import AlchemystAI

client = AlchemystAI(api_key="test")
print("calling delete")
try:
    res = client.v1.context.delete(source="test", by_doc=True, organization_id="default")
    print("res:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
