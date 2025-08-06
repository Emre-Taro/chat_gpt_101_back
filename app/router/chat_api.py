# File: app/router/chat_api.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import models
from app.schemas import chat_schema
from app.db.models.user import User
from app.auth.utils.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from datetime import datetime
from typing import Callable

router = APIRouter()

def get_user_dependency(user_id: str, db: Session = Depends(get_db)) -> User:
    """Dependency factory to get user from path parameter"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    user = db.query(User).filter(User.userId == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# get all the chats data from the db
@router.get("/{user_id}/chats", response_model=chat_schema.ChatResponse, status_code=status.HTTP_200_OK)
async def get_chats(user_id: str, user: User = Depends(get_user_dependency), db: Session = Depends(get_db)):
    chats = db.query(models.Chat).filter(models.Chat.userId == user.userId).order_by(models.Chat.created_at.asc()).all()
    return {"chats": chats}


# When a chat create button is clicked, this post request will be sent and a new chat will be added to the db
@router.post("/{user_id}/chats", status_code=status.HTTP_201_CREATED)
async def create_chat(user_id: str, user: User = Depends(get_user_dependency), db: Session = Depends(get_db)):
    new_chat = models.Chat(
        chatId=uuid.uuid4(),
        title = "New Chat",
        userId=user.userId,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat

# delete 
@router.delete("/{user_id}/chat/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(user_id: str, chat_id: uuid.UUID, user: User = Depends(get_user_dependency), db: Session = Depends(get_db)):
    chat = db.query(models.Chat).filter(models.Chat.chatId == chat_id, models.Chat.userId == user.userId).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return {"detail": "Chat deleted successfully"}
