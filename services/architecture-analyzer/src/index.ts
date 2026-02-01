import express from 'express';
import { llmClient, ModelType } from '../../../shared/llm-client';

const app = express();
const PORT = process.env.PORT || 3003;

app.use(express.json());

app.get('/health', async (req, res) => {
  const llmHealth = await llmClient.healthCheck();
  res.json({
    status: 'healthy',
    service: 'architecture-analyzer',
    llm: llmHealth,
  });
});

app.post('/analyze', async (req, res) => {
  try {
    const { components, dependencies, patterns } = req.body;

    if (!components || !dependencies) {
      return res.status(400).json({
        error: 'Missing required fields: components, dependencies',
      });
    }

    // Use local LLM for architecture analysis
    const prompt = `Analyze this system architecture:
Components: ${JSON.stringify(components)}
Dependencies: ${JSON.stringify(dependencies)}
Patterns: ${JSON.stringify(patterns || [])}

Provide architecture quality assessment and recommendations.`;

    const result = await llmClient.generate({
      prompt,
      model_type: ModelType.GENERAL,
      temperature: 0.2,
      max_tokens: 1024,
    });

    res.json({
      success: true,
      analysis: result.response,
    });
  } catch (error) {
    console.error('Architecture analysis failed:', error);
    res.status(500).json({
      error: 'Analysis failed',
      details: String(error),
    });
  }
});

app.listen(PORT, () => {
  console.log(`Architecture Analyzer service listening on port ${PORT}`);
  console.log(`LLM Service URL: ${process.env.LLM_SERVICE_URL || 'http://localhost:8000'}`);
});
