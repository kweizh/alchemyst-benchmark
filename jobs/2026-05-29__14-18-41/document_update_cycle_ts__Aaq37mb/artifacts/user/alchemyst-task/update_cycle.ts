import AlchemystAI from '@alchemystai/sdk';
import * as fs from 'fs';
import * as path from 'path';

async function main() {
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!apiKey || !runId) {
    console.error('Missing environment variables ALCHEMYST_AI_API_KEY or ZEALT_RUN_ID');
    process.exit(1);
  }

  const client = new AlchemystAI({
    apiKey: apiKey,
  });

  const fileName = `policy-${runId}.md`;
  const groupName = [`update-test-${runId}`];
  const logFilePath = '/home/user/alchemyst-task/output.log';

  try {
    // Step 1: Add initial document
    console.log(`Step 1: Adding initial document ${fileName}...`);
    const initialContent = 'Old refund policy: 30-day refunds.';
    await client.v1.context.add({
      context_type: 'resource',
      documents: [{ content: initialContent }],
      scope: 'internal',
      source: fileName,
      metadata: {
        fileName: fileName,
        groupName: groupName,
        fileSize: initialContent.length,
        fileType: 'text/markdown',
        lastModified: new Date().toISOString(),
      },
    });

    // Step 2: Update document (Delete then Add)
    console.log(`Step 2: Deleting existing document ${fileName}...`);
    // organization_id is required by the SDK's delete method.
    // We use a placeholder as it's not provided in the environment.
    await client.v1.context.delete({
      organization_id: 'org_01HXYZABC',
      source: fileName,
      by_doc: true,
    });

    console.log(`Step 2: Adding updated document ${fileName}...`);
    const updatedContent = 'Updated refund policy: 60-day refunds.';
    await client.v1.context.add({
      context_type: 'resource',
      documents: [{ content: updatedContent }],
      scope: 'internal',
      source: fileName,
      metadata: {
        fileName: fileName,
        groupName: groupName,
        fileSize: updatedContent.length,
        fileType: 'text/markdown',
        lastModified: new Date().toISOString(),
      },
    });

    // Step 3: Log success message
    const successMessage = `Update cycle successful: ${fileName}`;
    fs.mkdirSync(path.dirname(logFilePath), { recursive: true });
    fs.writeFileSync(logFilePath, successMessage);
    console.log(successMessage);

  } catch (error: any) {
    console.error('Error during document update cycle:', error);
    // Note: If the API returns 402 Payment Required, it indicates an issue with the account credits.
    process.exit(1);
  }
}

main().catch(console.error);
