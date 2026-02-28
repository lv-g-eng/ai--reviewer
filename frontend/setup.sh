#!/bin/bash
# Frontend Development Environment Setup Script

set -e

echo "=========================================="
echo "Frontend Development Environment Setup"
echo "=========================================="

# Check Node.js version
echo "Checking Node.js version..."
node_version=$(node --version 2>&1)
echo "Found Node.js $node_version"

# Check npm version
echo "Checking npm version..."
npm_version=$(npm --version 2>&1)
echo "Found npm $npm_version"

# Install dependencies
echo "Installing dependencies..."
npm install

# Create .env.local file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file from template..."
    cp .env.example .env.local
    echo ".env.local file created. Please update it with your configuration."
else
    echo ".env.local file already exists."
fi

# Run linting check
echo "Running linting check..."
npm run lint || echo "Linting check completed with warnings."

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo "To start the development server, run:"
echo "  npm run dev"
echo ""
echo "To run tests, run:"
echo "  npm test"
echo ""
echo "To build for production, run:"
echo "  npm run build"
echo "=========================================="
