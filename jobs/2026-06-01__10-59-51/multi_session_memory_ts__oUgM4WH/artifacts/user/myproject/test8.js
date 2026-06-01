const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
async function run() {
  try {
    const userId = 'user-test8-' + Date.now();
    const sessionId = 'session-test8-' + Date.now();
    
    await client.v1.context.memory.add({
      userId,
      sessionId,
      contents: [{ content: 'This is a unique memory for test8' }]
    });

    const res = await client.post('/api/v1/context/search', {
      body: {
        user_id: userId,
        session_id: sessionId,
        query: 'unique memory',
        minimum_similarity_threshold: 0,
        similarity_threshold: 0
      }
    });
    console.log(res);
  } catch(e) {
    console.error(e);
  }
}
run();
