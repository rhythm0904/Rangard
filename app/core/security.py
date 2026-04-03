"""
app/core/security.py
────────────────────
Password hashing and JWT token generation / verification.

How JWT works (plain English):
  1. User logs in with email + password
  2. We verify the password, then create a token — a signed string
     containing the user's ID and an expiry time
  3. We send that token to the frontend
  4. On every future request, the frontend sends the token in the header
  5. We verify the signature — if valid, we trust the user ID inside it
     No database lookup needed for every request.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

# bcrypt is the gold standard for password hashing.
# It's intentionally slow — that's the point.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Convert a plain-text password into a bcrypt hash.
    The hash is safe to store in the database.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the plain password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    """
    Create a signed JWT token.
    `sub` (subject) is the standard JWT claim for the user identifier.
    `exp` is the expiry timestamp.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),   # issued-at
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Raises JWTError if the token is invalid or expired.
    Returns the payload dict (contains 'sub' = user_id).
    """
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
