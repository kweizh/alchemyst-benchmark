const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: process.env.ALCHEMYST_AI_API_KEY });
async function run() {
  try {
    const res = await client.v1.context.search({
      query: 'unique memory',
      minimum_similarity_threshold: 0,
      similarity_threshold: 0,
      metadata: 'true'
    });
    console.log(JSON.stringify(res.contexts.slice(0, 3), null, 2));
  } catch(e) {
    console.error(e);
  }
}
run();
