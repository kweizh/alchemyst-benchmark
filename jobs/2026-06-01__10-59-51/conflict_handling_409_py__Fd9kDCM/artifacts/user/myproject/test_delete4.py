import os
from alchemyst_ai import AlchemystAI

client = AlchemystAI(api_key=os.getenv("ALCHEMYST_AI_API_KEY"))
try:
    client.v1.context.delete(source="test", by_doc=True, organization_id="default")
except Exception as e:
    import traceback
    traceback.print_exc()
