"""Simple token test."""
import sys
sys.path.insert(0, '.')

from enterprise_rbac_auth.services.auth_service import AuthService
from enterprise_rbac_auth.models import Role
import jwt
from enterprise_rbac_auth.config import settings

# Test with the exact values from the failing test
user_id = "00000000-0000-0000-0000-000000000000"
username = "000"
role = Role.ADMIN

print(f"Generating token for user_id={user_id}, username={username}, role={role}")
token = AuthService.generate_token(user_id, username, role)
print(f"Token generated: {token[:80]}...")

# Try to decode manually
try:
    decoded = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    print(f"Manual decode successful: {decoded}")
except Exception as e:
    print(f"Manual decode failed: {e}")

# Try with AuthService
payload = AuthService.validate_token(token)
if payload:
    print(f"AuthService validation successful!")
    print(f"  Payload: user_id={payload.user_id}, username={payload.username}, role={payload.role}")
else:
    print(f"AuthService validation failed!")
