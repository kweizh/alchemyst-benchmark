import AlchemystAI from '@alchemystai/sdk';

async function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const runId = process.env.ZEALT_RUN_ID;
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;

  if (!runId) {
    console.error("Missing ZEALT_RUN_ID");
    process.exit(1);
  }
  if (!apiKey) {
    console.error("Missing ALCHEMYST_AI_API_KEY");
    process.exit(1);
  }

  const client = new AlchemystAI({ apiKey });
  const fileName = `policy-${runId}.md`;

  // Best-effort delete any pre-existing document
  try {
    await (client.v1.context.delete as any)({
      metadata: { file_name: fileName }
    });
    await sleep(2000);
  } catch (err) {
    // Ignore error on initial best-effort delete
  }

  // 1. Add a first version of a document ("v1")
  const v1Content = "This is the 14-day return policy.";
  await (client.v1.context.add as any)({
    context_type: 'resource',
    source: 'documentation',
    scope: 'internal',
    metadata: { file_name: fileName },
    documents: [{ content: v1Content }]
  });
  
  await sleep(2000);

  // 2. Attempt to add the same file_name again and confirm 409 Conflict
  try {
    await (client.v1.context.add as any)({
      context_type: 'resource',
      source: 'documentation',
      scope: 'internal',
      metadata: { file_name: fileName },
      documents: [{ content: v1Content }]
    });
  } catch (err: any) {
    console.error(`Expected error caught (409 Conflict): ${err.message || err}`);
  }

  // 3. Delete the existing document by file_name
  await (client.v1.context.delete as any)({
    metadata: { file_name: fileName }
  });

  await sleep(2000);

  // 4. Add a second version of the document ("v2")
  const v2Content = "This is the updated 30-day return policy.";
  await (client.v1.context.add as any)({
    context_type: 'resource',
    source: 'documentation',
    scope: 'internal',
    metadata: { file_name: fileName },
    documents: [{ content: v2Content }]
  });

  await sleep(2000);

  // 5. Search the context engine for v2
  const searchRes = await (client.v1.context.search as any)({
    query: "return policy",
    similarity_threshold: 0.5,
    scope: 'internal',
    metadata: { fileName: fileName }
  });

  if (searchRes.contexts && searchRes.contexts.length > 0) {
    // Print only one line to stdout at the very end
    console.log(searchRes.contexts[0].content);
  } else {
    console.error("No contexts found in search.");
    process.exit(1);
  }
}

main().catch(err => {
  console.error("Fatal error:", err);
  process.exit(1);
});
