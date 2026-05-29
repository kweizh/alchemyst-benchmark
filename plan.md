# Alchemyst AI Evaluation Dataset Research
### 1. Library Overview
*   **Description**: Alchemyst AI is a "Context Engine" designed to provide AI agents with persistent memory, business-specific data, and operational context. It acts as a standalone context layer that handles document chunking, embedding generation, and retrieval, as well as cross-session user memory management.
*   **Ecosystem Role**: It serves as the "Pareto Frontier" for AI context, fitting between the LLM (e.g., OpenAI, Anthropic) and the application's data sources. It replaces or enhances manual RAG implementations with "Context Arithmetic" and built-in memory management.
*   **Project Setup**:
    *   **JavaScript/TypeScript**: `npm install @alchemystai/sdk`
    *   **Python**: `pip install alchemystai`
    *   **Vercel AI SDK**: `npm install ai @alchemystai/aisdk`
    *   **Configuration**: Requires an `ALCHEMYST_AI_API_KEY` from the [Alchemyst Platform](https://platform.getalchemystai.com/).
### 2. Core Primitives & APIs
*   **Context Addition (`v1.context.add`)**: Ingests documents into the context engine.
    *   **Snippet (TS)**:
        ```typescript
        await client.v1.context.add({
          documents: [{ content: "Policy: 30-day refunds", metadata: { file_name: "refunds.md", group_name: ["support"] } }],
          context_type: 'resource',
          source: 'docs',
          scope: 'internal'
        });
        ```
*   **Context Search (`v1.context.search`)**: Retrieves relevant chunks based on a query and "Context Arithmetic" (filters).
    *   **Snippet (Python)**:
        ```python
        result = client.v1.context.search(
            query="What is the refund policy?",
            similarity_threshold=0.7,
            metadata={"group_name": ["support"]}
        )
        ```
*   **Memory Management (`v1.context.memory.add/search`)**: Manages conversation history and user preferences across sessions using `userId` and `sessionId`.
    *   **Snippet (TS - AI SDK Middleware)**:
        ```typescript
        const generateTextWithMemory = withAlchemyst(generateText, { apiKey: process.env.ALCHEMYST_AI_API_KEY });
        const { text } = await generateTextWithMemory({ model: "openai:gpt-4", prompt: "I'm vegan", userId: "user_1", sessionId: "session_A" });
        ```
*   **Key Documentation Links**:
    *   [OpenAPI Reference](https://platform-backend.getalchemystai.com/api/openapi.json)
    *   [Contextual AI Quickstart](https://getalchemystai.com/docs/getting-started/quickstart)
    *   [Memory Agent Quickstart](https://getalchemystai.com/docs/getting-started/quickstart-memory)
### 3. Real-World Use Cases & Templates
*   **Customer Support**: Using memory to retain context across multi-day support tickets.
*   **SyllabAI**: Educational tool for uploading syllabi and getting personalized study assistance. [Link](https://getalchemystai.com/docs/example-projects/team/syllabai)
*   **Zendocs**: Automated SEO and indexing tool. [Link](https://getalchemystai.com/docs/example-projects/team/zendocs)
*   **CLI Agent**: A context-aware terminal assistant. [Link](https://getalchemystai.com/docs/example-projects/team/cli-chatbot)
*   **B2B Newsletter Writer**: Agentic workflow for researching and writing newsletters. [Link](https://getalchemystai.com/docs/example-projects/community/b2b-newsletter-writer)
### 4. Developer Friction Points
*   **Conflict Errors (409)**: Attempting to `add` a document with an existing `file_name` in metadata triggers a `409 Conflict`. Developers must delete the old version first or use unique identifiers. [Troubleshooting Link](https://getalchemystai.com/docs/advanced/troubleshooting#common-errors-add)
*   **Parameter Inconsistency**: In the TypeScript SDK, storage uses `group_name` (snake_case) but search uses `groupName` (camelCase). Python uses `group_name` consistently. [Quickstart Link](https://getalchemystai.com/docs/getting-started/quickstart#advanced-organize-with-metadata)
*   **Memory Prerequisites**: Both `userId` and `sessionId` are strictly required for memory operations; omitting one results in a `MISSING_PARAMETERS` error. [Memory Troubleshooting](https://getalchemystai.com/docs/getting-started/quickstart-memory#troubleshooting)
*   **Metadata Limitations**: Metadata values must be `string` or `number` only; nested objects or arrays (other than `group_name`) may fail or be ignored.
### 5. Evaluation Ideas
1.  **Basic RAG Flow**: Store a specific policy document and verify the agent can retrieve it to answer a related question.
2.  **Multi-Session Memory**: Have a user state a preference in Session A and verify the agent remembers it in Session B.
3.  **Context Arithmetic (Intersection)**: Store documents across multiple groups (e.g., `['eng', 'v1']` and `['eng', 'v2']`) and verify search only returns results when filtering for the correct intersection.
4.  **Document Update Cycle**: Implement a task where a document is updated by first deleting the old version (by `file_name`) and then adding the new one.
5.  **Shared Team Memory**: Simulate two different `userId`s participating in the same `sessionId` and verify shared context.
6.  **Rate Limit Resilience**: Implement a search loop that handles `429 Rate Limit` errors using exponential backoff provided by the SDK.
7.  **Threshold Sensitivity**: Test how changing the `similarity_threshold` from 0.9 to 0.5 affects recall for broad vs. specific queries.
### 6. Sources
1.  [Alchemyst AI Homepage](https://getalchemystai.com/): Product overview and high-level features.
2.  [Alchemyst AI Docs (llms.txt)](https://getalchemystai.com/docs/llms.txt): Comprehensive index of all documentation pages.
3.  [Contextual AI Quickstart](https://getalchemystai.com/docs/getting-started/quickstart.md): Detailed RAG implementation guide and code snippets.
4.  [Memory Agent Quickstart](https://getalchemystai.com/docs/getting-started/quickstart-memory.md): Guide for session-based and cross-session memory.
5.  [Context Arithmetic](https://getalchemystai.com/docs/advanced/context-arithmetic.md): Deep dive into the logic of context selection and filtering.
6.  [Troubleshooting & Limits](https://getalchemystai.com/docs/advanced/troubleshooting.md): List of API errors, rate limits, and common pitfalls.