import { AlchemystAI } from "@alchemystai/sdk";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const run = async () => {
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!apiKey) {
    throw new Error("Missing ALCHEMYST_AI_API_KEY environment variable.");
  }
  if (!runId) {
    throw new Error("Missing ZEALT_RUN_ID environment variable.");
  }

  const client = new AlchemystAI({ apiKey });
  const fileName = `policy-${runId}.md`;

  const v1Content = "Policy update: customers have a 14-day refund window.";
  const v2Content = "Policy update: customers have a 30-day refund window.";

  // Best-effort cleanup for reruns.
  try {
    await client.v1.context.delete({
      source: "documentation",
      by_doc: true,
      metadata: {
        file_name: fileName
      }
    } as any);
  } catch (error) {
    console.warn("Pre-run delete skipped:", error instanceof Error ? error.message : error);
  }

  await client.v1.context.add({
    context_type: "resource",
    source: "documentation",
    scope: "internal",
    documents: [{ content: v1Content }],
    metadata: {
      file_name: fileName
    }
  } as any);

  try {
    await client.v1.context.add({
      context_type: "resource",
      source: "documentation",
      scope: "internal",
      documents: [{ content: v1Content }],
      metadata: {
        file_name: fileName
      }
    } as any);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.warn(`Duplicate add rejected (expected 409): ${message}`);
  }

  await client.v1.context.delete({
    source: "documentation",
    by_doc: true,
    metadata: {
      file_name: fileName
    }
  } as any);

  await sleep(2000);

  await client.v1.context.add({
    context_type: "resource",
    source: "documentation",
    scope: "internal",
    documents: [{ content: v2Content }],
    metadata: {
      file_name: fileName
    }
  } as any);

  await sleep(2000);

  const searchResponse = await client.v1.context.search({
    query: "refund window",
    minimum_similarity_threshold: 0.5,
    similarity_threshold: 0.5,
    scope: "internal",
    body_metadata: {
      fileName
    }
  });

  const topResult = searchResponse?.contexts?.[0];
  if (!topResult?.content) {
    throw new Error("No search results returned for v2 content.");
  }

  process.stdout.write(`${topResult.content}\n`);
};

run().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
