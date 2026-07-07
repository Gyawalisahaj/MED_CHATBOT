from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.db.postgres_session import AuthBase


class User(AuthBase):
    __tablename__ = "users"

    #  Primary key 
    id = Column(Integer, primary_key=True, autoincrement=True)

    #  Identity
    username  = Column(String(50),  unique=True, index=True, nullable=False)
    email     = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)

    #  Password auth (NULL for Google-only accounts)
    hashed_password = Column(String(255), nullable=True)

    #  Google OAuth 
    is_google_user = Column(Boolean,     default=False,  nullable=False)
    google_id      = Column(String(255), nullable=True,  unique=True)
    picture        = Column(String(512), nullable=True)

    #  Account flags 
    is_active   = Column(Boolean, default=True,  nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    #  Timestamps (server_default uses the DB clock)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    #  Composite index 
    __table_args__ = (
        Index("ix_users_email_google", "email", "is_google_user"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} email={self.email!r}>"