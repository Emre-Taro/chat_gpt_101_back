# File: app/db/models/message.py
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from base import BaseModel


class Message(BaseModel):
    __tablename__ = 'messages'

    messageId: uuid = Column(String, primary_key=True, index=True)
    chatId: uuid = Column(String, index=True)
    userId: uuid = Column(String, ForeignKey('users.userId'), nullable=False)
    content: str = Column(String, nullable=False)
    chatname: str = Column(String, nullable=False)
    created_at = Column(DateTime, nullable = False)
    updated_at = Column(DateTime, nullable = False)

    chat = relationship("Chat", back_populates="messages")  # Assuming Chat model has a 'messages' relationship
    user = relationship("User", back_populates="messages")  # Assuming User model has a 'messages' relationship

