# File: app/db/models/user.py
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from base import BaseModel  


class User(BaseModel):
    __tablename__ = 'users'
    
    userId: uuid = Column(String, primary_key=True, index=True)
    username: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False, unique=True)
    password: str = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    chats = relationship("Chat", back_populates="users")  # Assuming Chat model has a 'users' relationship