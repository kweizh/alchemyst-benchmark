import os
import inspect
from alchemyst_ai import AlchemystAI

client = AlchemystAI(api_key="fake")
print(inspect.signature(client.v1.context.add))
