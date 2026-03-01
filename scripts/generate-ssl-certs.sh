#!/bin/bash

# Generate self-signed SSL certificates for local development
# This script creates SSL certificates in the certs directory

set -e

CERTS_DIR="./certs"
DAYS_VALID=365

echo "🔐 Generating self-signed SSL certificates for local development..."

# Create certs directory if it doesn't exist
mkdir -p "$CERTS_DIR"

# Generate private key and certificate
openssl req -x509 -nodes -days $DAYS_VALID -newkey rsa:2048 \
    -keyout "$CERTS_DIR/privkey.pem" \
    -out "$CERTS_DIR/fullchain.pem" \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "✅ SSL certificates generated successfully!"
echo "📁 Location: $CERTS_DIR/"
echo "⚠️  Note: These are self-signed certificates for development only"
echo ""
echo "Next steps:"
echo "1. Restart nginx: docker-compose restart nginx"
echo "2. Access via: https://localhost"
