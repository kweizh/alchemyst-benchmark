import AlchemystAI from '@alchemystai/sdk';

async function main(): Promise<void> {
  // Parse --question argument from command line
  const args = process.argv.slice(2);
  let question = '';

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--question' && i + 1 < args.length) {
      question = args[i + 1];
      break;
    }
  }

  if (!question) {
    console.error('Error: --question argument is required.');
    console.error('Usage: npm start -- --question "<your question>"');
    process.exit(1);
  }

  // Initialize Alchemyst client
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  if (!apiKey) {
    console.error('Error: ALCHEMYST_AI_API_KEY environment variable is required.');
    process.exit(1);
  }

  const client = new AlchemystAI({ apiKey });

  // Use ZEALT_RUN_ID to make file_name unique per run, avoiding 409 conflicts
  const runId = process.env.ZEALT_RUN_ID || Date.now().toString();
  const fileName = `refunds-${runId}.md`;

  // Refund policy document content - clearly states 30-day money-back refund policy
  const refundPolicyContent = `# Refund Policy

We offer a 30-day money-back refund policy on all purchases. If you are not satisfied with your purchase, you may request a full refund within 30 days of the original purchase date.

To request a refund, please contact our support team at support@example.com with your order number and reason for the refund.

Refunds will be processed within 5-7 business days and returned to the original payment method.`;

  // Step 1: Ingest the refund-policy document via v1.context.add
  // Note: metadata field uses snake_case (file_name, group_name) in add per SDK quirk
  console.log('Ingesting refund policy document...');
  await client.v1.context.add({
    documents: [
      {
        content: refundPolicyContent,
        file_name: fileName,
        group_name: 'customer-support',
      },
    ],
    context_type: 'resource',
    source: 'documentation',
    scope: 'internal',
    metadata: {
      fileName: fileName,
    },
  });
  console.log('Document ingested successfully.');

  // Step 2: Search the context store via v1.context.search
  // Note: uses scope: 'internal' and similarity_threshold <= 0.7
  console.log(`Searching for: "${question}"`);
  const { contexts } = await client.v1.context.search({
    query: question,
    minimum_similarity_threshold: 0.3,
    similarity_threshold: 0.7,
    scope: 'internal',
  });

  // Step 3: Print retrieved chunk contents to stdout
  if (contexts && contexts.length > 0) {
    console.log(`Found ${contexts.length} relevant chunk(s):`);
    for (const context of contexts) {
      console.log(context.content);
    }
  } else {
    console.log('No relevant chunks found.');
  }
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error('Error:', message);
  process.exit(1);
});