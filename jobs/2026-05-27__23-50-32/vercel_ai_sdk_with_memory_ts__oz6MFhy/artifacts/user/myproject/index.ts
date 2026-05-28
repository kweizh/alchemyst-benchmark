import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { withAlchemyst } from '@alchemystai/aisdk';
import * as fs from 'fs';

async function main() {
  const runId = process.env.ZEALT_RUN_ID;
  const alchemystApiKey = process.env.ALCHEMYST_AI_API_KEY;
  const openaiApiKey = process.env.OPENAI_API_KEY;

  if (!runId || !alchemystApiKey || !openaiApiKey) {
    console.error('Missing required environment variables: ZEALT_RUN_ID, ALCHEMYST_AI_API_KEY, OPENAI_API_KEY');
    process.exit(1);
  }

  const userId = `harbor-user-${runId}`;
  const sessionAId = `session-a-${runId}`;
  const sessionBId = `session-b-${runId}`;

  const generateTextWithMemory = withAlchemyst(generateText, {
    apiKey: alchemystApiKey,
  });

  const model = openai('gpt-4o-mini');

  console.log('--- Session A (Write) ---');
  await generateTextWithMemory({
    model,
    prompt: 'Please remember that my favorite web framework is Svelte.',
    userId,
    sessionId: sessionAId,
  });
  console.log('Session A completed.');

  console.log('--- Session B (Read) ---');
  const responseB = await generateTextWithMemory({
    model,
    prompt: 'Based on what you remember about me, what is my favorite web framework? Answer in one sentence.',
    userId,
    sessionId: sessionBId,
  });
  console.log('Session B completed.');
  console.log('Response:', responseB.text);

  fs.writeFileSync('/workspace/answer.txt', responseB.text, 'utf-8');
  console.log('Result written to /workspace/answer.txt');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
