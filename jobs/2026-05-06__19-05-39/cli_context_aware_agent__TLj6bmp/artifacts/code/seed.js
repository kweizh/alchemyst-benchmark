const AlchemystAI = require('@alchemystai/sdk');

async function main() {
  const client = new AlchemystAI({
    apiKey: process.env.ALCHEMYST_AI_API_KEY,
  });

  try {
    await client.v1.context.add({
      context_type: 'resource',
      documents: [{ content: "The secret launch code for Project Nova is 8847-ALPHA." }],
      source: 'docs',
      scope: 'internal',
      metadata: {
        fileName: "nova_secret.txt",
        groupName: ["eng"]
      },
    });
    console.log("Document added successfully.");
  } catch (error) {
    // Handle 409 Conflict gracefully
    if (error.status === 409 || error.name === 'ConflictError') {
      console.log("Document already exists (409 Conflict). Catching error gracefully.");
    } else {
      console.error("Error adding document:", error);
      process.exit(1);
    }
  }
}

main();
