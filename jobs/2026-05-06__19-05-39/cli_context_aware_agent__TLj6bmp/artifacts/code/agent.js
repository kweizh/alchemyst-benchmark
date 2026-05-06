const AlchemystAI = require('@alchemystai/sdk');
const OpenAI = require('openai');

async function main() {
  const query = process.argv[2];
  if (!query) {
    process.exit(1);
  }

  const alchemyst = new AlchemystAI({
    apiKey: process.env.ALCHEMYST_AI_API_KEY,
  });

  const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });

  try {
    const searchResponse = await alchemyst.v1.context.search({
      query: query,
      similarity_threshold: 0.7,
      minimum_similarity_threshold: 0.7,
      scope: 'internal',
      body_metadata: {
        groupName: ['eng']
      }
    });

    let prompt = query;
    if (searchResponse.contexts && searchResponse.contexts.length > 0) {
      const joinedContexts = searchResponse.contexts
        .map(c => c.content)
        .filter(content => !!content)
        .join('\n');
      
      if (joinedContexts) {
        prompt = `Context:\n${joinedContexts}\n\nQuestion: ${query}`;
      }
    }

    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
    });

    process.stdout.write(completion.choices[0].message.content);
  } catch (error) {
    console.error("Error:", error);
    process.exit(1);
  }
}

main();
