import os
from alchemyst_ai import AlchemystAI

client = AlchemystAI(api_key=os.environ.get("ALCHEMYST_AI_API_KEY", "test"))

try:
    res = client.v1.context.search(
        query="hello",
        scope="internal",
        user_id="test-user-id",
        minimum_similarity_threshold=0.0,
        similarity_threshold=1.0
    )
    print("SUCCESS", res)
    print("DIR", dir(res))
    if hasattr(res, "model_dump"):
        print("DUMP", res.model_dump())
except Exception as e:
    print("ERROR", e)
