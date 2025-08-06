# File: app/router/message_api.py
from unittest import result
import uuid
import json
import os
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import models
from app.schemas.message_schema import MessageSchema, MessageInputSchema
from app.db.models.user import User
from app.auth.utils.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from app.openAPI.openai import generate_openai_response
from app.openAPI.title_generator import generate_title_from_message
from datetime import datetime
from typing import List
from app.db.models.message import Message
from app.db.models.chat import Chat

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

@router.get("/{user_id}/chat/{chat_id}/message", response_model=List[MessageSchema], status_code=status.HTTP_200_OK)
async def read_message(user_id: str, chat_id: uuid.UUID, user: User = Depends(get_user_dependency), db: Session = Depends(get_db)):
    # take all the messages in the chat with the given chat_id and user_id
    messages = db.query(Message).filter(
        Message.chatId == chat_id,
    ).order_by(Message.created_at.asc()).all()

    return [MessageSchema.model_validate(message) for message in messages]

@router.post("/{user_id}/chat/{chat_id}/message", status_code=status.HTTP_201_CREATED)
async def insert_message(
    user_id: str,
    chat_id: uuid.UUID, 
    input: MessageInputSchema,
    user: User = Depends(get_user_dependency), 
    db: Session = Depends(get_db)
        ):
    
    existing_messages = db.query(Message).filter_by(chatId=chat_id).count()
    if existing_messages == 0:
        generated_title: str | None = generate_title_from_message(input.content)
        chat = db.query(Chat).filter_by(chatId=chat_id).first()
        if chat:
            chat.title = generated_title
            db.commit()
    else:
        generated_title = input.title

    # Check if there's an image filename in the input
    image_filename = getattr(input, 'imageFilename', None)
    image_path = None

    if image_filename:
        image_path = os.path.join("static/uploads", image_filename)
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image file not found")


    # message of the user in the chat
    user_msg = Message(
        messageId = uuid.uuid4(),
        chatId = chat_id,
        userId = user.userId,
        content = input.content,
        title = generated_title,
        role = "user",
        created_at = datetime.utcnow()
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # message of the assistant in the chat
    messages = [
        {"role": "user", "content": input.content}
    ]
    ai_reply = generate_openai_response(messages)
    if isinstance(ai_reply, dict):
        content_str = json.dumps(ai_reply, ensure_ascii=False)
        print("OpenAI API error:", ai_reply["error"])
    else:
        content_str = ai_reply
        print("OpenAI response:", ai_reply)

    # 3. AIの返答もDBに保存
    ai_msg = Message(
        messageId=uuid.uuid4(),
        chatId=chat_id,
        userId=None,
        role="assistant",
        content=content_str,
        title=generated_title,
        created_at=datetime.utcnow()
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {
        "user": user_msg, 
        "assistant": ai_msg, 
        "generated_title": generated_title, 
        "chatId": str(chat_id)
    }
