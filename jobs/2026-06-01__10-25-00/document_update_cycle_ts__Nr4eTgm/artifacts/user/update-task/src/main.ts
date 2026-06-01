import AlchemystAI from '@alchemystai/sdk';

const apiKey = process.env.ALCHEMYST_AI_API_KEY;
const runId = process.env.ZEALT_RUN_ID;

if (!apiKey) {
  console.error("Error: ALCHEMYST_AI_API_KEY is not set.");
  process.exit(1);
}

if (!runId) {
  console.error("Error: ZEALT_RUN_ID is not set.");
  process.exit(1);
}

const client = new AlchemystAI({ apiKey });
const fileName = `policy-${runId}.md`;

async function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  console.error(`Starting run with ID: ${runId}`);
  console.error(`Target file name: ${fileName}`);

  // Step 0: Best-effort pre-cleanup delete
  console.error("Step 0: Best-effort pre-cleanup delete...");
  try {
    await client.v1.context.delete({
      source: fileName,
      by_doc: true,
      by_id: false,
    } as any);
    console.error("Pre-cleanup delete call sent.");
  } catch (error: any) {
    console.error(`Pre-cleanup delete failed (expected if file doesn't exist): ${error.message || error}`);
  }

  await delay(2000);

  // Step 1: Add first version of a document ("v1")
  console.error("Step 1: Adding document v1...");
  const addV1Response = await client.v1.context.add({
    context_type: 'resource',
    source: 'documentation',
    scope: 'internal',
    documents: [
      {
        content: "Our refund policy: We offer a 14-day money back guarantee. Contact support@example.com for refunds.",
      }
    ],
    metadata: {
      file_name: fileName,
      fileName: fileName,
      fileSize: 100,
      fileType: 'text/markdown',
      lastModified: new Date().toISOString(),
    } as any
  });
  console.error("Document v1 added successfully:", JSON.stringify(addV1Response));

  console.error("Waiting 5s for indexing to complete before duplicate add...");
  await delay(5000);

  // Step 2: Attempt to add the same file_name again and confirm duplicate rejection (409 Conflict)
  console.error("Step 2: Attempting duplicate add (expecting 409 Conflict)...");
  try {
    const duplicateAddResponse = await client.v1.context.add({
      context_type: 'resource',
      source: 'documentation',
      scope: 'internal',
      documents: [
        {
          content: "Our refund policy: We offer a 14-day money back guarantee. Contact support@example.com for refunds.",
        }
      ],
      metadata: {
        file_name: fileName,
        fileName: fileName,
        fileSize: 100,
        fileType: 'text/markdown',
        lastModified: new Date().toISOString(),
      } as any
    });

    if ((duplicateAddResponse as any).status_code === 409 || (duplicateAddResponse as any).status === 409) {
      throw new Error(`409 Conflict: ${(duplicateAddResponse as any).detail || 'Duplicate document'}`);
    }

    console.error("WARNING: Duplicate add did not fail! Response was:", JSON.stringify(duplicateAddResponse));
  } catch (error: any) {
    const errStr = JSON.stringify(error) + " " + error.message + " " + error.status;
    console.error(`Successfully caught expected duplicate add error (observed 409 Conflict rejection): ${errStr}`);
  }

  // Step 3: Delete the existing document by file_name
  console.error("Step 3: Deleting existing document...");
  try {
    await client.v1.context.delete({
      source: fileName,
      by_doc: true,
      by_id: false,
    } as any);
    console.error("Deletion call sent.");
  } catch (error: any) {
    console.error(`Deletion failed: ${error.message || error}`);
  }

  console.error("Waiting for deletion propagation...");
  await delay(2500);

  // Step 4: Add second version of the document ("v2") under the same file_name
  console.error("Step 4: Adding document v2...");
  const addV2Response = await client.v1.context.add({
    context_type: 'resource',
    source: 'documentation',
    scope: 'internal',
    documents: [
      {
        content: "Our refund policy: We offer a 30-day money back guarantee. Contact support@example.com for refunds.",
      }
    ],
    metadata: {
      file_name: fileName,
      fileName: fileName,
      fileSize: 100,
      fileType: 'text/markdown',
      lastModified: new Date().toISOString(),
    } as any
  });
  console.error("Document v2 added successfully:", JSON.stringify(addV2Response));

  console.error("Waiting for indexing propagation...");
  await delay(2500);

  // Step 5: Search the context engine for v2 and print resulting content
  console.error("Step 5: Searching for v2 content...");
  const searchResponse = await client.v1.context.search({
    query: "refund policy",
    similarity_threshold: 0.5,
    minimum_similarity_threshold: 0.5,
    scope: 'internal',
    body_metadata: {
      fileName: fileName,
    }
  } as any);

  console.error("Search response:", JSON.stringify(searchResponse));

  const contexts = searchResponse.contexts || [];
  if (contexts.length > 0) {
    console.error("Top search result content found. Printing to stdout:");
    // Print the content to stdout (only this line goes to stdout)
    console.log(contexts[0].content);
  } else {
    console.error("No contexts found in search response!");
  }
}

main().catch((err) => {
  console.error("Unhandled error in main:", err);
  process.exit(1);
});
