#!/bin/bash
# Setup script for Enterprise RBAC Authentication System

echo "Setting up Enterprise RBAC Authentication System..."

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "WARNING: Please update JWT_SECRET_KEY in .env before running in production!"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the application, run:"
echo "  python main.py"
echo ""
echo "To run tests, run:"
echo "  pytest"
