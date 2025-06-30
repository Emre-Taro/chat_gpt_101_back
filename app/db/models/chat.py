# File: app/db/models/chat.py
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import BaseModel  


class Chat(BaseModel):
    __tablename__ = 'chats'
    
    chatId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatname = Column(String, nullable=False)
    userId = Column(UUID(as_uuid=True), ForeignKey('users.userId'), nullable=False)
    created_at = Column(DateTime, nullable = False)
    updated_at = Column(DateTime, nullable = False)

    messages = relationship("Message", back_populates="chat")  # Assuming Message model has a 'chat' relationship
    users = relationship("User", back_populates="chats")  # Assuming User model has a 'chats' relationship
