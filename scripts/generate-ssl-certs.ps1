# Generate self-signed SSL certificates for local development
# This script creates SSL certificates in the certs directory

$ErrorActionPreference = "Stop"

$CertsDir = ".\certs"
$DaysValid = 365

Write-Host "🔐 Generating self-signed SSL certificates for local development..." -ForegroundColor Cyan

# Create certs directory if it doesn't exist
if (-not (Test-Path $CertsDir)) {
    New-Item -ItemType Directory -Path $CertsDir | Out-Null
}

# Generate private key and certificate using OpenSSL
# Note: OpenSSL must be installed on Windows
try {
    & openssl req -x509 -nodes -days $DaysValid -newkey rsa:2048 `
        -keyout "$CertsDir\privkey.pem" `
        -out "$CertsDir\fullchain.pem" `
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    Write-Host "✅ SSL certificates generated successfully!" -ForegroundColor Green
    Write-Host "📁 Location: $CertsDir\" -ForegroundColor Yellow
    Write-Host "⚠️  Note: These are self-signed certificates for development only" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Restart nginx: docker-compose restart nginx"
    Write-Host "2. Access via: https://localhost"
}
catch {
    Write-Host "❌ Error: OpenSSL not found or failed to generate certificates" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install OpenSSL:" -ForegroundColor Yellow
    Write-Host "- Download from: https://slproweb.com/products/Win32OpenSSL.html"
    Write-Host "- Or use: choco install openssl"
    Write-Host "- Or use: winget install OpenSSL.OpenSSL"
    exit 1
}
