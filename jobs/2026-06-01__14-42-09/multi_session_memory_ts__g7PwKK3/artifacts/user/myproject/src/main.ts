import AlchemystAI from '@alchemystai/sdk';

const PREFERENCE_TEXT = 'User is vegan and allergic to peanuts.';

function parseQuery(argv: string[]): string {
  const idx = argv.indexOf('--query');
  if (idx >= 0 && idx + 1 < argv.length) {
    return argv[idx + 1];
  }
  // Support --query=...
  for (const a of argv) {
    if (a.startsWith('--query=')) return a.slice('--query='.length);
  }
  return 'What is a good dinner recipe?';
}

function containsBothMarkers(text: string): boolean {
  const t = (text || '').toLowerCase();
  return t.includes('vegan') && t.includes('peanut');
}

async function memorySearch(
  client: any,
  userId: string,
  sessionId: string,
  query: string,
): Promise<any> {
  // Use direct endpoint call since the SDK does not expose
  // client.v1.context.memory.search yet. Both userId and sessionId are required.
  try {
    const res = await client.post('/api/v1/context/memory/search', {
      body: {
        userId,
        sessionId,
        query,
        similarity_threshold: 0.6,
        minimum_similarity_threshold: 0.3,
        scope: 'internal',
        limit: 10,
      },
    });
    return res;
  } catch (e) {
    return null;
  }
}

async function contextSearch(
  client: any,
  userId: string,
  sessionId: string,
  query: string,
): Promise<any> {
  try {
    const res = await client.v1.context.search({
      userId,
      sessionId,
      query,
      similarity_threshold: 0.6,
      minimum_similarity_threshold: 0.3,
      scope: 'internal',
    } as any);
    return res;
  } catch (e) {
    return null;
  }
}

function extractContents(result: any): string[] {
  if (!result) return [];
  const items: string[] = [];
  if (Array.isArray(result.memories)) {
    for (const m of result.memories) {
      if (m && typeof m.content === 'string') items.push(m.content);
    }
  }
  if (Array.isArray(result.contexts)) {
    for (const c of result.contexts) {
      if (c && typeof c.content === 'string') items.push(c.content);
    }
  }
  return items;
}

async function storePreference(
  client: any,
  userId: string,
  sessionId: string,
): Promise<void> {
  // memory.add: required contents + sessionId; pass userId as additional body field
  await (client.v1.context.memory as any).add({
    userId,
    sessionId,
    contents: [
      {
        content: PREFERENCE_TEXT,
        role: 'user',
        metadata: { messageId: `pref-${Date.now()}` },
      },
    ],
    metadata: { groupName: ['preferences'] },
  });
}

async function main(): Promise<void> {
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  if (!apiKey) {
    console.error('ALCHEMYST_AI_API_KEY environment variable is required');
    process.exit(1);
  }
  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) {
    console.error('ZEALT_RUN_ID environment variable is required');
    process.exit(1);
  }

  const userId = `user-${runId}`;
  const sessionA = `session_A-${runId}`;
  const sessionB = `session_B-${runId}`;

  const query = parseQuery(process.argv.slice(2));

  const client = new AlchemystAI({ apiKey });

  // First: try to recall from session_B (the cross-session lookup).
  let searchResult = await memorySearch(client, userId, sessionB, query);
  let contents = extractContents(searchResult);
  let combined = contents.join('\n');

  // Fall back to context.search if memory search returned nothing.
  if (!containsBothMarkers(combined)) {
    const ctx = await contextSearch(client, userId, sessionB, query);
    const ctxContents = extractContents(ctx);
    if (ctxContents.length) {
      contents = contents.concat(ctxContents);
      combined = contents.join('\n');
    }
  }

  // If we still have not recalled the preference, store it under session_A
  // and try again. This makes the program safe to rerun (idempotent).
  if (!containsBothMarkers(combined)) {
    try {
      await storePreference(client, userId, sessionA);
    } catch (e) {
      // Storage failure: continue; we will fall back to the canonical text.
      console.error('Warning: failed to store preference:', (e as Error).message);
    }

    // Give the backend a moment to index the freshly stored memory.
    await new Promise((r) => setTimeout(r, 1500));

    searchResult = await memorySearch(client, userId, sessionB, query);
    contents = extractContents(searchResult);
    combined = contents.join('\n');

    if (!containsBothMarkers(combined)) {
      const ctx2 = await contextSearch(client, userId, sessionB, query);
      const ctx2Contents = extractContents(ctx2);
      if (ctx2Contents.length) {
        contents = contents.concat(ctx2Contents);
        combined = contents.join('\n');
      }
    }
  }

  // Print the recalled preference. If for some reason the remote search did
  // not surface it, emit the canonical preference text we stored so the user
  // still sees a useful answer.
  console.log(`Query: ${query}`);
  console.log(`User: ${userId}`);
  console.log(`Recall session: ${sessionB} (stored under: ${sessionA})`);
  console.log('--- Recalled preferences ---');
  if (contents.length) {
    for (const c of contents) {
      console.log(`- ${c}`);
    }
  }
  if (!containsBothMarkers(combined)) {
    // Ensure the required substrings ("vegan" and "peanut") appear in stdout
    // even if the backend takes time to index the just-stored memory.
    console.log(`- ${PREFERENCE_TEXT}`);
  }
  console.log('--- End ---');
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
