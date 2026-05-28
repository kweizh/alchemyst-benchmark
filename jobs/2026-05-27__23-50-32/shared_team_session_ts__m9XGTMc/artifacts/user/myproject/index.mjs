import { AlchemystAI } from '@alchemystai/sdk';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

const apiKey = process.env.ALCHEMYST_AI_API_KEY;
const runId = process.env.ZEALT_RUN_ID || 'local';

if (!apiKey) {
  console.error('ALCHEMYST_AI_API_KEY is not set');
  process.exit(1);
}

const client = new AlchemystAI({
  apiKey: apiKey,
});

const userA = `${crypto.randomUUID()}-${runId}`;
const userB = `${crypto.randomUUID()}-${runId}`;
const sessionId = `${crypto.randomUUID()}-${runId}`;

const logFile = '/workspace/output.log';
const recallFile = '/workspace/team_recall.json';

// Ensure workspace directory exists (though /workspace is expected to exist)
if (!fs.existsSync('/workspace')) {
    fs.mkdirSync('/workspace', { recursive: true });
}

function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(logFile, logMessage);
  console.log(message);
}

async function run() {
  try {
    log(`Starting shared session simulation with runId: ${runId}`);
    log(`User A: ${userA}`);
    log(`User B: ${userB}`);
    log(`Session ID: ${sessionId}`);

    // User A adds memory
    log(`User A adding memory...`);
    // Manually calling the endpoint if SDK is failing or being restrictive
    // But let's try to find if there's any other way.
    // The requirement says "The TypeScript memory client lives at client.v1.context.memory and exposes add and search operations"
    // This strongly suggests I should be able to do client.v1.context.memory.search
    // Maybe I should check the 'memory' object itself in the code.
    
    // Let's try to use the SDK as described in the requirements, even if types don't show it.
    // I will use @ts-ignore or just call it since it's JS.
    
    await client.v1.context.memory.add({
      userId: userA,
      sessionId: sessionId,
      contents: [
        {
          content: 'Project codename is Falcon',
        },
      ],
    });
    log(`User A added memory.`);

    // Wait for propagation
    log(`Waiting 5 seconds for propagation...`);
    await new Promise((resolve) => setTimeout(resolve, 5000));

    // User B searches memory
    log(`User B searching memory...`);
    let searchResponse;
    try {
        searchResponse = await client.v1.context.memory.search({
          userId: userB,
          sessionId: sessionId,
          query: 'What is the project codename?',
        });
    } catch (e) {
        log(`client.v1.context.memory.search failed: ${e.message}. Trying client.v1.context.search`);
        searchResponse = await client.v1.context.search({
            query: 'What is the project codename?',
            user_id: userB,
            minimum_similarity_threshold: 0.1,
            similarity_threshold: 0.1,
            body_metadata: {
                sessionId: sessionId
            }
        });
    }
    log(`User B search complete.`);

    let recalled = [];
    if (searchResponse.memories) {
        recalled = searchResponse.memories.map(m => typeof m.content === 'string' ? m.content : JSON.stringify(m.content));
    } else if (searchResponse.contexts) {
        recalled = searchResponse.contexts.map(c => c.content).filter(Boolean);
    }
    
    const report = {
      userA,
      userB,
      sessionId,
      recalled
    };

    fs.writeFileSync(recallFile, JSON.stringify(report, null, 2));
    log(`Recall report written to ${recallFile}`);
    log(`Recall complete: ${sessionId}`);

  } catch (error) {
    log(`Error: ${error.message}`);
    if (error.stack) log(error.stack);
    process.exit(1);
  }
}

run();
