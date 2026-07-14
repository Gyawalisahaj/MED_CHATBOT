from datetime import datetime, timezone
from typing import Optional
import re

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.postgres_session import get_pg_db
from app.models.users import User
from app.schemas.auth import (
    RegisterRequest, LoginRequest, GoogleLoginRequest,
    TokenResponse, RefreshRequest, RefreshResponse,
    UserPublic, ChangePasswordRequest,
)
from app.core.security import (
    hash_password, verify_password, validate_password_strength,
    create_access_token, create_refresh_token,
    decode_access_token, decode_refresh_token,
    verify_google_id_token,
)
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("auth_service")

_bearer = HTTPBearer(auto_error=True)

#  Token builder
def _token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token  = create_access_token(user.id, user.email),
        refresh_token = create_refresh_token(user.id),
        expires_in    = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user          = UserPublic.model_validate(user),
    )


def _touch_login(user: User, db: Session) -> None:
    try:
        user.last_login = datetime.now(timezone.utc)
        db.commit()
    except Exception as e:
        logger.warning(f"Could not update last_login for {user.id}: {e}")
        db.rollback()


#  FastAPI dependencies
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
    db:    Session                       = Depends(get_pg_db),
) -> User:
    payload = decode_access_token(creds.credentials)
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")
    return user


def get_verified_user(user: User = Depends(get_current_user)) -> User:
    """Like get_current_user but also requires email verification."""
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Check your inbox.",
        )
    return user


#  Register
def register_user(req: RegisterRequest, db: Session) -> TokenResponse:
    validate_password_strength(req.password)

    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken. Choose a different one.",
        )
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists. Please log in.",
        )

    user = User(
        username        = req.username,
        email           = req.email,
        full_name       = req.full_name,
        hashed_password = hash_password(req.password),
        is_google_user  = False,
        is_active       = True,
        is_verified     = False,  # flip to True after email verify click
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user registered: {user.username} / {user.email} (id={user.id})")
    return _token_response(user)



def login_user(req: LoginRequest, db: Session) -> TokenResponse:
    _BAD = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username/email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )


    user = (
        db.query(User).filter(User.username == req.identifier).first()
        or db.query(User).filter(User.email   == req.identifier).first()
    )

    if not user:
        verify_password("dummy", "$2b$12$dummyhashsotimingattacksdonotwork0000000000000000000")
        raise _BAD

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")

    if user.hashed_password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses Google Sign-In. Please log in with Google.",
        )

    if not verify_password(req.password, user.hashed_password):
        raise _BAD

    _touch_login(user, db)
    logger.info(f"Login: {user.username} (id={user.id})")
    return _token_response(user)



def google_login(req: GoogleLoginRequest, db: Session) -> TokenResponse:
    claims = verify_google_id_token(req.id_token)
    email  = claims["email"].lower()
    name   = claims.get("name")
    pic    = claims.get("picture")
    g_sub  = claims["sub"]

    user = db.query(User).filter(User.email == email).first()

    if user:
        # Existing account — link Google if not already linked
        changed = False
        if not user.google_id:
            user.google_id      = g_sub
            user.is_google_user = True
            changed = True
        if pic and not user.picture:
            user.picture = pic
            changed = True
        if not user.is_verified:
            user.is_verified = True   
            changed = True
        if changed:
            db.commit()
    else:
        # New Google user — auto-register
        # Derive a unique username from the email local-part
        base_uname = re.sub(r"[^a-z0-9_]", "_", email.split("@")[0])[:40]
        username   = base_uname
        suffix     = 1
        while db.query(User).filter(User.username == username).first():
            username = f"{base_uname}_{suffix}"
            suffix  += 1

        user = User(
            username        = username,
            email           = email,
            full_name       = name,
            picture         = pic,
            is_google_user  = True,
            google_id       = g_sub,
            is_active       = True,
            is_verified     = True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Google auto-register: {user.username} / {email} (id={user.id})")

    _touch_login(user, db)
    logger.info(f"Google login: {user.username} (id={user.id})")
    return _token_response(user)


# Token refresh 
def refresh_access_token(req: RefreshRequest, db: Session) -> RefreshResponse:
    payload = decode_refresh_token(req.refresh_token)
    user    = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or deactivated.")
    return RefreshResponse(
        access_token = create_access_token(user.id, user.email),
        expires_in   = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


#  Change password
def change_password(req: ChangePasswordRequest, current_user: User, db: Session) -> dict:
    if current_user.hashed_password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Sign-In accounts do not have a password.",
        )
    if not verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect.")
    validate_password_strength(req.new_password)
    current_user.hashed_password = hash_password(req.new_password)
    db.commit()
    logger.info(f"Password changed for user {current_user.id}")
    return {"message": "Password changed successfully."}