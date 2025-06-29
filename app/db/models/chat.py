# File: app/db/models/chat.py
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from base import BaseModel  


class Chat(BaseModel):
    __tablename__ = 'chats'
    
    chatId: uuid = Column(String, primary_key=True, index=True)
    chatname: str = Column(String, nullable=False)
    userId: uuid = Column(String, ForeignKey('users.userId'), nullable=False)
    created_at = Column(DateTime, nullable = False)
    updated_at = Column(DateTime, nullable = False)

    messages = relationship("Message", back_populates="chat")  # Assuming Message model has a 'chat' relationship
    users = relationship("User", back_populates="chats")  # Assuming User model has a 'chats' relationship
