# File: app/db/models/user.py
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from app.db. base import BaseModel
from datetime import datetime


class User(BaseModel):
    __tablename__ = 'users'
    
    userId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    chats = relationship("Chat", back_populates="users")  # Assuming Chat model has a 'users' relationship
    messages = relationship("Message", back_populates="user")