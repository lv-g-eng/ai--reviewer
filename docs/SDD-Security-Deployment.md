# Security Design and Deployment Architecture
## AI-Based Code Reviewer Platform - Supplementary Design Document

---

# 5. Security Design

## 5.1 Security Architecture Overview

The platform implements defense-in-depth security with multiple layers:

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Network Security                                    │
│ - Firewall rules                                             │
│ - DDoS protection (Cloudflare)                               │
│ - VPC isolation                                              │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Transport Security                                  │
│ - TLS 1.3 encryption                                         │
│ - Certificate management (Let's Encrypt)                     │
│ - HSTS headers                                               │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Application Security                                │
│ - JWT authentication                                         │
│ - RBAC authorization                                         │
│ - Input validation                                           │
│ - CSRF protection                                            │
│ - XSS prevention                                             │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Data Security                                       │
│ - Encryption at rest (AES-256)                               │
│ - Database access control                                    │
│ - Secrets management (AWS KMS)                               │
│ - Audit logging                                              │
└─────────────────────────────────────────────────────────────┘
```

## 5.2 Authentication Mechanism

### JWT Token Structure

**Access Token (24-hour expiry)**:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "email": "user@example.com",
    "role": "programmer",
    "permissions": ["read:projects", "write:code"],
    "iat": 1708099200,
    "exp": 1708185600
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

**Refresh Token (7-day expiry)**:
- Stored in HTTP-only, secure cookie
- Used only for token refresh endpoint
- Revoked on logout or password change

### Password Security

**Hashing Algorithm**: bcrypt with cost factor 12

```python
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
```

**Password Policy**:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*)
- Password history: Last 5 passwords cannot be reused
- Password expiry: 90 days (configurable)

### Account Lockout

```python
class AccountLockoutPolicy:
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=30)
    
    async def handle_failed_login(self, user_id: UUID):
        """Handle failed login attempt"""
        user = await self.db.get_user(user_id)
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now() + self.LOCKOUT_DURATION
            await self.notification_service.send_lockout_email(user)
            await self.audit_log.log_account_locked(user_id)
        
        await self.db.update_user(user)
```

## 5.3 Authorization Model (RBAC)

### Role Hierarchy

```
Admin (Full Access)
  ├── Manager (Read All + Reports)
  │   ├── Reviewer (Read/Write Analysis)
  │   │   ├── Programmer (Read Analysis + Write Code)
  │   │   │   ├── User (Basic Access)
  │   │   │   │   └── Guest (Public Access)
```

### Permission Matrix

| Resource | Guest | User | Programmer | Reviewer | Manager | Admin |
|----------|-------|------|------------|----------|---------|-------|
| View Public Docs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Register/Login | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| View Own Projects | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| Add Repository | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| View Analysis Results | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| Submit PR | - | - | ✓ | ✓ | ✓ | ✓ |
| Accept/Dismiss Issues | - | - | ✓ | ✓ | ✓ | ✓ |
| Approve PR | - | - | - | ✓ | ✓ | ✓ |
| View All Projects | - | - | - | - | ✓ | ✓ |
| Generate Reports | - | - | - | - | ✓ | ✓ |
| Manage Users | - | - | - | - | - | ✓ |
| Configure System | - | - | - | - | - | ✓ |
| View Audit Logs | - | - | - | - | - | ✓ |

### Permission Enforcement

```python
from functools import wraps
from fastapi import HTTPException, Depends

def require_permission(permission: str):
    """Decorator to enforce permission requirements"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission} required"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/api/repositories")
@require_permission("write:repositories")
async def create_repository(data: CreateRepositoryDTO, current_user: User):
    # Implementation
    pass
```

## 5.4 Input Validation and Sanitization

### SQL Injection Prevention

```python
# BAD: String concatenation
query = f"SELECT * FROM users WHERE email = '{email}'"

# GOOD: Parameterized query
query = "SELECT * FROM users WHERE email = %s"
result = await db.execute(query, (email,))

# BEST: ORM with automatic escaping
user = await User.objects.filter(email=email).first()
```

### XSS Prevention

```python
import bleach
from markupsafe import escape

def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS"""
    allowed_tags = ['p', 'br', 'strong', 'em', 'code', 'pre']
    allowed_attributes = {}
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attributes)

def escape_user_input(text: str) -> str:
    """Escape user input for safe display"""
    return escape(text)
```

### CSRF Protection

```python
from fastapi_csrf_protect import CsrfProtect

