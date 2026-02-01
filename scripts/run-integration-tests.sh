#!/bin/bash

echo "Starting Integration Tests..."
echo

echo "Installing dependencies..."
npm install

echo
echo "Running integration tests..."
npm run test:integration

echo
echo "Integration tests completed."