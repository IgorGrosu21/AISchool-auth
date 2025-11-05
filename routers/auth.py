from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
from core.database import get_db
from models.models import User
from schemas.schemas import (
    SignUpRequest, LoginRequest, GoogleLoginRequest, FacebookLoginRequest,
    TokenResponse
)
from utils.jwt_utils import create_tokens_for_user

router = APIRouter(tags=["auth"])

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignUpRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email_already_exists"
        )
    
    # Create new user
    user = User(
        email=request.email,
        signup_method='email',
        is_verified=False,
    )
    user.set_password(request.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate tokens and create token record in database
    tokens = create_tokens_for_user(user.email, db)
    return TokenResponse(**tokens)

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    # Find user
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="email_not_found"
        )
    
    # Check password
    if not user.check_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="password_incorrect"
        )
    
    # Generate tokens and create token record in database
    tokens = create_tokens_for_user(user.email, db)
    return TokenResponse(**tokens)

@router.post("/google-login", response_model=TokenResponse)
async def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    """Login with Google OAuth token"""
    try:
        # Verify Google token
        response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={request.token}",
            timeout=10
        )
        response.raise_for_status()
        token_info = response.json()
        
        if "error" in token_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid_google_token"
            )
        
        if "email" not in token_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email_not_provided_by_google"
            )
        
        verified_email = token_info["email"].lower()
        
        # If frontend provided email, verify it matches
        if request.user_email:
            if request.user_email.lower() != verified_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="email_mismatch"
                )
        
        # Find user
        user = db.query(User).filter(User.email == verified_email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="email_not_found"
            )
        
        # Generate tokens and create token record in database
        tokens = create_tokens_for_user(user.email, db)
        return TokenResponse(**tokens)
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="failed_to_verify_google_token"
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_google_token"
        ) from e

@router.post("/facebook-login", response_model=TokenResponse)
async def facebook_login(request: FacebookLoginRequest, db: Session = Depends(get_db)):
    """Login with Facebook OAuth token"""
    try:
        # Verify Facebook token
        response = requests.get(
            f"https://graph.facebook.com/me?fields=email&access_token={request.token}",
            timeout=10
        )
        response.raise_for_status()
        token_info = response.json()
        
        if "error" in token_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invalid_facebook_token"
            )
        
        if "email" not in token_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email_not_provided_by_facebook"
            )
        
        verified_email = token_info["email"].lower()
        
        # If frontend provided email, verify it matches
        if request.user_email:
            if request.user_email.lower() != verified_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="email_mismatch"
                )
        
        # Find user
        user = db.query(User).filter(User.email == verified_email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="email_not_found"
            )
        
        # Generate tokens and create token record in database
        tokens = create_tokens_for_user(user.email, db)
        return TokenResponse(**tokens)
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="failed_to_verify_facebook_token"
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_facebook_token"
        ) from e