@app.post("/api/repositories")
async def create_repository(
    data: CreateRepositoryDTO,
    csrf_protect: CsrfProtect = Depends()
):
    await csrf_protect.validate_csrf(request)
    # Implementation
```

## 5.5 Data Encryption

### Encryption at Rest

**Database Encryption**:
- PostgreSQL: Transparent Data Encryption (TDE)
- Neo4j: Encrypted storage volumes
- Redis: Encrypted snapshots

**Sensitive Data Encryption**:
```python
from cryptography.fernet import Fernet
import base64

class EncryptionService:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Usage for GitHub tokens, webhook secrets
encryption_service = EncryptionService(settings.ENCRYPTION_KEY)
encrypted_token = encryption_service.encrypt(github_token)
```

### Encryption in Transit

**TLS Configuration**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.codereview.com;
    
    # TLS 1.3 only
    ssl_protocols TLSv1.3;
    ssl_ciphers 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384';
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Certificate
    ssl_certificate /etc/letsencrypt/live/api.codereview.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.codereview.com/privkey.pem;
}
```

## 5.6 Secrets Management

### AWS Secrets Manager Integration

```python
import boto3
from botocore.exceptions import ClientError

class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager', region_name='us-east-1')
    
    def get_secret(self, secret_name: str) -> dict:
        """Retrieve secret from AWS Secrets Manager"""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except ClientError as e:
            logger.error(f"Failed to retrieve secret: {e}")
            raise

# Usage
secrets = SecretsManager()
db_credentials = secrets.get_secret('prod/database/credentials')
github_token = secrets.get_secret('prod/github/oauth-token')
```

### Environment Variables

```bash
# .env.example (never commit actual .env)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
ENCRYPTION_KEY=<generate-with-fernet-generate-key>
GITHUB_CLIENT_ID=<github-oauth-app-id>
GITHUB_CLIENT_SECRET=<github-oauth-app-secret>
OPENAI_API_KEY=<openai-api-key>
ANTHROPIC_API_KEY=<anthropic-api-key>
```

## 5.7 Audit Logging

### Audit Log Events

```python
class AuditLogger:
    EVENTS = {
        'USER_REGISTERED': 'User account created',
        'USER_LOGIN': 'User logged in',
        'USER_LOGOUT': 'User logged out',
        'USER_LOGIN_FAILED': 'Failed login attempt',
        'ACCOUNT_LOCKED': 'Account locked due to failed attempts',
        'PASSWORD_CHANGED': 'User changed password',
        'REPOSITORY_ADDED': 'Repository added to platform',
        'REPOSITORY_DELETED': 'Repository removed from platform',
        'ANALYSIS_STARTED': 'Code analysis started',
        'ANALYSIS_COMPLETED': 'Code analysis completed',
        'SETTINGS_CHANGED': 'System settings modified',
        'USER_ROLE_CHANGED': 'User role modified',
        'DATA_EXPORTED': 'Data exported',
    }
    
    async def log(self, event: str, user_id: UUID, details: dict, request: Request):
        """Log audit event"""
        await self.db.create_audit_log({
            'user_id': user_id,
            'action': event,
            'resource_type': details.get('resource_type'),
            'resource_id': details.get('resource_id'),
            'details': details,
            'ip_address': request.client.host,
            'user_agent': request.headers.get('user-agent'),
            'timestamp': datetime.now()
        })
```

### Audit Log Retention

- **Retention Period**: 7 years (compliance requirement)
- **Storage**: Append-only table with no delete permissions
- **Backup**: Daily backups to S3 with versioning
- **Access**: Admin-only, all access logged

---

# 6. Deployment Architecture

## 6.1 Infrastructure Overview

### Cloud Provider: AWS

**Regions**:
- Primary: us-east-1 (N. Virginia)
- Secondary: eu-west-1 (Ireland) - Disaster Recovery

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Route 53 (DNS)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CloudFront (CDN)                              │
│                    - Static assets                               │
│                    - DDoS protection                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                Application Load Balancer                         │
│                - SSL termination                                 │
│                - Health checks                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EKS Cluster (Kubernetes)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Frontend   │  │   API        │  │   Workers    │          │
│  │   Pods       │  │   Pods       │  │   Pods       │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   RDS        │  │   ElastiCache│  │   EC2        │          │
│  │  (PostgreSQL)│  │   (Redis)    │  │   (Neo4j)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

