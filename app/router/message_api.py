# File: app/router/message_api.py
from unittest import result
import uuid
import json
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
from datetime import datetime
from typing import List

from app.router.chat_api import user_exists

router = APIRouter()

@router.get("/{user_id}/chat/{chat_id}/message", response_model=List[MessageSchema], status_code=status.HTTP_200_OK)
async def read_message(chat_id: uuid.UUID, user: User = Depends(user_exists), db: Session = Depends(get_db)):
    # take all the messages in the chat with the given chat_id and user_id
    messages = db.query(models.Message).filter(
        models.Message.chatId == chat_id,
    ).order_by(models.Message.created_at.asc()).all()
    if not messages:
        raise HTTPException(status_code=404, detail="Messages not found")
    return [MessageSchema.model_validate(message) for message in messages]

@router.post("/{user_id}/chat/{chat_id}/message", status_code=status.HTTP_201_CREATED)
async def insert_message(
    chat_id: uuid.UUID, 
    input: MessageInputSchema,
    user: User = Depends(user_exists), 
    db: Session = Depends(get_db)
        ):
    # message of the user in the chat
    user_msg = models.Message(
        messageId = uuid.uuid4(),
        chatId = chat_id,
        userId = user.userId,
        content = input.content,
        chatname = input.chatname,
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
    ai_msg = models.Message(
        messageId=uuid.uuid4(),
        chatId=chat_id,
        userId=None,
        role="assistant",
        content=content_str,
        chatname=input.chatname or "Default Chat",
        created_at=datetime.utcnow()
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {"user": user_msg, "assistant": ai_msg}
