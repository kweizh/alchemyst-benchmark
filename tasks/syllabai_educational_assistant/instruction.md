# SyllabAI Backend Integration

## Background
You need to build the backend API for SyllabAI, an educational assistant that answers questions based on a syllabus. You will use Express.js and the Alchemyst AI SDK.

## Requirements
Create an Express.js server that provides three endpoints:
1. `POST /upload`: Accepts a multipart/form-data file upload (field name `file`), reads its text content, and returns `{ "text": "<file content>" }`.
2. `POST /context/add`: Accepts a JSON payload like `{ "documents": [{ "content": "...", "fileName": "...", "name": "..." }], "source": "user-upload", "context_type": "resource" }`. It should use `@alchemystai/sdk` to add the documents to the context engine and return `{ "success": true }`. Assume the request body matches the Alchemyst API requirements.
3. `POST /chat/generate`: Accepts a JSON payload `{ "chat_history": [{ "type": "human", "id": "1", "lc_kwargs": { "content": "What are the grading policies?" } }] }`. Extract the latest user message content from the `chat_history` array (the last item where `type` is `human`). Use `@alchemystai/aisdk`'s `withAlchemyst` wrapper with `generateText` from the `ai` package (using the `openai` provider, e.g., `openai('gpt-4o-mini')`) to generate a response. The `userId` should be `student_1` and `sessionId` should be `syllabus_chat`. Return the generated text in the exact format: `{ "result": { "response": { "kwargs": { "content": "<assistant response text>" } } } }`.

## Implementation Guide
1. Initialize a Node.js project in `/home/user/syllabai`.
2. Install `express`, `multer`, `@alchemystai/sdk`, `@alchemystai/aisdk`, `ai`, `@ai-sdk/openai`.
3. Create `server.js` that sets up the Express app. Use `multer` to parse the file upload.
4. Use `process.env.ALCHEMYST_AI_API_KEY` and `process.env.OPENAI_API_KEY` for authentication.
5. Start the server on port 3000.

## Constraints
- Project path: /home/user/syllabai
- Start command: `node server.js`
- Port: 3000
- Return proper JSON responses for all endpoints.