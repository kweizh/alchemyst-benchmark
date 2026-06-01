import AlchemystAI from '@alchemystai/sdk';

// Type definitions for monkey-patched search
interface MemorySearchParams {
  userId: string;
  user_id?: string;
  sessionId: string;
  session_id?: string;
  query?: string;
  similarityThreshold?: number;
  minimumSimilarityThreshold?: number;
  scope?: 'internal' | 'external';
}

async function main() {
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  if (!apiKey) {
    console.error('Error: ALCHEMYST_AI_API_KEY environment variable is not set.');
    process.exit(1);
  }

  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) {
    console.error('Error: ZEALT_RUN_ID environment variable is not set.');
    process.exit(1);
  }

  // Parse --query argument
  let queryText = '';
  const args = process.argv;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--query' && i + 1 < args.length) {
      queryText = args[i + 1];
      break;
    }
  }

  if (!queryText) {
    console.error('Error: --query argument is required.');
    process.exit(1);
  }

  // Construct AlchemystAI client
  const client = new AlchemystAI({ apiKey });

  // Monkey-patch client.v1.context.memory.search as it is not present in the SDK but required by the API and prompt
  (client.v1.context.memory as any).search = async function (
    body: MemorySearchParams,
    options?: any
  ) {
    const searchParams = {
      user_id: body.userId || body.user_id,
      session_id: body.sessionId || body.session_id,
      query: body.query || '',
      similarity_threshold: body.similarityThreshold || body.minimumSimilarityThreshold || 0.1,
      minimum_similarity_threshold: body.minimumSimilarityThreshold || 0.1,
      scope: body.scope || 'internal',
    };
    
    // Call the unified search endpoint
    const res = await this._client.post('/api/v1/context/search', { body: searchParams, ...options });
    
    // Map contexts to memories array to support memories[i].content iteration
    const memories = (res.contexts || []).map((ctx: any) => ({
      content: ctx.content,
    }));

    return {
      ...res,
      memories,
    };
  };

  const userId = `user-${runId}`;
  const sessionA = `session_A-${runId}`;
  const sessionB = `session_B-${runId}`;

  // 1. Idempotent Store: Check if memory under sessionA is already present
  try {
    const checkA = await (client.v1.context.memory as any).search({
      userId,
      sessionId: sessionA,
      query: 'vegan peanut',
      minimumSimilarityThreshold: 0.1,
    });

    const hasPreference = checkA.memories && checkA.memories.some((m: any) => {
      const contentLower = (m.content || '').toLowerCase();
      return contentLower.includes('vegan') && contentLower.includes('peanut');
    });

    if (!hasPreference) {
      // Memory is empty or preference not found under session_A, so store it
      await client.v1.context.memory.add({
        userId,
        user_id: userId,
        sessionId: sessionA,
        session_id: sessionA,
        contents: [
          { content: 'User is vegan and allergic to peanuts' }
        ]
      } as any);
    }
  } catch (err) {
    console.error('Error checking/storing memory under session_A:', err);
    process.exit(1);
  }

  // 2. Retrieve and Recall: Search memory under sessionB
  try {
    const searchRes = await (client.v1.context.memory as any).search({
      userId,
      sessionId: sessionB,
      query: queryText,
      minimumSimilarityThreshold: 0.1,
    });

    if (searchRes.memories && searchRes.memories.length > 0) {
      for (const mem of searchRes.memories) {
        if (mem.content) {
          console.log(mem.content);
        }
      }
    } else {
      console.log('No memories recalled.');
    }
  } catch (err) {
    console.error('Error searching memory under session_B:', err);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Unexpected error:', err);
  process.exit(1);
});
