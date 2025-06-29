# File: app/db/models/message.py
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import BaseModel
from datetime import datetime


class Message(BaseModel):
    __tablename__ = 'messages'

    messageId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chatId = Column(UUID(as_uuid=True), ForeignKey('chats.chatId'), index=True)
    userId = Column(UUID(as_uuid=True), ForeignKey('users.userId'), nullable=False)
    content = Column(String, nullable=False)
    chatname = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    chat = relationship("Chat", back_populates="messages")  # Assuming Chat model has a 'messages' relationship
    user = relationship("User", back_populates="messages")  # Assuming User model has a 'messages' relationship

