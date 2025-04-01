from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Integer, func
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy with type support
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, server_default="1")
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'

    @staticmethod
    def validate_registration(username: str, password: str, display_name: str) -> tuple[bool, str]:
        """Validate registration input fields"""
        if not username or not username.strip():
            return False, "Username is required"
        if not password or not password.strip():
            return False, "Password is required"
        if not display_name or not display_name.strip():
            return False, "Display name is required"
        if len(username) > 80:
            return False, "Username must be less than 80 characters"
        if len(password) > 120:
            return False, "Password must be less than 120 characters"
        if len(display_name) > 50:
            return False, "Display name must be less than 50 characters"
        return True, ""