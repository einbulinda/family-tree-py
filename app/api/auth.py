import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    UserRead,
    Token,
)


router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger("family_tree.auth")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    logger.info(f"User registration attempt: {payload.email}")
    # Check if email is already used
    existing = db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        logger.warning(f"Duplicate registration attempt: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=get_password_hash(payload.password),
        role="member",
        is_approved=True,  # or False if you want an approval flow
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"User login success: {user.email} (ID={user.id})")
    return user


@router.post("/login", response_model=Token)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    logger.info(f"Login attempt for: {payload.email}")
    stmt = select(User).where(User.email == payload.email)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning(f"Failed login attempt: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    logger.info(f"Login success for: {payload.email}")
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    logger.info(f"Fetching profile for user: {current_user.email}")
    return current_user
