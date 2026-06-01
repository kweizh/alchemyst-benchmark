const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
async function run() {
  try {
    const res = await client.v1.context.search({
      userId: 'test-user',
      sessionId: 'test-session-2',
      query: 'test',
      minimum_similarity_threshold: 0,
      similarity_threshold: 0
    });
    console.log(res);
  } catch(e) {
    console.error(e);
  }
}
run();
