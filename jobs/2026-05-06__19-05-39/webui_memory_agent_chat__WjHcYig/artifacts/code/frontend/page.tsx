'use client';

import { useState } from 'react';
import { useChat } from 'ai/react';

export default function Chat() {
  const [userId, setUserId] = useState('user-1');
  const [sessionId, setSessionId] = useState('session-1');
  
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: {
      userId,
      sessionId,
    },
  });

  const lastResponse = messages
    .filter(m => m.role === 'assistant')
    .pop()?.content;

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm flex flex-col gap-4">
        <h1 className="text-2xl font-bold">Alchemyst AI Memory Chat</h1>
        
        <div className="flex flex-col gap-2 w-full">
          <label htmlFor="userId">User ID:</label>
          <input
            id="userId"
            className="p-2 border rounded text-black"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
          />
        </div>

        <div className="flex flex-col gap-2 w-full">
          <label htmlFor="sessionId">Session ID:</label>
          <input
            id="sessionId"
            className="p-2 border rounded text-black"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
          />
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-2 w-full">
          <label htmlFor="prompt">Message:</label>
          <input
            id="prompt"
            className="p-2 border rounded text-black"
            value={input}
            onChange={handleInputChange}
            placeholder="Say something..."
          />
          <button
            id="submit"
            type="submit"
            disabled={isLoading}
            className="bg-blue-500 text-white p-2 rounded disabled:bg-gray-400"
          >
            {isLoading ? 'Sending...' : 'Submit'}
          </button>
        </form>

        <div className="w-full mt-8 p-4 border rounded bg-gray-50 min-h-[100px]">
          <h2 className="font-bold mb-2">AI Response:</h2>
          <div id="response" className="text-black whitespace-pre-wrap">
            {lastResponse || 'No response yet.'}
          </div>
        </div>
        
        <div className="w-full mt-4">
          <h3 className="font-bold">History:</h3>
          <div className="flex flex-col gap-2">
            {messages.map(m => (
              <div key={m.id} className={`p-2 rounded ${m.role === 'user' ? 'bg-blue-100' : 'bg-green-100'} text-black`}>
                <strong>{m.role === 'user' ? 'User: ' : 'AI: '}</strong>
                {m.content}
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
