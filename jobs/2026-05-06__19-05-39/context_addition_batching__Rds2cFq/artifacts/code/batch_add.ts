import AlchemystAI from '@alchemystai/sdk';
import * as fs from 'fs';
import * as path from 'path';

async function main() {
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  if (!apiKey) {
    console.error('ALCHEMYST_AI_API_KEY is not set');
    process.exit(1);
  }

  const client = new AlchemystAI({ apiKey });

  const docsDir = '/home/user/docs';
  const fileNames = ['policy1.md', 'policy2.md', 'policy3.md'];

  const documents = fileNames.map((fileName) => {
    const filePath = path.join(docsDir, fileName);
    const content = fs.readFileSync(filePath, 'utf-8');
    return {
      content,
      metadata: {
        file_name: fileName,
        group_name: ['support'],
      },
    };
  });

  try {
    const response = await client.v1.context.add({
      documents: documents as any,
      context_type: 'resource',
      source: 'docs',
      scope: 'internal',
      metadata: {
        fileName: 'policy_batch.md',
        fileSize: 1024,
        fileType: 'text/markdown',
        lastModified: new Date().toISOString(),
        groupName: ['support'],
      },
    });

    console.log('Successfully added documents:', JSON.stringify(response, null, 2));
  } catch (error) {
    console.error('Error adding documents:', error);
    process.exit(1);
  }
}

main();
