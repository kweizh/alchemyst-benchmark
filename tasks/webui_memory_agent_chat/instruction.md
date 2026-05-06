# Alchemyst AI WebUI Memory Agent

## Background
Create a Next.js application that implements a chat interface backed by Alchemyst AI's memory agent. This application should allow users to chat with an AI that automatically remembers their preferences across different sessions.

## Requirements
- Initialize a Next.js project in `/home/user/app`.
- Install `ai`, `@alchemystai/aisdk`, and `@ai-sdk/openai`.
- Create an API route `app/api/chat/route.ts` (or `.js`) that accepts a POST request with JSON body containing `{ prompt, userId, sessionId }`.
- The API route must use Vercel AI SDK's `generateText` or `streamText` wrapped with `withAlchemyst` from `@alchemystai/aisdk` to generate a response. Use `openai('gpt-4o-mini')` as the model.
- Create a frontend page (`app/page.tsx`) with:
  - An input field for `userId` (id: `userId`).
  - An input field for `sessionId` (id: `sessionId`).
  - A text input for the chat message (id: `prompt`).
  - A submit button (id: `submit`).
  - A display area for the AI's response (id: `response`).
- When the user submits a message, the app should call the API route and display the AI's response.
- The AI must remember facts stated by a `userId` across different `sessionId`s.

## Constraints
- Project path: `/home/user/app`
- Start command: `npm run build && npm start`
- Port: `3000`
- You must use `@alchemystai/aisdk` to handle memory automatically.