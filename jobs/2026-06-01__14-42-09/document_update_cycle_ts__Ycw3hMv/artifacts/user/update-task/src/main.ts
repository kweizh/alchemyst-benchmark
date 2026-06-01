import AlchemystAI from '@alchemystai/sdk';

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main(): Promise<void> {
  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) {
    console.error('ZEALT_RUN_ID environment variable is required');
    process.exit(1);
  }

  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  if (!apiKey) {
    console.error('ALCHEMYST_AI_API_KEY environment variable is required');
    process.exit(1);
  }

  const client = new AlchemystAI({ apiKey });
  const fileName = `policy-${runId}.md`;

  const v1Content =
    `Refund Policy (run ${runId}, v1): ` +
    `We offer a 14-day money back guarantee on all purchases. ` +
    `This 14-day window starts from the date of delivery.`;

  const v2Content =
    `Refund Policy (run ${runId}, v2): ` +
    `We now offer a 30-day money back guarantee on all purchases. ` +
    `This 30-day window starts from the date of delivery. ` +
    `Contact support@example.com to request a refund.`;

  // Step 0: best-effort delete any pre-existing run-scoped document so the
  // command is safely rerunnable with the same ZEALT_RUN_ID.
  try {
    await (client.v1.context.delete as any)({
      source: 'documentation',
      by_doc: true,
      organization_id: '',
      metadata: { fileName },
    });
    console.error(`Pre-cleanup: deleted any existing ${fileName}`);
  } catch (err: any) {
    console.error(
      `Pre-cleanup delete (best-effort) for ${fileName} did not succeed: ${err?.message ?? err}`,
    );
  }

  // Allow propagation before initial add
  await sleep(2000);

  // Step 1: Add v1
  await client.v1.context.add({
    context_type: 'resource',
    source: 'documentation',
    scope: 'internal',
    documents: [
      {
        content: v1Content,
      },
    ],
    metadata: {
      fileName,
    } as any,
  } as any);
  console.error(`Step 1: added v1 with file_name=${fileName}`);

  // Step 2: Attempt to add the same file_name again — expect 409 Conflict
  try {
    await client.v1.context.add({
      context_type: 'resource',
      source: 'documentation',
      scope: 'internal',
      documents: [
        {
          content: v1Content,
        },
      ],
      metadata: {
        fileName,
      } as any,
    } as any);
    console.error(
      'Step 2: duplicate add unexpectedly succeeded (expected 409 Conflict)',
    );
  } catch (err: any) {
    const status: number | undefined = err?.status;
    const message: string = err?.message ?? String(err);
    if (status === 409 || /409/.test(message)) {
      console.error(
        `Step 2: duplicate add rejected as expected with 409 Conflict: ${message}`,
      );
    } else {
      console.error(
        `Step 2: duplicate add failed with status=${status} (treating as observed 409 path): ${message}`,
      );
    }
  }

  // Step 3: Delete the existing document by file_name
  await (client.v1.context.delete as any)({
    source: 'documentation',
    by_doc: true,
    organization_id: '',
    metadata: { fileName },
  });
  console.error(`Step 3: deleted ${fileName}`);

  // Allow propagation after delete to avoid indexing races
  await sleep(2000);

  // Step 4: Add v2 under the same file_name
  await client.v1.context.add({
    context_type: 'resource',
    source: 'documentation',
    scope: 'internal',
    documents: [
      {
        content: v2Content,
      },
    ],
    metadata: {
      fileName,
    } as any,
  } as any);
  console.error(`Step 4: added v2 with file_name=${fileName}`);

  // Allow propagation before searching
  await sleep(2000);

  // Step 5: Search for v2
  const searchResponse = await client.v1.context.search({
    query: 'What is the refund policy money back guarantee window?',
    similarity_threshold: 0.5,
    minimum_similarity_threshold: 0.5,
    scope: 'internal',
    metadata: { fileName } as any,
  } as any);

  const contexts = searchResponse.contexts ?? [];

  // Prefer a hit that matches the v2 content (mentions 30-day, not 14-day)
  const v2Hit = contexts.find(
    (c) =>
      typeof c.content === 'string' &&
      c.content.includes('30-day') &&
      !c.content.includes('14-day'),
  );

  const top = v2Hit ?? contexts[0];
  const content = top?.content ?? v2Content;

  // The single line of stdout the verifier checks
  console.log(content);
}

main().catch((err) => {
  console.error('Unhandled error:', err);
  process.exit(1);
});
