const express = require('express');
const multer = require('multer');
const { Alchemyst } = require('@alchemystai/sdk');
const { withAlchemyst } = require('@alchemystai/aisdk');
const { generateText } = require('ai');
const { openai } = require('@ai-sdk/openai');

const app = express();
const port = 3000;

// Use environment variables for API keys
const ALCHEMYST_AI_API_KEY = process.env.ALCHEMYST_AI_API_KEY;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const alchemyst = new Alchemyst({
  apiKey: ALCHEMYST_AI_API_KEY,
});

app.use(express.json());

// Setup multer for file uploads in memory
const upload = multer({ storage: multer.memoryStorage() });

// 1. POST /upload: Accepts a multipart/form-data file upload (field name 'file')
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }
  try {
    const text = req.file.buffer.toString('utf-8');
    res.json({ text });
  } catch (error) {
    res.status(500).json({ error: 'Failed to read file content' });
  }
});

// 2. POST /context/add: Adds documents to the context engine
app.post('/context/add', async (req, res) => {
  try {
    // Assuming the request body matches the Alchemyst API requirements
    // and using alchemyst.addContext to add documents.
    await alchemyst.addContext(req.body);
    res.json({ success: true });
  } catch (error) {
    console.error('Error adding context:', error);
    res.status(500).json({ error: error.message || 'Failed to add context' });
  }
});

// 3. POST /chat/generate: Generates a response using Alchemyst AI SDK and OpenAI
app.post('/chat/generate', async (req, res) => {
  try {
    const { chat_history } = req.body;
    if (!chat_history || !Array.isArray(chat_history)) {
      return res.status(400).json({ error: 'Invalid chat history' });
    }

    // Extract the latest user message content from the chat_history array
    // (the last item where type is 'human')
    const lastHumanMessage = [...chat_history].reverse().find(msg => msg.type === 'human');

    if (!lastHumanMessage) {
      return res.status(400).json({ error: 'No human message found in chat history' });
    }

    const prompt = lastHumanMessage.lc_kwargs?.content || lastHumanMessage.content;

    // Use withAlchemyst wrapper with generateText
    const { text } = await generateText({
      model: withAlchemyst(openai('gpt-4o-mini'), {
        userId: 'student_1',
        sessionId: 'syllabus_chat',
      }),
      prompt: prompt,
    });

    // Return the generated text in the specified format
    res.json({
      result: {
        response: {
          kwargs: {
            content: text
          }
        }
      }
    });
  } catch (error) {
    console.error('Error generating chat response:', error);
    res.status(500).json({ error: error.message || 'Failed to generate response' });
  }
});

app.listen(port, () => {
  console.log(`SyllabAI server running on port ${port}`);
});
