import os
from alchemyst_ai import AlchemystAI

client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "test"))

try:
    res = client.v1.context.memory.add(
        session_id="test-session",
        user_id="test-user-id",
        contents=[{"content": "test memory"}],
    )
    print("SUCCESS", res)
except Exception as e:
    print("ERROR", e)
