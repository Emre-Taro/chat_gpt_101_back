# File: app/router/message_api.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import models
from app.schemas.message_schema import MessageSchema
from app.db.models.user import User
from app.auth.utils.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from datetime import datetime
from typing import List

from app.router.chat_api import user_exists

router = APIRouter()

@router.get("/{user_id}/chat/{chat_id}/{message}", response_model=List[MessageSchema], status_code=status.HTTP_200_OK)
async def read_message(chat_id: uuid.UUID, user: User = Depends(user_exists), db: Session = Depends(get_db)):
    # take all the messages in the chat with the given chat_id and user_id
    messages = db.query(models.Message).filter(
        models.Message.chatId == chat_id,
        models.Message.userId == user.userId
    ).all()
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    return [MessageSchema.model_validate(message) for message in messages]

@router.post("/{user_id}/chat/{chat_id}/{message}", status_code=status.HTTP_201_CREATED)
async def insert_message(chat_id: uuid.UUID, user: User = Depends(user_exists), db: Session = Depends(get_db)):
    new_message_user = models.Message(
        messageId = uuid.uuid4(),
        chatId = chat_id,
        userId = user.userId,
        content = "New message content",
        chatname = "New Chat",
        created_at = datetime.utcnow()
    )
    db.add(new_message_user)
    db.commit()
    db.refresh(new_message_user)
    return new_message_user
