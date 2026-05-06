Your application features a collaborative terminal assistant (CLI Agent) where multiple developers working in a shared terminal session need to benefit from the same conversational context.

You need to write a test script that saves a piece of context to memory as `user_1`, and then successfully retrieves and utilizes that memory in a subsequent generation call made by `user_2`.

**Constraints:**
- Both operations must utilize distinct `userId` parameters to simulate different team members.
- You MUST pass the exact same `sessionId` to both calls to ensure the context is shared correctly at the session level.