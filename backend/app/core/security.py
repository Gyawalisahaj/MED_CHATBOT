import re
import math
import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("security")

#  Bcrypt context 
# rounds=12 → ~400 ms per hash — correct for commercial production
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

#Password policy constants 
_COMMON_PASSWORDS = {
    "password", "password1", "password123", "12345678", "123456789",
    "qwerty123", "iloveyou", "admin123", "letmein1", "welcome1",
    "monkey123", "dragon123", "sunshine1", "princess1", "superman1",
    "baseball1", "football1", "master123", "shadow123", "michael1",
}
_RE_UPPER   = re.compile(r"[A-Z]")
_RE_LOWER   = re.compile(r"[a-z]")
_RE_DIGIT   = re.compile(r"\d")
_RE_SPECIAL = re.compile(r"[!@#$%^&*()\-_=+\[\]{}|;:',.<>?/`~\"\\]")
_RE_REPEAT  = re.compile(r"(.)\1{2,}")


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def validate_password_strength(password: str) -> None:
    if len(password) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must not exceed 128 characters.",
        )
    errors = []
    if len(password) < 8:
        errors.append("Minimum 8 characters required.")
    if not _RE_UPPER.search(password):
        errors.append("Must contain at least one uppercase letter (A-Z).")
    if not _RE_LOWER.search(password):
        errors.append("Must contain at least one lowercase letter (a-z).")
    if not _RE_DIGIT.search(password):
        errors.append("Must contain at least one digit (0-9).")
    if not _RE_SPECIAL.search(password):
        errors.append("Must contain at least one special character (!@#$%^&* etc.).")
    if password.lower() in _COMMON_PASSWORDS:
        errors.append("This password is too common. Choose something unique.")
    if _RE_REPEAT.search(password):
        errors.append("Must not have 3+ consecutive identical characters (e.g. aaa).")
    if _shannon_entropy(password) < 3.0:
        errors.append("Password is too predictable. Use a more varied mix.")
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Password does not meet security requirements.",
                "errors": errors,
                "hint": "Strong example: MyM3d!c@l2025#",
            },
        )


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


#  JWT helpers 
def _encode(payload: dict, expires: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload.update({"iat": now, "exp": now + expires, "type": token_type})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int, email: str) -> str:
    return _encode(
        {"sub": str(user_id), "email": email},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(user_id: int) -> str:
    return _encode(
        {"sub": str(user_id), "jti": secrets.token_hex(16)},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def _decode(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != expected_type:
            raise JWTError("wrong token type")
        return payload
    except JWTError as exc:
        logger.warning(f"JWT decode failed ({expected_type}): {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_access_token(token: str) -> dict:
    return _decode(token, "access")


def decode_refresh_token(token: str) -> dict:
    return _decode(token, "refresh")


#   Google ID-token verification 
def verify_google_id_token(id_token: str) -> dict:
    try:
        from google.oauth2 import id_token as _id_token
        from google.auth.transport import requests as _greq
        claims = _id_token.verify_oauth2_token(
            id_token, _greq.Request(), settings.GOOGLE_CLIENT_ID, clock_skew_in_seconds=10
        )
        if not claims.get("email_verified"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google account email is not verified.",
            )
        return claims
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google auth not available on this server.",
        )
    except ValueError as exc:
        logger.warning(f"Google token verify failed: {exc}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google ID token.")