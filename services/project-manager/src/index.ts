import express from 'express';

const app = express();
const PORT = process.env.PORT || 3005;

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'project-manager' });
});

app.listen(PORT, () => {
  console.log(`Project Manager service listening on port ${PORT}`);
});
