# Data Encryption Implementation

This document describes the encryption implementation for the AI Code Review Platform.

**Implements Requirements:**
- **8.4**: Encrypt all sensitive data at rest using AES-256 encryption
- **8.5**: Encrypt all data in transit using TLS 1.3

## Overview

The platform implements defense-in-depth encryption:

1. **Data in Transit**: TLS 1.3 for all network connections
2. **Data at Rest**: AES-256-GCM for sensitive database fields
3. **Key Management**: Support for AWS KMS or environment-based keys

## Data in Transit (TLS 1.3)

### Configuration

TLS/SSL is configured in `app/core/tls_config.py` with:

- **Minimum Protocol**: TLS 1.3 (fallback to TLS 1.2 if unavailable)
- **Cipher Suites**: Strong ciphers with Perfect Forward Secrecy
  - TLS_AES_256_GCM_SHA384
  - TLS_AES_128_GCM_SHA256
  - TLS_CHACHA20_POLY1305_SHA256
  - ECDHE-RSA-AES256-GCM-SHA384 (TLS 1.2 fallback)
- **Certificate Verification**: CERT_REQUIRED by default

### Setup for Development

Generate self-signed certificates for local development:

```bash
python backend/scripts/generate_ssl_certs.py
```

This creates:
- `certs/server.crt` - SSL certificate
- `certs/server.key` - Private key (permissions set to 600)

Update `.env`:
```bash
SSL_ENABLED=true
SSL_CERT_FILE=certs/server.crt
SSL_KEY_FILE=certs/server.key
```

### Setup for Production

For production, use certificates from a trusted Certificate Authority:

**Option 1: Let's Encrypt (Recommended for self-hosted)**
```bash
certbot certonly --standalone -d yourdomain.com
```

**Option 2: AWS Certificate Manager (Recommended for AWS)**
- Create certificate in ACM
- Attach to Application Load Balancer
- ALB handles TLS termination

**Option 3: Commercial CA**
- Purchase certificate from DigiCert, GlobalSign, etc.
- Install certificate and private key

Update `.env` with production certificate paths:
```bash
SSL_ENABLED=true
SSL_CERT_FILE=/etc/ssl/certs/yourdomain.crt
SSL_KEY_FILE=/etc/ssl/private/yourdomain.key
SSL_CA_FILE=/etc/ssl/certs/ca-bundle.crt
```

### Running with TLS

Start Uvicorn with SSL:
```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8443 \
  --ssl-keyfile certs/server.key \
  --ssl-certfile certs/server.crt
```

Or use the TLS configuration in code:
```python
from app.core.tls_config import tls_config

ssl_context = tls_config.create_server_ssl_context()
# Pass to Uvicorn or other server
```

## Data at Rest (AES-256-GCM)

### Encryption Service

The `EncryptionService` in `app/services/encryption_service.py` provides:

- **Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Size**: 256 bits (32 bytes)
- **Nonce Size**: 96 bits (12 bytes, randomly generated per encryption)
- **Authentication**: 128-bit authentication tag (prevents tampering)

### Key Management

**Option 1: Environment Variable (Development/Small Deployments)**

Generate a key:
```bash
python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"
```

Add to `.env`:
```bash
ENCRYPTION_KEY=your_base64_encoded_32_byte_key
```

**Option 2: AWS KMS (Production/Enterprise)**

Configure AWS KMS:
```bash
# Create KMS key
aws kms create-key --description "AI Code Review Platform Encryption Key"

# Add to .env
AWS_KMS_KEY_ID=arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012
```

The service automatically uses KMS when `AWS_KMS_KEY_ID` is set.

### Encrypted Database Fields

Use custom SQLAlchemy types for automatic encryption/decryption:

```python
from app.database.encrypted_types import EncryptedString, EncryptedText
from sqlalchemy import Column
from app.database.postgresql import Base

class User(Base):
    __tablename__ = "users"
    
    # Automatically encrypted/decrypted
    api_key = Column(EncryptedString(255))
    private_notes = Column(EncryptedText)
```

### Sensitive Fields

The following fields are encrypted at rest:

| Table | Field | Purpose |
|-------|-------|---------|
| `projects` | `github_webhook_secret` | GitHub webhook validation |
| Future | API keys, tokens | External service credentials |

### Encrypting Existing Data

After adding encryption to a field, encrypt existing plaintext data:

```bash
# Check encryption status
python backend/scripts/encrypt_existing_data.py --status

# Dry run (preview changes)
python backend/scripts/encrypt_existing_data.py --dry-run

# Encrypt all data
python backend/scripts/encrypt_existing_data.py

# Encrypt specific table/field
python backend/scripts/encrypt_existing_data.py --table projects --field github_webhook_secret
```

### Manual Encryption/Decryption

For manual encryption in application code:

