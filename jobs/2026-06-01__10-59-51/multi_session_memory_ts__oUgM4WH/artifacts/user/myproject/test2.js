const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
async function run() {
  try {
    const res = await client.post('/api/v1/context/memory/search', {
      body: {
        userId: 'test-user',
        sessionId: 'test-session-2',
        query: 'test memory'
      }
    });
    console.log(res);
  } catch(e) {
    console.error(e);
  }
}
run();
