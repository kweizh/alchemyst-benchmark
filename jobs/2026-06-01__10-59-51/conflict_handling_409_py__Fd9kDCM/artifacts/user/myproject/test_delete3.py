import os
from alchemyst_ai import AlchemystAI

client = AlchemystAI(api_key=os.getenv("ALCHEMYST_AI_API_KEY"))
print("Client org id:", getattr(client, "organization_id", None))
