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

# Use argon2 for password hashing (more modern than bcrypt, no 72-byte limit).
# argon2 is memory-hard and intentionally slow against brute force attacks.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """
    Convert a plain-text password into an argon2 hash.
    The hash is safe to store in the database.
    Argon2 is more secure than bcrypt and has no byte-length constraints.
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Return True if the plain password matches the stored hash.
    Works with argon2 hashes, which have no length constraints.
    """
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


# ── Email verification tokens ───────────────────────────────────────────────

def create_email_verification_token(email: str) -> str:
    """
    Create a signed token for email verification.
    Token expires in EMAIL_VERIFICATION_EXPIRE_HOURS hours.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS
    )
    payload = {
        "email": email,
        "type": "email_verification",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_email_token(token: str) -> dict:
    """
    Decode and validate an email verification token.
    Returns dict with 'email' key if valid.
    Raises JWTError if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "email_verification":
            raise JWTError("Invalid token type")
        return payload
    except JWTError as e:
        raise JWTError(f"Email verification token invalid: {str(e)}")

