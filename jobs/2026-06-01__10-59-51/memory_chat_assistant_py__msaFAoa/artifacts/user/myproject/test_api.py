import os
from alchemyst_ai import AlchemystAI

client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "test"))

try:
    res = client.v1.context.memory.add(
        session_id="test-session",
        contents=[{"content": "test memory"}],
        extra_body={"userId": "test-user-id"}
    )
    print("SUCCESS", res)
except Exception as e:
    print("ERROR", e)
