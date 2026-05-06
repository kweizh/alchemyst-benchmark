import AlchemystAI from '@alchemystai/sdk';
import * as fs from 'fs';

const alchemyst = new AlchemystAI({
  apiKey: process.env.ALCHEMYST_AI_API_KEY,
});

async function main() {
  const fileName = `eng-guidelines-${Date.now()}.md`;
  
  // Add document
  await alchemyst.v1.context.add({
    documents: [{
      content: "Engineering department guidelines",
      metadata: {
        file_name: fileName,
        group_name: ["engineering"]
      }
    }],
    context_type: 'resource',
    source: 'docs',
    scope: 'internal'
  } as any);
  
  // Wait a moment for indexing
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Search for context
  const { contexts } = await alchemyst.v1.context.search({
    query: "guidelines",
    similarity_threshold: 0.1,
    scope: 'internal',
    metadata: {
      groupName: ["engineering"]
    } as any
  });

  if (contexts && contexts.length > 0) {
    fs.writeFileSync('/home/user/app/output.txt', contexts[0].content || '');
    console.log("Document found and written to output.txt");
  } else {
    console.log("Document not found");
  }
}

main().catch(console.error);
