#always make models sqlalchemy 2.0 syntax
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy with type support
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'