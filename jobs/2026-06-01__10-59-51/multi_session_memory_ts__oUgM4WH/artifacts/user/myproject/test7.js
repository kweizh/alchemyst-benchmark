const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
async function run() {
  try {
    const userId = 'user-test7-' + Date.now();
    const sessionId = 'session-test7-' + Date.now();
    
    await client.v1.context.memory.add({
      userId,
      sessionId,
      contents: [{ content: 'This is a unique memory for test7' }]
    });

    const res = await client.v1.context.search({
      userId,
      sessionId,
      query: 'unique memory',
      minimum_similarity_threshold: 0,
      similarity_threshold: 0
    });
    console.log(res);
  } catch(e) {
    console.error(e);
  }
}
run();
