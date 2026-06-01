import { AlchemystAI } from '@alchemystai/sdk';

async function main() {
  const apiKey = process.env.ALCHEMYST_AI_API_KEY;
  const runId = process.env.ZEALT_RUN_ID;

  if (!apiKey || !runId) {
    console.error('Missing ALCHEMYST_AI_API_KEY or ZEALT_RUN_ID environment variables');
    process.exit(1);
  }

  const client = new AlchemystAI({ apiKey });
  const groupName = `threshold-${runId}`;

  const documents = [
    {
      content: 'Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including structured, object-oriented and functional programming.',
      metadata: {
        file_name: `python-${runId}.md`,
        group_name: [groupName],
        fileName: `python-${runId}.md`
      }
    },
    {
      content: 'JavaScript, often abbreviated as JS, is a programming language that is one of the core technologies of the World Wide Web, alongside HTML and CSS. As of 2023, 98.7% of websites use JavaScript on the client side for webpage behavior, often incorporating third-party libraries.',
      metadata: {
        file_name: `js-${runId}.md`,
        group_name: [groupName],
        fileName: `js-${runId}.md`
      }
    },
    {
      content: 'Baking a chocolate cake involves mixing flour, sugar, cocoa powder, baking powder, baking soda, and salt. Then add eggs, milk, oil, and vanilla extract. Beat on medium speed for two minutes. Stir in boiling water by hand. Pour into pans and bake in a preheated oven at 350 degrees Fahrenheit.',
      metadata: {
        file_name: `cake-${runId}.md`,
        group_name: [groupName],
        fileName: `cake-${runId}.md`
      }
    }
  ];

  for (const doc of documents) {
    const fileName = doc.metadata.file_name;
    try {
      // Best-effort delete any pre-existing document with the same file_name
      // Note: TypeScript search uses camelCase for metadata filters in some contexts, 
      // but the hint says client.v1.context.delete({ metadata: { fileName: ... } })
      await client.v1.context.delete({
        metadata: {
          fileName: fileName
        }
      });
      console.log(`Deleted existing document: ${fileName}`);
    } catch (error) {
      // Ignore errors during deletion
    }
  }

  try {
    await client.v1.context.add({
      documents: documents,
      context_type: 'resource',
      source: 'docs',
      scope: 'internal',
      metadata: {
        fileName: 'seed-batch',
        fileSize: 0,
        fileType: 'text/markdown',
        lastModified: new Date().toISOString()
      }
    });
    console.log('Successfully added documents');
  } catch (error) {
    console.error('Error adding documents:', error);
    process.exit(1);
  }
}

main();
