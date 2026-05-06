const express = require('express');
const { AlchemystClient } = require('@alchemystai/sdk');

const app = express();
app.use(express.json());

const port = process.env.PORT || 3000;
const apiKey = process.env.ALCHEMYST_AI_API_KEY;

if (!apiKey) {
  console.error('ALCHEMYST_AI_API_KEY environment variable is required');
  process.exit(1);
}

const client = new AlchemystClient({
  apiKey: apiKey
});

/**
 * POST /ingest
 * Ingests a document into Alchemyst AI.
 * Body: { "content": "...", "group": "..." }
 */
app.post('/ingest', async (req, res) => {
  const { content, group } = req.body;

  if (!content || !group) {
    return res.status(400).json({ error: 'Missing content or group in request body' });
  }

  try {
    const result = await client.v1.context.add({
      content: content,
      context_type: 'resource',
      source: 'docs',
      scope: 'internal',
      metadata: {
        group_name: group
      }
    });

    res.status(201).json(result);
  } catch (error) {
    console.error('Error ingesting document:', error);
    res.status(500).json({ error: 'Failed to ingest document', details: error.message });
  }
});

/**
 * GET /research
 * Searches Alchemyst AI.
 * Query params: query, group
 */
app.get('/research', async (req, res) => {
  const { query, group } = req.query;

  if (!query || !group) {
    return res.status(400).json({ error: 'Missing query or group parameter' });
  }

  try {
    const results = await client.v1.context.search({
      query: query,
      filters: {
        group_name: group
      }
    });

    res.json(results);
  } catch (error) {
    console.error('Error searching Alchemyst AI:', error);
    res.status(500).json({ error: 'Failed to search', details: error.message });
  }
});

app.listen(port, () => {
  console.log(`B2B Newsletter API listening at http://localhost:${port}`);
});
