
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict


#  Registration 
class RegisterRequest(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50,
        description="3-50 chars, letters/digits/underscores only",
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    email: EmailStr = Field(..., description="Valid email address")
    password: str   = Field(..., min_length=8, max_length=128,
                            description="Must meet strength requirements")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)

    @field_validator("username")
    @classmethod
    def username_no_reserved(cls, v: str) -> str:
        reserved = {"admin", "root", "system", "superuser", "null", "undefined"}
        if v.lower() in reserved:
            raise ValueError("This username is reserved. Choose a different one.")
        return v.lower()

    @field_validator("email")
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower().strip()

    @field_validator("full_name")
    @classmethod
    def full_name_no_html(cls, v: Optional[str]) -> Optional[str]:
        if v and re.search(r"<[^>]+>", v):
            raise ValueError("Full name must not contain HTML.")
        return v.strip() if v else v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username":  "drgyawali",
                "email":     "doctor@hospital.com",
                "password":  "MyM3d!c@l2025#",
                "full_name": "Dr. Gyawali",
            }
        }
    )


#  Login (username OR email + password) 
class LoginRequest(BaseModel):
    """
    Login with either username or email.
    The backend checks both columns.
    """
    identifier: str = Field(
        ..., min_length=1, max_length=255,
        description="Your username or email address",
    )
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("identifier")
    @classmethod
    def strip_identifier(cls, v: str) -> str:
        return v.strip().lower()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identifier": "drgyawali",    # or "doctor@hospital.com"
                "password":   "MyM3d!c@l2025#",
            }
        }
    )


# Google OAuth 
class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Google ID token from Google Sign-In button")

    model_config = ConfigDict(
        json_schema_extra={"example": {"id_token": "eyJhbGci..."}}
    )


#  Public user shape (never exposes hashed_password)
class UserPublic(BaseModel):
    id:             int
    username:       str
    email:          str
    full_name:      Optional[str]
    is_google_user: bool
    picture:        Optional[str]
    is_active:      bool
    is_verified:    bool
    created_at:     datetime

    model_config = ConfigDict(from_attributes=True)


# Token responses 
class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    expires_in:    int            # seconds until access_token expires
    user:          UserPublic     # embedded — client needs no extra /me call


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token from login response")


class RefreshResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int


# Password change (authenticated) 
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1,  max_length=128)
    new_password:     str = Field(..., min_length=8,  max_length=128)

    @model_validator(mode="after")
    def passwords_differ(self):
        if self.current_password == self.new_password:
            raise ValueError("New password must differ from current password.")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "MyM3d!c@l2025#",
                "new_password":     "N3wS3cur3#2026!",
            }
        }
    )