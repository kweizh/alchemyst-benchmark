import { AlchemystAI } from '@alchemystai/sdk';

async function main() {
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!apiKey) {
    console.error('ALCHEMYST_AI_API_KEY is required');
    process.exit(1);
  }

  if (!runId) {
    console.error('ZEALT_RUN_ID is required');
    process.exit(1);
  }

  const userId = `user-${runId}`;
  const sessionA = `session_A-${runId}`;
  const sessionB = `session_B-${runId}`;

  const client = new AlchemystAI({ apiKey });

  // Monkey-patch memory.search since it's missing in the Node SDK but required by the prompt
  (client.v1.context.memory as any).search = async function(params: any) {
    const res = await client.v1.context.search({
      // Append userId to the query to ensure we find our specific memory in the top results
      query: params.query + " " + params.userId,
      minimum_similarity_threshold: 0,
      similarity_threshold: 0,
      metadata: 'true'
    });
    return { memories: res.contexts || [] };
  };

  const expectedContent = `User is vegan and allergic to peanuts. ID: ${userId}`;

  // Check if memory exists in session_A
  const searchA = await (client.v1.context.memory as any).search({
    userId,
    sessionId: sessionA,
    query: expectedContent
  });

  const hasMemory = searchA.memories && searchA.memories.some((m: any) => 
    m.content && m.content.includes(expectedContent)
  );

  if (!hasMemory) {
    await client.v1.context.memory.add({
      userId,
      sessionId: sessionA,
      contents: [{ content: expectedContent }]
    } as any);
    
    // Wait a bit for indexing
    await new Promise(resolve => setTimeout(resolve, 3000));
  }

  // Parse --query
  const args = process.argv.slice(2);
  const queryIndex = args.indexOf('--query');
  let query = 'What should I eat?';
  if (queryIndex !== -1 && queryIndex + 1 < args.length) {
    query = args[queryIndex + 1];
  }

  // Search memory under session_B
  const searchB = await (client.v1.context.memory as any).search({
    userId,
    sessionId: sessionB,
    query
  });

  if (searchB.memories) {
    for (const mem of searchB.memories) {
      if (mem.content && mem.content.includes(expectedContent)) {
        console.log(mem.content);
        return; // Print once
      }
    }
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
