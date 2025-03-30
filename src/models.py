from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy with type support
db = SQLAlchemy()

# Create a base class for declarative models
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)

    def __repr__(self) -> str:
        return f'<User {self.username}>'