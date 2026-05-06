A key feature of your AI application is retaining user dietary preferences across different login sessions using the `@alchemystai/aisdk` integration.

You need to implement an API route using the Vercel AI SDK that wraps `generateText` with the `withAlchemyst` middleware to store and retrieve a user stating "I'm vegan". 

**Constraints:**
- You MUST supply both `userId` and `sessionId` in the options; omitting either will trigger a `MISSING_PARAMETERS` error.
- You must use the `openai:gpt-4` model configuration as specified in the Alchemyst quickstart.