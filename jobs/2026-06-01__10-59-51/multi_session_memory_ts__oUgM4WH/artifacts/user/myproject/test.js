const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
async function run() {
  try {
    const res = await client.v1.context.memory.add({
      userId: 'test-user',
      sessionId: 'test-session',
      contents: [{ content: 'test memory' }]
    });
    console.log(res);
  } catch(e) {
    console.error(e);
  }
}
run();
