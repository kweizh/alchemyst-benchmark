import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { withAlchemyst } from '@alchemystai/aisdk';

export const maxDuration = 30;

export async function POST(req: Request) {
  const { prompt, userId, sessionId } = await req.json();

  const result = await streamText(
    withAlchemyst({
      model: openai('gpt-4o-mini'),
      userId,
      sessionId,
    })({
      messages: [{ role: 'user', content: prompt }],
    })
  );

  return result.toDataStreamResponse();
}