```python
from app.services.encryption_service import get_encryption_service

encryption_service = get_encryption_service()

# Encrypt
encrypted = encryption_service.encrypt("sensitive data")

# Decrypt
plaintext = encryption_service.decrypt(encrypted)

# Encrypt database field (handles None values)
encrypted_field = encryption_service.encrypt_field(value)
decrypted_field = encryption_service.decrypt_field(encrypted_value)
```

## Key Rotation

### Environment Key Rotation

1. Generate new key:
   ```bash
   python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"
   ```

2. Decrypt all data with old key
3. Update `ENCRYPTION_KEY` in environment
4. Re-encrypt all data with new key

### AWS KMS Key Rotation

AWS KMS supports automatic key rotation:

```bash
# Enable automatic rotation (yearly)
aws kms enable-key-rotation --key-id $KMS_KEY_ID
```

For manual rotation:
```python
from app.services.encryption_service import AWSKMSEncryptionService

kms_service = AWSKMSEncryptionService()
kms_service.rotate_key()
```

## Security Best Practices

### Key Storage

✅ **DO:**
- Store keys in AWS Secrets Manager or similar
- Use environment variables for keys
- Restrict key file permissions (chmod 600)
- Use AWS KMS for production
- Rotate keys regularly (annually minimum)

❌ **DON'T:**
- Commit keys to version control
- Share keys via email/chat
- Use the same key across environments
- Store keys in application code
- Use weak or short keys

### Encryption Usage

✅ **DO:**
- Encrypt all sensitive data (passwords, tokens, API keys, PII)
- Use authenticated encryption (GCM mode)
- Generate random nonces for each encryption
- Validate decryption (catch exceptions)
- Log encryption failures

❌ **DON'T:**
- Reuse nonces
- Use ECB mode
- Encrypt without authentication
- Ignore decryption errors
- Log plaintext sensitive data

### TLS Configuration

✅ **DO:**
- Use TLS 1.3 (or minimum TLS 1.2)
- Use strong cipher suites
- Enable Perfect Forward Secrecy
- Verify certificates (CERT_REQUIRED)
- Use certificates from trusted CAs in production

❌ **DON'T:**
- Use SSL 2.0, SSL 3.0, TLS 1.0, or TLS 1.1
- Use weak ciphers (RC4, DES, MD5)
- Disable certificate verification
- Use self-signed certificates in production
- Ignore certificate expiration

## Monitoring and Auditing

### Encryption Metrics

Monitor encryption operations:
- Encryption/decryption success rate
- Encryption operation latency
- Key rotation events
- Decryption failures (potential tampering)

### Audit Logging

All encryption-related events are logged:
- Key generation/rotation
- Encryption/decryption operations
- Certificate loading
- TLS handshake failures

Check logs:
```bash
grep "encryption" backend/app.log
grep "TLS" backend/app.log
```

## Troubleshooting

### "ENCRYPTION_KEY environment variable not set"

Generate and set encryption key:
```bash
export ENCRYPTION_KEY=$(python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())")
```

### "Failed to decrypt data - invalid key or corrupted data"

Possible causes:
- Wrong encryption key
- Data was encrypted with different key
- Data corruption
- Data was not encrypted (legacy plaintext)

Solution:
1. Verify `ENCRYPTION_KEY` is correct
2. Check if data needs migration from old key
3. Verify database integrity

### "Certificate file not found"

Generate certificates:
```bash
python backend/scripts/generate_ssl_certs.py
```

Or update paths in `.env`:
```bash
SSL_CERT_FILE=/path/to/cert.crt
SSL_KEY_FILE=/path/to/key.key
```

### "TLS 1.3 not available"

Your Python version may not support TLS 1.3. The system will fallback to TLS 1.2.

Upgrade Python to 3.7+ for TLS 1.3 support.

## Testing

### Test Encryption Service

```bash
pytest backend/tests/test_encryption_service.py -v
```

### Test TLS Configuration

```bash
pytest backend/tests/test_tls_config.py -v
```

### Test Encrypted Database Fields

```bash
pytest backend/tests/test_encrypted_types.py -v
```

## Compliance

This implementation satisfies:

- **OWASP**: Cryptographic Storage Cheat Sheet
- **PCI DSS**: Requirement 3 (Protect Stored Cardholder Data)
- **GDPR**: Article 32 (Security of Processing)
- **HIPAA**: 164.312(a)(2)(iv) (Encryption and Decryption)
- **ISO 27001**: A.10.1.1 (Cryptographic Controls)

## References

- [NIST SP 800-175B: Guideline for Using Cryptographic Standards](https://csrc.nist.gov/publications/detail/sp/800-175b/rev-1/final)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [RFC 8446: TLS 1.3](https://tools.ietf.org/html/rfc8446)
- [RFC 5288: AES-GCM Cipher Suites for TLS](https://tools.ietf.org/html/rfc5288)
