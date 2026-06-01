import { AlchemystAI } from "@alchemystai/sdk";

const questionFlag = "--question";
const args = process.argv.slice(2);
const questionIndex = args.indexOf(questionFlag);
const question = questionIndex >= 0 ? args[questionIndex + 1] : undefined;

if (!question) {
  console.error("Usage: npm start -- --question \"<question>\"");
  process.exit(1);
}

const apiKey = process.env.ALCHEMYST_AI_API_KEY;
if (!apiKey) {
  console.error("Missing ALCHEMYST_AI_API_KEY environment variable.");
  process.exit(1);
}

const runId = process.env.ZEALT_RUN_ID ?? "local-run";
const fileName = `refunds-${runId}.md`;

const refundPolicy = `# Refund Policy

We offer a 30-day money-back refund policy for all purchases.
If you are not satisfied within 30 days of your purchase date, contact support for a full refund.
`;

const client = new AlchemystAI({ apiKey });

async function run(): Promise<void> {
  await client.v1.context.add({
    context_type: "resource",
    source: "documentation",
    scope: "internal",
    content: refundPolicy,
    metadata: {
      file_name: fileName,
      group_name: "policies"
    }
  });

  const searchResponse = await client.v1.context.search({
    query: question,
    scope: "internal",
    similarity_threshold: 0.7
  });

  const contexts =
    (searchResponse as { contexts?: Array<{ content?: string }> }).contexts ??
    (searchResponse as { data?: Array<{ content?: string }> }).data ??
    [];

  if (contexts.length === 0) {
    console.log("No relevant context found.");
    return;
  }

  for (const context of contexts) {
    if (context.content) {
      console.log(context.content);
    }
  }
}

run().catch((error) => {
  console.error("RAG flow failed:", error);
  process.exit(1);
});
