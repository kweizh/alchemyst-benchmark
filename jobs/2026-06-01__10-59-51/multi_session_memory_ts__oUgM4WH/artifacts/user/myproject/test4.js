const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
async function run() {
  try {
    const res = await client.get('/api/v1/context/memory/search', {
      query: {
        userId: 'test-user',
        sessionId: 'test-session-2',
        query: 'test'
      }
    });
    console.log(res);
  } catch(e) {
    console.error(e);
  }
}
run();
