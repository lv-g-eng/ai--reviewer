"""
Authentication service for password hashing, JWT token management, and user authentication.
"""
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
import uuid
from sqlalchemy.orm import Session as DBSession

from ..config import settings
from ..models import User, Session as SessionModel, Role
from ..database import get_db


class AuthResult:
    """Result of an authentication attempt."""
    def __init__(self, success: bool, token: Optional[str] = None, 
                 user: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        self.success = success
        self.token = token
        self.user = user
        self.error = error


class TokenPayload:
    """Data class for JWT token payload."""
    def __init__(self, user_id: str, username: str, role: str, iat: int, exp: int):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.iat = iat
        self.exp = exp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JWT encoding."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "iat": self.iat,
            "exp": self.exp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenPayload':
        """Create TokenPayload from dictionary."""
        return cls(
            user_id=data["user_id"],
            username=data["username"],
            role=data["role"],
            iat=data["iat"],
            exp=data["exp"]
        )


class AuthService:
    """Service for handling authentication operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password as a string
        """
        # Generate salt and hash the password
        salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def generate_token(user_id: str, username: str, role: Role) -> str:
        """
        Generate a JWT token for a user.
        
        Args:
            user_id: User's unique identifier
            username: User's username
            role: User's role
            
        Returns:
            JWT token as a string
        """
        now = datetime.now(timezone.utc)
        iat = int(now.timestamp())
        exp = int((now + timedelta(minutes=settings.jwt_access_token_expire_minutes)).timestamp())
        
        payload = TokenPayload(
            user_id=user_id,
            username=username,
            role=role.value,
            iat=iat,
            exp=exp
        )
        
        token = jwt.encode(
            payload.to_dict(),
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        return token
    
    @staticmethod
    def validate_token(token: str) -> Optional[TokenPayload]:
        """
        Validate a JWT token and return its payload.
        
        Args:
            token: JWT token to validate
            
        Returns:
            TokenPayload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return TokenPayload.from_dict(payload)
        except jwt.ExpiredSignatureError:
            # Token has expired
            return None
        except jwt.InvalidTokenError:
            # Token is invalid
            return None
        except KeyError:
            # Missing required fields in payload
            return None
        except Exception:
            # Any other error
            return None
    
    @staticmethod
    def refresh_token(token: str) -> Optional[str]:
        """
        Refresh a JWT token if it's still valid and close to expiration.
        
        Args:
            token: Current JWT token
            
        Returns:
            New JWT token if refresh is successful, None otherwise
        """
        # First decode without verification to check expiration
        try:
            payload_dict = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
                options={"verify_exp": False}  # Don't verify expiration yet
            )
            payload = TokenPayload.from_dict(payload_dict)
        except Exception:
            return None
        
        # Check if token is within refresh window (e.g., less than 10 minutes remaining)
        now = int(datetime.now(timezone.utc).timestamp())
        time_until_expiry = payload.exp - now
        refresh_window = 600  # 10 minutes in seconds
        
        # Token must be either:
        # 1. Still valid but close to expiration (within refresh window)
        # 2. Or recently expired (within grace period)
        grace_period = 300  # 5 minutes grace period after expiration
        
        if time_until_expiry < refresh_window and time_until_expiry > -grace_period:
            # Generate new token with same user info
            return AuthService.generate_token(
                payload.user_id,
                payload.username,
                Role(payload.role)
            )
        
        # Token is either too fresh or too old
        return None
    
    @staticmethod
    def login(db: DBSession, username: str, password: str, ip_address: str = "0.0.0.0", 
              device_info: Optional[str] = None) -> AuthResult:
        """
        Authenticate a user and create a session.
        
        Args:
            db: Database session
            username: User's username
            password: User's password
            ip_address: IP address of the client
            device_info: Optional device information
            
        Returns:
            AuthResult with success status, token, and user info or error message
        """
        try:
            # Find user by username
            user = db.query(User).filter(User.username == username).first()
            
            # Generic error message to prevent username enumeration
            generic_error = "Invalid username or password"
            
            if not user:
                return AuthResult(success=False, error=generic_error)
            
            # Check if user is active
            if not user.is_active:
                return AuthResult(success=False, error="Account is disabled")
            
            # Verify password
            if not AuthService.verify_password(password, user.password_hash):
                return AuthResult(success=False, error=generic_error)
            
            # Generate JWT token
            token = AuthService.generate_token(user.id, user.username, user.role)
            
            # Create session record
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(minutes=settings.session_expire_minutes)
            
            session = SessionModel(
                id=str(uuid.uuid4()),
                user_id=user.id,
                token=token,
                issued_at=now,
                expires_at=expires_at,
                is_valid=True,
                device_info=device_info,
                ip_address=ip_address
            )
            db.add(session)
            
            # Update last login timestamp
            user.last_login = now
            
            db.commit()
            
            # Return success with token and user info
            user_info = {
                "id": user.id,
                "username": user.username,
                "role": user.role.value,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            
            return AuthResult(success=True, token=token, user=user_info)
            
        except Exception as e:
            db.rollback()
            return AuthResult(success=False, error=f"An error occurred: {str(e)}")
    
    @staticmethod
    def logout(db: DBSession, user_id: str, token: str) -> bool:
        """
        Invalidate a user's session.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            token: JWT token to invalidate
            
        Returns:
            True if logout was successful, False otherwise
        """
        try:
            # Find and invalidate the session
            session = db.query(SessionModel).filter(
                SessionModel.user_id == user_id,
                SessionModel.token == token,
                SessionModel.is_valid == True
            ).first()
            
            if session:
                session.is_valid = False
                db.commit()
                return True
            
            return False
            
        except Exception:
            db.rollback()
            return False
