import { AlchemystAI } from '@alchemystai/sdk';
import * as fs from 'fs';
import * as path from 'path';

const runId = process.env.ZEALT_RUN_ID || '';
const apiKey = process.env.ALCHEMYST_API_KEY || 'dummy';

const client = new AlchemystAI({
  apiKey: apiKey,
});

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'add') {
    const filePath = args[1];
    if (!filePath) {
      console.error('Usage: npx tsx rag.ts add <file_path>');
      process.exit(1);
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    const fileName = path.basename(filePath);
    const fileNameWithRunId = `${fileName}-${runId}`;

    await client.v1.context.add({
      context_type: 'resource',
      source: 'documentation',
      scope: 'internal',
      documents: [{ content }],
      metadata: {
        file_name: fileNameWithRunId,
      } as any,
    });
  } else if (command === 'search') {
    const query = args[1];
    const fileNameArg = args[2];
    if (!query || !fileNameArg) {
      console.error('Usage: npx tsx rag.ts search "<query>" <file_name>');
      process.exit(1);
    }

    const fileNameWithRunId = `${fileNameArg}-${runId}`;

    const response = await client.v1.context.search({
      query: query,
      minimum_similarity_threshold: 0,
      similarity_threshold: 0,
      body_metadata: {
        fileName: fileNameWithRunId,
      },
    } as any);

    if (response.contexts && response.contexts.length > 0) {
      console.log(response.contexts[0].content);
    }
  }
}

main().catch(console.error);
