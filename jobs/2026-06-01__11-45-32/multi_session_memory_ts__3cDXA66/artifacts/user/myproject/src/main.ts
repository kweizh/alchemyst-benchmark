import AlchemystAI from "@alchemystai/sdk";

const preferenceText = "User is vegan and allergic to peanuts.";

const getArgValue = (flag: string): string | undefined => {
  const index = process.argv.indexOf(flag);
  if (index === -1 || index + 1 >= process.argv.length) {
    return undefined;
  }
  return process.argv[index + 1];
};

const run = async (): Promise<void> => {
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  if (!apiKey) {
    throw new Error("Missing ALCHEMYST_AI_API_KEY environment variable.");
  }

  const runId = process.env.ZEALT_RUN_ID;
  if (!runId) {
    throw new Error("Missing ZEALT_RUN_ID environment variable.");
  }

  const query = getArgValue("--query");
  if (!query) {
    throw new Error("Missing required --query argument.");
  }

  const userId = `user-${runId}`;
  const sessionA = `session_A-${runId}`;
  const sessionB = `session_B-${runId}`;

  const client = new AlchemystAI({ apiKey });

  const existing = await client.v1.context.memory.search({
    userId,
    sessionId: sessionA,
    query: "dietary preference"
  });

  if (!existing.memories || existing.memories.length === 0) {
    await client.v1.context.memory.add({
      userId,
      sessionId: sessionA,
      content: preferenceText
    });
  }

  const recall = await client.v1.context.memory.search({
    userId,
    sessionId: sessionB,
    query
  });

  const recalledContents = (recall.memories || []).map((memory) => memory.content).filter(Boolean);

  if (recalledContents.length === 0) {
    console.log("No memories found.");
    return;
  }

  console.log(recalledContents.join("\n"));
};

run().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
