const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const { AlchemystAI } = require('@alchemystai/sdk');
const path = require('path');

const app = express();
const port = 3000;

app.use(express.json());

// Initialize SQLite
const dbPath = path.join(__dirname, 'zendocs.db');
const db = new sqlite3.Database(dbPath);

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS documents (
      file_name TEXT PRIMARY KEY,
      content TEXT,
      group_name TEXT
    )
  `);
});

// Initialize Alchemyst SDK
const client = new AlchemystAI({
  apiKey: process.env.ALCHEMYST_AI_API_KEY,
});

// POST /api/docs/generate
app.post('/api/docs/generate', async (req, res) => {
  const { fileName, content, group } = req.body;

  if (!fileName || !content || !group) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    // Save or update in SQLite
    await new Promise((resolve, reject) => {
      db.run(
        `INSERT INTO documents (file_name, content, group_name) 
         VALUES (?, ?, ?) 
         ON CONFLICT(file_name) DO UPDATE SET content=excluded.content, group_name=excluded.group_name`,
        [fileName, content, group],
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });

    // Add to Alchemyst AI
    try {
      await client.v1.context.add({
        documents: [{ content, metadata: { file_name: fileName, group_name: [group] } }],
        scope: 'internal',
      });
    } catch (error) {
      // Handling Updates: If 409 Conflict, delete and retry
      if (error.response && error.response.status === 409) {
        await client.v1.context.delete({
          metadata: { file_name: fileName },
        });
        await client.v1.context.add({
          documents: [{ content, metadata: { file_name: fileName, group_name: [group] } }],
          scope: 'internal',
        });
      } else {
        throw error;
      }
    }

    res.status(200).json({ message: 'Document generated and indexed successfully' });
  } catch (error) {
    console.error('Error in /api/docs/generate:', error);
    res.status(500).json({ error: 'Internal Server Error', details: error.message });
  }
});

// GET /api/docs/search
app.get('/api/docs/search', async (req, res) => {
  const { q, group } = req.query;

  if (!q) {
    return res.status(400).json({ error: 'Missing search query' });
  }

  try {
    const searchParams = {
      query: q,
      similarity_threshold: 0.5,
      scope: 'internal',
    };

    if (group) {
      // Storage uses group_name, but search filtering requires groupName (camelCase)
      searchParams.metadata = { groupName: group };
    }

    const response = await client.v1.context.search(searchParams);

    res.status(200).json({ results: response.contexts || [] });
  } catch (error) {
    console.error('Error in /api/docs/search:', error);
    res.status(500).json({ error: 'Internal Server Error', details: error.message });
  }
});

app.listen(port, () => {
  console.log(`Zendocs backend listening at http://localhost:${port}`);
});
