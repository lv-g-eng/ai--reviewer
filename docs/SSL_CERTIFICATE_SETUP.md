# SSL Certificate Setup and Validation

This document provides instructions for setting up and validating SSL certificates for the AI Code Review Platform production environment.

## Table of Contents

1. [Overview](#overview)
2. [Certificate Requirements](#certificate-requirements)
3. [Obtaining SSL Certificates](#obtaining-ssl-certificates)
4. [Certificate Installation](#certificate-installation)
5. [Certificate Validation](#certificate-validation)
6. [Certificate Renewal](#certificate-renewal)
7. [Troubleshooting](#troubleshooting)

## Overview

SSL/TLS certificates are required for secure HTTPS communication in production. The platform requires valid SSL certificates for:

- Main application domain (e.g., `your-domain.com`)
- API subdomain (if separate, e.g., `api.your-domain.com`)
- Any additional subdomains

## Certificate Requirements

### Required Files

The following certificate files must be present in the `certs/` directory:

```
certs/
├── fullchain.pem    # Full certificate chain (certificate + intermediate certificates)
├── privkey.pem      # Private key
├── cert.pem         # Certificate only (optional, for reference)
└── chain.pem        # Intermediate certificates (optional, for reference)
```

### Certificate Specifications

- **Type**: X.509 SSL/TLS certificate
- **Key Size**: Minimum 2048-bit RSA or 256-bit ECC
- **Validity**: Recommended 90 days (Let's Encrypt) or up to 1 year
- **Subject Alternative Names (SAN)**: Include all domains and subdomains
- **Certificate Authority**: Trusted CA (Let's Encrypt, DigiCert, etc.)

## Obtaining SSL Certificates

### Option 1: Let's Encrypt (Recommended for Most Cases)

Let's Encrypt provides free, automated SSL certificates with 90-day validity.

#### Using Certbot

1. **Install Certbot**:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot

# macOS
brew install certbot
```

2. **Obtain Certificate** (Standalone Mode):

```bash
sudo certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  --email admin@your-domain.com \
  --agree-tos \
  --non-interactive
```

3. **Obtain Certificate** (Webroot Mode, if web server is running):

```bash
sudo certbot certonly --webroot \
  -w /var/www/html \
  -d your-domain.com \
  -d www.your-domain.com \
  --email admin@your-domain.com \
  --agree-tos \
  --non-interactive
```

4. **Copy Certificates to Project**:

```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem certs/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem certs/
sudo chmod 644 certs/fullchain.pem
sudo chmod 600 certs/privkey.pem
```

#### Using Docker with Certbot

```bash
docker run -it --rm \
  -v "$(pwd)/certs:/etc/letsencrypt" \
  -p 80:80 \
  certbot/certbot certonly --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  --email admin@your-domain.com \
  --agree-tos \
  --non-interactive
```

### Option 2: Commercial Certificate Authority

If using a commercial CA (DigiCert, GlobalSign, etc.):

1. **Generate Certificate Signing Request (CSR)**:

```bash
openssl req -new -newkey rsa:2048 -nodes \
  -keyout certs/privkey.pem \
  -out certs/request.csr \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

2. **Submit CSR to CA**: Follow your CA's process to submit the CSR and verify domain ownership.

3. **Download Certificate**: Once issued, download the certificate and intermediate chain.

4. **Create Full Chain**:

```bash
cat certificate.crt intermediate.crt > certs/fullchain.pem
```

### Option 3: Self-Signed Certificate (Development/Testing Only)

**WARNING**: Self-signed certificates should NEVER be used in production.

```bash
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout certs/privkey.pem \
  -out certs/fullchain.pem \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

## Certificate Installation

### 1. Create Certificate Directory

```bash
mkdir -p certs
chmod 755 certs
```

### 2. Place Certificate Files

Ensure the following files are in the `certs/` directory:

- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key

### 3. Set Correct Permissions

```bash
chmod 644 certs/fullchain.pem
chmod 600 certs/privkey.pem
```

**Security Note**: The private key (`privkey.pem`) should have restricted permissions (600) to prevent unauthorized access.

### 4. Update Nginx Configuration

The Nginx configuration should reference the certificate files:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # ... rest of configuration
}
```

### 5. Verify Nginx Configuration

```bash
nginx -t
```

### 6. Reload Nginx

```bash
nginx -s reload
# or
systemctl reload nginx
```

## Certificate Validation

### Automated Validation

The production environment validation script automatically checks SSL certificates:

```bash
bash scripts/validate-production-env.sh
```

This script verifies:
- Certificate files exist
- Certificate is not expired
- Certificate expiration date (warns if < 30 days)

### Manual Validation

#### Check Certificate Details

```bash
openssl x509 -in certs/fullchain.pem -text -noout
```

#### Check Certificate Expiration

```bash
openssl x509 -in certs/fullchain.pem -noout -enddate
```

#### Verify Certificate Chain

```bash
openssl verify -CAfile certs/fullchain.pem certs/fullchain.pem
```

#### Test HTTPS Connection

```bash
curl -vI https://your-domain.com
```

#### Check Certificate from Browser

1. Open your site in a browser (e.g., `https://your-domain.com`)
2. Click the padlock icon in the address bar
3. View certificate details
4. Verify:
   - Issued to correct domain
   - Valid date range
   - Trusted certificate authority

#### Online SSL Testing Tools

- **SSL Labs**: https://www.ssllabs.com/ssltest/
  - Comprehensive SSL/TLS configuration analysis
  - Security grade (A+ to F)
  - Identifies vulnerabilities

- **SSL Checker**: https://www.sslshopper.com/ssl-checker.html
  - Quick certificate validation
  - Chain verification
  - Expiration check

## Certificate Renewal

### Let's Encrypt Auto-Renewal

Let's Encrypt certificates expire after 90 days. Set up automatic renewal:

#### Using Certbot

1. **Test Renewal**:

```bash
sudo certbot renew --dry-run
```

2. **Set Up Cron Job**:

```bash
# Edit crontab
sudo crontab -e

# Add renewal job (runs twice daily)
0 0,12 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

3. **Copy Renewed Certificates**:

Create a renewal hook script:

```bash
#!/bin/bash
# /etc/letsencrypt/renewal-hooks/post/copy-certs.sh

cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /path/to/project/certs/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /path/to/project/certs/
chmod 644 /path/to/project/certs/fullchain.pem
chmod 600 /path/to/project/certs/privkey.pem
systemctl reload nginx
```

Make it executable:

```bash
chmod +x /etc/letsencrypt/renewal-hooks/post/copy-certs.sh
```

### Manual Renewal

If automatic renewal fails or you're using a commercial CA:

1. **Obtain New Certificate** (follow steps in "Obtaining SSL Certificates")
2. **Replace Old Certificate Files**
3. **Reload Nginx**:

```bash
nginx -s reload
```

4. **Verify New Certificate**:

```bash
openssl x509 -in certs/fullchain.pem -noout -enddate
```

### Renewal Monitoring

Set up monitoring to alert before certificate expiration:

- **Prometheus + Alertmanager**: Monitor certificate expiration
- **Uptime Monitoring Services**: Many services check SSL expiration
- **Email Alerts**: Configure alerts 30, 14, and 7 days before expiration

## Troubleshooting

### Certificate Not Found

**Error**: `SSL certificate file not found`

**Solution**:
1. Verify files exist in `certs/` directory
2. Check file names match exactly: `fullchain.pem`, `privkey.pem`
3. Verify file permissions

### Certificate Expired

**Error**: `SSL certificate has expired`

**Solution**:
1. Renew certificate immediately
2. Follow renewal steps above
3. Reload Nginx after renewal

### Certificate Chain Issues

**Error**: `unable to get local issuer certificate`

**Solution**:
1. Ensure `fullchain.pem` includes full certificate chain
2. Verify intermediate certificates are included
3. Test chain: `openssl verify -CAfile certs/fullchain.pem certs/fullchain.pem`

### Permission Denied

**Error**: `Permission denied` when accessing certificate files

**Solution**:
```bash
chmod 644 certs/fullchain.pem
chmod 600 certs/privkey.pem
chown www-data:www-data certs/*.pem  # Adjust user as needed
```

### Domain Mismatch

**Error**: `Certificate does not match domain`

**Solution**:
1. Verify certificate Subject Alternative Names (SAN) include your domain
2. Check certificate: `openssl x509 -in certs/fullchain.pem -text -noout | grep DNS`
3. Obtain new certificate with correct domains

### Browser Security Warning

**Error**: Browser shows "Your connection is not private"

**Possible Causes**:
1. Self-signed certificate (not trusted)
2. Expired certificate
3. Certificate chain incomplete
4. Domain mismatch

**Solution**:
1. Use certificate from trusted CA
2. Renew expired certificate
3. Include full certificate chain
4. Ensure certificate matches domain

## Security Best Practices

1. **Never Commit Private Keys**: Ensure `certs/` directory is in `.gitignore`
2. **Restrict Permissions**: Private key should be readable only by necessary users
3. **Use Strong Encryption**: Minimum 2048-bit RSA or 256-bit ECC
4. **Enable HSTS**: Force HTTPS with HTTP Strict Transport Security
5. **Disable Weak Protocols**: Use only TLS 1.2 and TLS 1.3
6. **Monitor Expiration**: Set up alerts for certificate expiration
7. **Rotate Regularly**: Even if not expired, consider rotating annually
8. **Backup Certificates**: Keep secure backups of certificates and keys

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Best Practices](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)
- [OWASP TLS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)

## Support

For issues with SSL certificate setup:

1. Check this documentation
2. Review Nginx error logs: `/var/log/nginx/error.log`
3. Test certificate with SSL Labs
4. Consult your certificate authority's documentation
5. Contact your DevOps team or system administrator
