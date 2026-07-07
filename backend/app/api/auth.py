
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.postgres_session import get_pg_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, GoogleLoginRequest,
    TokenResponse, RefreshRequest, RefreshResponse,
    UserPublic, ChangePasswordRequest,
)
from app.services.auth_service import (
    register_user, login_user, google_login,
    refresh_access_token, change_password,
    get_current_user,
)
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("auth_api")

router = APIRouter()



@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register with username + email + password",
)
def register(req: RegisterRequest, db: Session = Depends(get_pg_db)):
    logger.info(f"Register attempt: username={req.username} email={req.email}")
    return register_user(req, db)

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with username or email + password",
)
def login(req: LoginRequest, db: Session = Depends(get_pg_db)):
    logger.info(f"Login attempt: identifier={req.identifier}")
    return login_user(req, db)



@router.post(
    "/google",
    response_model=TokenResponse,
    summary="Login or register with Google",
)
def login_with_google(req: GoogleLoginRequest, db: Session = Depends(get_pg_db)):
    logger.info("Google OAuth login attempt")
    return google_login(req, db)



@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Refresh access token",
)
def refresh(req: RefreshRequest, db: Session = Depends(get_pg_db)):
    return refresh_access_token(req, db)



@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user info",
)
def me(current_user: User = Depends(get_current_user)):
    return UserPublic.model_validate(current_user)



@router.post(
    "/change-password",
    summary="Change password (authenticated)",
)
def change_pwd(
    req:          ChangePasswordRequest,
    current_user: User    = Depends(get_current_user),
    db:           Session = Depends(get_pg_db),
):
    return change_password(req, current_user, db)



@router.post(
    "/logout",
    summary="Logout (client-side)",
)
def logout(current_user: User = Depends(get_current_user)):
    logger.info(f"Logout: user {current_user.id}")
    return {"message": "Logged out. Please discard your tokens on the client side."}