import inspect
from alchemyst_ai import AlchemystAI

client = AlchemystAI(api_key="test")
print("SEARCH:")
print(inspect.signature(client.v1.context.search))
print("MEMORY ADD:")
print(inspect.signature(client.v1.context.memory.add))
