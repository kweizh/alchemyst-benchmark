import { AlchemystAI } from '@alchemystai/sdk';
import { parseArgs } from 'util';
async function main() {
    const { values } = parseArgs({
        args: process.argv.slice(2),
        options: {
            question: {
                type: 'string',
            },
        },
    });
    const question = values.question;
    if (!question) {
        console.error("Missing --question argument");
        process.exit(1);
    }
    const client = new AlchemystAI({
        apiKey: process.env.ALCHEMYST_AI_API_KEY,
    });
    const runId = process.env.ZEALT_RUN_ID || 'default-run-id';
    const fileName = `refunds-${runId}.md`;
    const content = `# Refund Policy\nOur company offers a 30-day money-back refund policy for all purchases.\nIf you are not satisfied, you can request a full refund within 30 days of the original purchase date.`;
    // 1. Ingest document
    await client.v1.context.add({
        context_type: 'resource',
        documents: [{ content }],
        scope: 'internal',
        source: 'documentation',
        metadata: {
            fileName: fileName,
            file_name: fileName,
            fileSize: content.length,
            fileType: 'text/markdown',
            lastModified: new Date().toISOString(),
            group_name: 'policies'
        }
    });
    // 2. Search
    const searchRes = await client.v1.context.search({
        query: question,
        scope: 'internal',
        similarity_threshold: 0.7,
        minimum_similarity_threshold: 0.0,
    });
    // 3. Print
    if (searchRes.contexts && searchRes.contexts.length > 0) {
        for (const chunk of searchRes.contexts) {
            console.log(chunk.content);
        }
    }
    else {
        console.log("No results found. Response:", JSON.stringify(searchRes, null, 2));
    }
}
main().catch(err => {
    console.error(err);
    process.exit(1);
});
//# sourceMappingURL=index.js.map