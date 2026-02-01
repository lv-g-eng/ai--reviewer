import express from 'express';

const app = express();
const PORT = process.env.PORT || 3004;

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'ai-service' });
});

app.listen(PORT, () => {
  console.log(`Agentic AI service listening on port ${PORT}`);
});
