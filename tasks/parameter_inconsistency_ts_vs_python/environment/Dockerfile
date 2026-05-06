FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-pytest bash && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="any-task-builder"
LABEL Description="Alchemyst AI parameter inconsistency test environment"

RUN mkdir -p /home/user/app && \
    cd /home/user/app && \
    cat > package.json <<'EOF'
{
  "name": "alchemyst-test",
  "version": "1.0.0",
  "dependencies": {
    "@alchemystai/sdk": "latest"
  },
  "devDependencies": {
    "tsx": "latest",
    "typescript": "latest",
    "@types/node": "latest"
  }
}
EOF

RUN cd /home/user/app && npm install

RUN cd /home/user/app && \
    cat > index.ts <<'EOF'
import AlchemystAI from '@alchemystai/sdk';
import * as fs from 'fs';

const alchemyst = new AlchemystAI({
  apiKey: process.env.ALCHEMYST_AI_API_KEY,
});

async function main() {
  const fileName = `eng-guidelines-${Date.now()}.md`;
  
  // Add document
  await alchemyst.v1.context.add({
    documents: [{
      content: "Engineering department guidelines",
      metadata: {
        file_name: fileName,
        group_name: ["engineering"]
      }
    }],
    context_type: 'resource',
    source: 'docs',
    scope: 'internal'
  });
  
  // Wait a moment for indexing
  await new Promise(resolve => setTimeout(resolve, 3000));

  // Search for context
  const { contexts } = await alchemyst.v1.context.search({
    query: "guidelines",
    similarity_threshold: 0.1,
    scope: 'internal',
    metadata: {
      // Intentional bug: using snake_case instead of camelCase for TypeScript SDK search
      group_name: ["engineering"]
    } as any
  });

  if (contexts && contexts.length > 0) {
    fs.writeFileSync('/home/user/app/output.txt', contexts[0].content);
    console.log("Document found and written to output.txt");
  } else {
    console.log("Document not found");
  }
}

main().catch(console.error);
EOF

# Container contents:
#   - Node.js v24 installed
#   - /home/user/app with package.json and index.ts
#   - @alchemystai/sdk installed

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]