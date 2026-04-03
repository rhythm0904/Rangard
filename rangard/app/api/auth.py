"""
app/api/auth.py
───────────────
Authentication endpoints:
  POST /api/auth/register         → create account
  POST /api/auth/login            → get JWT token
  GET  /api/auth/me               → get current user info
  POST /api/auth/verify-email     → verify email with token
  POST /api/auth/resend-verification → resend verification email
"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.models import User
from app.core.config import get_settings
from app.core.security import (
    create_access_token, 
    hash_password, 
    verify_password, 
    decode_token,
    create_email_verification_token,
    verify_email_token,
)
from app.services.email import get_email_service


router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)

# OAuth2 tells FastAPI where to find the token in requests
# (Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Pydantic schemas (request / response shapes) ──────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "alice@example.com",
                "password": "strongpassword123",
                "full_name": "Alice Smith",
            }
        }


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime


# ── Email verification response ────────────────────────────────────────────────

class VerifyEmailResponse(BaseModel):
    message: str
    email: str
    verified: bool


# ── Dependency: get the current authenticated user ────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency.  Add `user: User = Depends(get_current_user)` to any
    route that requires authentication.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise credentials_exception

    return user


# ── Routes ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = ""


@router.post("/register", response_model=LoginResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account and send verification email.
    
    The user receives a JWT token immediately but threat alerts will only
    be sent after they verify their email address via the link sent to them.
    """
    try:
        # Validate input
        if len(user.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must be at least 8 characters",
            )

        result = await db.execute(select(User).where(User.email == user.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        hashed_password = hash_password(user.password)
        new_user = User(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name or "",
            is_active=True,
            is_verified=False,  # Not verified until they click email link
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # Generate verification token and send email
        verification_token = create_email_verification_token(user.email)
        settings = get_settings()
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        email_svc = get_email_service()
        success, error_msg = email_svc.send_email_verification(user.email, verification_link)
        
        if success:
            logger.info(f"[Auth] New user registered: {new_user.email} — verification email sent")
        else:
            logger.warning(f"[Auth] Failed to send verification email to {new_user.email}: {error_msg}")

        token = create_access_token(str(new_user.id))
        
        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user_id=str(new_user.id),
            email=new_user.email,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Auth] Registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")





@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email + password.
    Uses OAuth2PasswordRequestForm so it's compatible with standard tooling
    (form fields: username, password — username = email here).
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    token = create_access_token(str(user.id))
    logger.info(f"[Auth] Login: {user.email}")

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(user.id),
        email=user.email,
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
    )


# ── Email verification endpoints ──────────────────────────────────────────────

class VerifyEmailRequest(BaseModel):
    token: str


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify a user's email address using the verification token from their email.
    Token is valid for 24 hours from registration.
    """
    try:
        # Decode the verification token
        payload = verify_email_token(request.token)
        email = payload.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )
        
        # Find the user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        if user.is_verified:
            return VerifyEmailResponse(
                message="Email already verified",
                email=email,
                verified=True,
            )
        
        # Mark user as verified
        user.is_verified = True
        db.add(user)
        await db.commit()
        
        logger.info(f"[Auth] Email verified: {email}")
        
        return VerifyEmailResponse(
            message="Email verified successfully! You can now receive threat alerts.",
            email=email,
            verified=True,
        )
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Auth] Email verification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed",
        )


@router.post("/resend-verification")
async def resend_verification(
    current_user: User = Depends(get_current_user),
):
    """
    Resend the email verification link to the currently logged-in user.
    Useful if they didn't receive the original email or it expired.
    """
    if current_user.is_verified:
        return {
            "message": "Your email is already verified!",
            "verified": True,
        }
    
    try:
        # Generate new verification token
        verification_token = create_email_verification_token(current_user.email)
        settings = get_settings()
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        # Send verification email
        email_svc = get_email_service()
        success, error_msg = email_svc.send_email_verification(current_user.email, verification_link)
        
        if success:
            logger.info(f"[Auth] Verification email re-sent to: {current_user.email}")
            return {
                "message": "Verification email sent. Check your inbox!",
                "verified": False,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg or "Failed to send verification email",
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Auth] Resend verification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email",
        )
