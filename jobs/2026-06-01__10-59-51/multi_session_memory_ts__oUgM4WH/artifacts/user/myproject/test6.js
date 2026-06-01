const { AlchemystAI } = require('@alchemystai/sdk');
const client = new AlchemystAI({ apiKey: 'test' });
console.log(Object.keys(client.v1.context.memory));
console.log(Object.getOwnPropertyNames(Object.getPrototypeOf(client.v1.context.memory)));
