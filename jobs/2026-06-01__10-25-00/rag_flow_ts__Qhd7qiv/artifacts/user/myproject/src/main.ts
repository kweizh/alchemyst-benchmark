import AlchemystAI from '@alchemystai/sdk';

async function main() {
  // 1. Parse CLI arguments
  const args = process.argv.slice(2);
  let question = '';
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--question' && i + 1 < args.length) {
      question = args[i + 1];
      break;
    } else if (args[i].startsWith('--question=')) {
      question = args[i].substring('--question='.length);
      break;
    }
  }

  if (!question) {
    console.error('Error: Please provide a question using --question "<question>"');
    process.exit(1);
  }

  // 2. Get API key and Run ID
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  if (!apiKey) {
    console.error('Error: ALCHEMYST_AI_API_KEY environment variable is not set');
    process.exit(1);
  }

  const runId = process.env.ZEALT_RUN_ID || 'default-run-id';
  const fileName = `refunds-${runId}.md`;

  // 3. Initialize Alchemyst AI client
  const client = new AlchemystAI({
    apiKey: apiKey,
  });

  // 4. Ingest the refund policy document
  const refundPolicyContent = `Refund Policy:
We offer a 30-day money-back guarantee for all purchases.
If you are not completely satisfied with our service, you can request a full refund within 30 days of your purchase date.
To request a refund, please contact our support team.`;

  console.log(`Ingesting refund policy document with file_name: ${fileName}...`);
  try {
    await client.v1.context.add({
      documents: [
        {
          content: refundPolicyContent,
          file_name: fileName,
          fileName: fileName,
        },
      ],
      context_type: 'resource',
      source: 'documentation',
      scope: 'internal',
      metadata: {
        fileName: fileName,
        file_name: fileName,
        fileSize: Buffer.byteLength(refundPolicyContent),
        fileType: 'text/markdown',
        lastModified: new Date().toISOString(),
      } as any,
    });
    console.log('✅ Document stored successfully.');
  } catch (error) {
    console.error('Error storing document:', error);
    process.exit(1);
  }

  // 5. Search for the user question
  console.log(`Searching context store for: "${question}"...`);
  try {
    const response = await client.v1.context.search({
      query: question,
      similarity_threshold: 0.7,
      minimum_similarity_threshold: 0.5,
      scope: 'internal',
    });

    const contexts = response.contexts || [];
    console.log(`Found ${contexts.length} relevant chunks:`);

    for (const ctx of contexts) {
      console.log(ctx.content);
    }
  } catch (error) {
    console.error('Search failed:', error);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('An unexpected error occurred:', err);
  process.exit(1);
});
