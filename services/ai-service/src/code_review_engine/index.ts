import express from 'express';
import { llmClient } from '../../../shared/llm-client';

const app = express();
const PORT = process.env.PORT || 3002;

app.use(express.json());

app.get('/health', async (req, res) => {
  const llmHealth = await llmClient.healthCheck();
  res.json({
    status: 'healthy',
    service: 'ai-service',
    llm: llmHealth,
  });
});

app.post('/analyze', async (req, res) => {
  try {
    const { code, language, analysis_type } = req.body;

    if (!code || !language) {
      return res.status(400).json({
        error: 'Missing required fields: code, language',
      });
    }

    // Use local LLM for code analysis
    const result = await llmClient.analyzeCode({
      code,
      language,
      analysis_type: analysis_type || 'review',
    });

    res.json(result);
  } catch (error) {
    console.error('Analysis failed:', error);
    res.status(500).json({
      error: 'Analysis failed',
      details: String(error),
    });
  }
});

app.get('/models', async (req, res) => {
  try {
    const models = await llmClient.listModels();
    res.json({ success: true, models });
  } catch (error) {
    res.status(500).json({
      error: 'Failed to list models',
      details: String(error),
    });
  }
});

app.listen(PORT, () => {
  console.log(`Code Review Engine service listening on port ${PORT}`);
  console.log(`LLM Service URL: ${process.env.LLM_SERVICE_URL || 'http://localhost:8000'}`);
});
