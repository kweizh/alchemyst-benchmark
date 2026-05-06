# Context-Aware CLI Agent with Alchemyst AI

## Background
Build a Node.js CLI agent that acts as a context-aware terminal assistant. The agent will accept a question, search Alchemyst AI for relevant context, inject that context into a prompt, and generate a response using OpenAI.

## Requirements
- Initialize a Node.js project in `/home/user/agent`.
- Install `@alchemystai/sdk` and `openai`.
- Create a script `seed.js` that:
  - Initializes `AlchemystAI` with `process.env.ALCHEMYST_AI_API_KEY`.
  - Adds a document with content: `"The secret launch code for Project Nova is 8847-ALPHA."`
  - Sets `context_type: 'resource'`, `source: 'docs'`, `scope: 'internal'`.
  - Adds metadata: `{ file_name: "nova_secret.txt", group_name: ["eng"] }`.
  - Handles potential 409 Conflict errors by either deleting the existing document first (using `fileName: "nova_secret.txt"`) or catching the error gracefully.
- Create a script `agent.js` that:
  - Initializes `AlchemystAI` and `OpenAI`.
  - Takes a user query from the first command-line argument (`process.argv[2]`).
  - Searches Alchemyst AI for the query with `similarity_threshold: 0.7`, `scope: 'internal'`, and filters by metadata for the `eng` group (Note: the TypeScript SDK uses `groupName` for searching).
  - If contexts are found, constructs a prompt:
    `Context:\n<joined context contents>\n\nQuestion: <query>`
  - If no contexts are found, uses the query as the prompt.
  - Calls OpenAI (`gpt-4o-mini` or `gpt-4`) to generate an answer.
  - Prints ONLY the AI's response text to `stdout`.

## Constraints
- Project path: `/home/user/agent`
- Use Node.js 18+.