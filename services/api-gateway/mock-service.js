// Simple mock backend service for testing
const express = require('express');
const app = express();

app.use(express.json());

// Mock health endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', service: 'mock-backend', timestamp: new Date().toISOString() });
});

// Mock API endpoints
app.get('/api/projects', (req, res) => {
    res.json({
        data: [
            { id: 1, name: 'Test Project 1', description: 'Mock project 1' },
            { id: 2, name: 'Test Project 2', description: 'Mock project 2' }
        ],
        meta: { total: 2, page: 1, limit: 10 }
    });
});

app.post('/api/projects', (req, res) => {
    const project = {
        id: 3,
        name: req.body.name || 'New Project',
        description: req.body.description || 'New project description',
        createdAt: new Date().toISOString()
    };
    res.status(201).json({ data: project });
});

app.get('/api/projects/:id', (req, res) => {
    const id = req.params.id;
    res.json({
        data: {
            id: parseInt(id),
            name: `Project ${id}`,
            description: `Description for project ${id}`,
            createdAt: '2026-01-22T10:00:00Z'
        }
    });
});

// Mock error scenarios
app.get('/api/error/500', (req, res) => {
    res.status(500).json({ error: 'Internal Server Error', message: 'Mock server error' });
});

app.get('/api/slow', (req, res) => {
    // Simulate slow response (6 seconds - should trigger circuit breaker timeout)
    setTimeout(() => {
        res.json({ message: 'This was a slow response' });
    }, 6000);
});

const port = process.argv[2] || 3001;
app.listen(port, () => {
    console.log(`Mock service running on port ${port}`);
});

module.exports = app;