const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
async function run() {
  try {
    const userId = 'user-test9-' + Date.now();
    const sessionId = 'session-test9-' + Date.now();
    
    await client.v1.context.memory.add({
      userId,
      sessionId,
      contents: [{ content: 'This is a unique memory for test9' }]
    });

    const res = await client.v1.context.search({
      query: 'unique memory',
      minimum_similarity_threshold: 0,
      similarity_threshold: 0,
      body_metadata: {
        userId,
        sessionId
      }
    });
    console.log(res);
  } catch(e) {
    console.error(e);
  }
}
run();
