"""Debug script for token generation."""
from services.auth_service import AuthService
from models import Role

# Test token generation and validation
token = AuthService.generate_token('test-id-123', 'testuser', Role.ADMIN)
print(f"Generated token: {token[:50]}...")

payload = AuthService.validate_token(token)
if payload:
    print(f"Token is valid!")
    print(f"  user_id: {payload.user_id}")
    print(f"  username: {payload.username}")
    print(f"  role: {payload.role}")
    print(f"  iat: {payload.iat}")
    print(f"  exp: {payload.exp}")
else:
    print("Token validation failed!")
