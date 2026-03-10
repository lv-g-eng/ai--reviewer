#!/usr/bin/env python3
"""
Security Configuration Checker
Validates that all security settings are properly configured
"""

import os
import sys
import secrets
import string
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_jwt_secret():
    """Check if JWT secret is properly configured"""
    jwt_secret = os.getenv('AUTH_JWT_SECRET_KEY', '')
    
    if not jwt_secret:
        print("❌ AUTH_JWT_SECRET_KEY not set")
        return False
    
    if jwt_secret == 'dev-secret-key-change-in-production':
        print("❌ JWT secret is still using default development value")
        return False
    
    if len(jwt_secret) < 32:
        print("❌ JWT secret is too short (minimum 32 characters)")
        return False
    
    print("✅ JWT secret is properly configured")
    return True

def check_bcrypt_rounds():
    """Check if bcrypt rounds are secure"""
    rounds = int(os.getenv('AUTH_BCRYPT_ROUNDS', '12'))
    
    if rounds < 12:
        print(f"❌ Bcrypt rounds ({rounds}) is too low (minimum 12)")
        return False
    
    print(f"✅ Bcrypt rounds ({rounds}) is secure")
    return True

def check_https_config():
    """Check HTTPS configuration"""
    force_https = os.getenv('FORCE_HTTPS', 'false').lower() == 'true'
    secure_cookies = os.getenv('SECURE_COOKIES', 'false').lower() == 'true'
    
    if not force_https:
        print("⚠️  FORCE_HTTPS is not enabled (recommended for production)")
    else:
        print("✅ HTTPS is enforced")
    
    if not secure_cookies:
        print("⚠️  SECURE_COOKIES is not enabled (recommended for production)")
    else:
        print("✅ Secure cookies are enabled")
    
    return force_https and secure_cookies

def check_database_encryption():
    """Check database encryption key"""
    encryption_key = os.getenv('DATABASE_ENCRYPTION_KEY', '')
    
    if not encryption_key:
        print("❌ DATABASE_ENCRYPTION_KEY not set")
        return False
    
    if len(encryption_key) < 32:
        print("❌ Database encryption key is too short (minimum 32 bytes)")
        return False
    
    print("✅ Database encryption key is configured")
    return True

def check_redis_config():
    """Check Redis configuration"""
    redis_url = os.getenv('REDIS_URL', '')
    
    if not redis_url:
        print("❌ REDIS_URL not set")
        return False
    
    print("✅ Redis is configured")
    return True

def check_rate_limiting():
    """Check rate limiting configuration"""
    login_limit = int(os.getenv('LOGIN_RATE_LIMIT_REQUESTS', '5'))
    login_window = int(os.getenv('LOGIN_RATE_LIMIT_WINDOW', '60'))
    
    if login_limit > 10:
        print(f"⚠️  Login rate limit ({login_limit}) might be too high")
    else:
        print(f"✅ Login rate limit ({login_limit} requests per {login_window}s) is secure")
    
    return True

def generate_secure_key(length=64):
    """Generate a secure random key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_config_template():
    """Generate secure configuration template"""
    template = f"""# Generated Secure Configuration
# Copy these values to your .env.production file

AUTH_JWT_SECRET_KEY={generate_secure_key(64)}
AUTH_JWT_ALGORITHM=HS256
AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=480
AUTH_JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

AUTH_BCRYPT_ROUNDS=12

DATABASE_ENCRYPTION_KEY={generate_secure_key(32)}

REDIS_URL=redis://localhost:6379/0

FORCE_HTTPS=true
SECURE_COOKIES=true

LOGIN_RATE_LIMIT_REQUESTS=5
LOGIN_RATE_LIMIT_WINDOW=60

ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=900
"""
    
    config_file = Path("backend/.env.production.secure")
    with open(config_file, 'w') as f:
        f.write(template)
    
    print(f"✅ Generated secure configuration template: {config_file}")
    print("⚠️  Review and customize the values before using in production")

def main():
    """Main security check function"""
    print("🔒 Security Configuration Checker")
    print("=" * 40)
    
    checks = [
        check_jwt_secret,
        check_bcrypt_rounds,
        check_https_config,
        check_database_encryption,
        check_redis_config,
        check_rate_limiting,
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Security Score: {passed}/{total}")
    
    if passed < total:
        print("❌ Some security checks failed. Please review the configuration.")
        print("\n💡 Run with --generate to create a secure configuration template:")
        print("   python scripts/security_check.py --generate")
        sys.exit(1)
    else:
        print("✅ All security checks passed!")
    
    if '--generate' in sys.argv:
        print("\n🔧 Generating secure configuration template...")
        generate_config_template()

if __name__ == '__main__':
    main()