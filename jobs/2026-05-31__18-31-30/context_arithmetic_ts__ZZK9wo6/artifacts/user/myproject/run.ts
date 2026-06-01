import AlchemystAI from '@alchemystai/sdk';
import * as fs from 'fs';

async function run() {
  const runId = process.env.ZEALT_RUN_ID;
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;

  if (!runId || !apiKey) {
    console.error('Missing environment variables ZEALT_RUN_ID or ALCHEMYST_AI_API_KEY');
    process.exit(1);
  }

  const client = new AlchemystAI({
    apiKey: apiKey,
  });

  // Document 1
  await client.v1.context.add({
    context_type: 'resource',
    source: 'docs',
    scope: 'internal',
    documents: [{ content: 'The v1 engine uses a monolithic architecture.' }],
    metadata: {
      fileName: `doc1-${runId}.txt`,
      groupName: ['eng', 'v1'],
      fileSize: 0,
      fileType: 'text/plain',
      lastModified: new Date().toISOString(),
    },
  });

  // Document 2
  await client.v1.context.add({
    context_type: 'resource',
    source: 'docs',
    scope: 'internal',
    documents: [{ content: 'The v2 engine uses a microservices architecture.' }],
    metadata: {
      fileName: `doc2-${runId}.txt`,
      groupName: ['eng', 'v2'],
      fileSize: 0,
      fileType: 'text/plain',
      lastModified: new Date().toISOString(),
    },
  });

  // Perform search with Context Arithmetic filter
  // Requirement: both 'eng' and 'v2' groups.
  // Based on "Context Arithmetic", the '+' operator is used for AND logic.
  // We use the snake_case 'group_name' as suggested by the hint for search.
  const searchResponse = await client.v1.context.search({
    query: 'What architecture is used?',
    minimum_similarity_threshold: 0,
    similarity_threshold: 0,
    body_metadata: {
      groupName: 'eng+v2',
    },
    scope: 'internal',
  });

  const contexts = searchResponse.contexts || [];
  if (contexts.length > 0) {
    const topResult = contexts[0].content;
    fs.writeFileSync('/home/user/myproject/output.log', `Result: ${topResult}`);
    console.log('Successfully wrote result to output.log');
    console.log('Result content:', topResult);
  } else {
    console.log('No results with group_name: eng+v2, trying groupName: eng+v2');
    // Fallback or alternative attempt
    try {
      const searchResponse2 = await client.v1.context.search({
        query: 'What architecture is used?',
        minimum_similarity_threshold: 0.1,
        similarity_threshold: 0.1,
        body_metadata: {
          groupName: 'eng+v2',
        },
        scope: 'internal',
      });
      const contexts2 = searchResponse2.contexts || [];
      if (contexts2.length > 0) {
        const topResult = contexts2[0].content;
        fs.writeFileSync('/home/user/myproject/output.log', `Result: ${topResult}`);
        console.log('Successfully wrote result to output.log (using groupName)');
        console.log('Result content:', topResult);
      }
    } catch (e) {
      console.log('Error with groupName fallback');
    }
  }
}

run().catch((err) => {
  console.error('Error occurred:', err);
  process.exit(1);
});
