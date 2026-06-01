import AlchemystAI from '@alchemystai/sdk';

function parseArgs(argv: string[]): { question: string } {
  let question = '';
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--question') {
      question = argv[i + 1] ?? '';
      i++;
    } else if (arg.startsWith('--question=')) {
      question = arg.slice('--question='.length);
    }
  }
  return { question };
}

async function main() {
  const { question } = parseArgs(process.argv.slice(2));
  if (!question) {
    console.error('Usage: npm start -- --question "<question>"');
    process.exit(1);
  }

  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  if (!apiKey) {
    console.error('Missing ALCHEMYST_AI_API_KEY environment variable.');
    process.exit(1);
  }

  const runId = process.env.ZEALT_RUN_ID || `${Date.now()}`;
  const fileName = `refunds-${runId}.md`;

  const client = new AlchemystAI({ apiKey });

  const refundPolicyContent = `# Refund Policy

Our company offers a 30-day money-back refund policy on all purchases.
If you are not satisfied with your purchase for any reason, you may request a full refund within 30 days of the purchase date.

To request a refund, contact support@example.com with your order number. Refunds are processed within 5-7 business days.
`;

  // Ingest the refund policy document. The file_name is unique per run via
  // ZEALT_RUN_ID so repeated invocations don't 409 Conflict.
  const addBody: any = {
    context_type: 'resource',
    source: 'documentation',
    scope: 'internal',
    documents: [
      {
        content: refundPolicyContent,
      },
    ],
    metadata: {
      fileName: fileName,
      file_name: fileName,
      fileSize: refundPolicyContent.length,
      fileType: 'text/markdown',
      lastModified: new Date().toISOString(),
      groupName: ['customer-support', 'policies'],
      group_name: ['customer-support', 'policies'],
    },
  };

  await client.v1.context.add(addBody);
  console.log(`Ingested document: ${fileName}`);

  // Search the context store for the user's question.
  const searchBody: any = {
    query: question,
    scope: 'internal',
    similarity_threshold: 0.7,
    minimum_similarity_threshold: 0.5,
  };

  const searchResult: any = await client.v1.context.search(searchBody);
  const contexts: any[] = searchResult?.contexts ?? [];
  console.log(`Found ${contexts.length} relevant chunks`);
  for (const ctx of contexts) {
    console.log('--- CHUNK ---');
    console.log(ctx?.content ?? '');
  }
}

main().catch((err) => {
  console.error('Error:', err);
  process.exit(1);
});
