const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: 'test' });
console.log(typeof client.v1.context.memory.search);
