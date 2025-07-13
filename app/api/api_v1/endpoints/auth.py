from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from loguru import logger

from app.core.config import settings
from app.core.security import (
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_password_hash
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, 
    LoginResponse, 
    RefreshTokenRequest, 
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    AuthResponse
)
from app.schemas.user import UserInDB
from app.core.exceptions import AuthenticationError, ValidationError

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=RegisterResponse)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        is_active=True,
        is_verified=False  # Email verification required
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email}")
    
    return RegisterResponse(
        message="User registered successfully. Please verify your email.",
        user_id=new_user.id,
        email=new_user.email
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    
    # Authenticate user
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise AuthenticationError("Incorrect email or password")
    
    if not user.is_active:
        raise AuthenticationError("Account is deactivated")
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        subject=user.id, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        subject=user.id,
        expires_delta=refresh_token_expires
    )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"User logged in: {user.email}")
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
            "total_points": user.total_points
        }
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    # Verify refresh token
    user_id = verify_token(refresh_data.refresh_token, "refresh")
    if not user_id:
        raise AuthenticationError("Invalid refresh token")
    
    # Check if user exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires
    )
    
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", response_model=AuthResponse)
async def logout():
    """Logout user (client should remove tokens)"""
    return AuthResponse(
        success=True,
        message="Logged out successfully"
    )


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify user email with token"""
    # TODO: Implement email verification logic
    # This would involve:
    # 1. Decode verification token
    # 2. Update user.is_verified = True
    # 3. Return success response
    
    return AuthResponse(
        success=True,
        message="Email verification endpoint (to be implemented)"
    )


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    """Send password reset email"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal if email exists or not
        return AuthResponse(
            success=True,
            message="If the email exists, a password reset link has been sent"
        )
    
    # TODO: Implement password reset email logic
    logger.info(f"Password reset requested for: {email}")
    
    return AuthResponse(
        success=True,
        message="If the email exists, a password reset link has been sent"
    )
