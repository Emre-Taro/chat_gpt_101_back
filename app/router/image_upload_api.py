# File: app/router/image_upload_api.py
from email.mime import image
from unittest import result
import os
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import models
from app.db.models.chat import Chat
from app.db.models.message import Message
from app.schemas.message_schema import MessageSchema, MessageInputSchema
from app.db.models.user import User
from app.auth.utils.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from app.openAPI.openai import generate_openai_response_with_vision, create_vision_message
from app.openAPI.title_generator import generate_title_from_message
from datetime import datetime
from typing import List
import base64
from pydantic import BaseModel

from app.router.chat_api import user_exists

router = APIRouter()
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ImageUpload(BaseModel):
    image_data : str
    chatId: str
    userId: str
    prompt: str = "What do you see in this image?"  # Default prompt for image analysis

@router.post("/{user_id}/{chat_id}/upload_image")
async def upload_image(
    user_id: str,
    chat_id: str,
    image: ImageUpload,
    db: Session = Depends(get_db)
):
    try:
        # Base64データとヘッダーの分離に対応
        if "," in image.image_data:
            header, encoded = image.image_data.split(",", 1)
        else:
            encoded = image.image_data  # ヘッダーなしのケースもサポート

        image_data = base64.b64decode(encoded)

        # Generate a unique filename
        filename = f"{uuid.uuid4()}.png"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save the image
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        # Create user message with image
        user_msg = Message(
            messageId=uuid.uuid4(),
            chatId=chat_id,
            userId=user_id,
            content=image.prompt,  # Use the provided prompt or default
            role="user",
            imageFilename=filename,
            created_at=datetime.utcnow()
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        # Generate AI response using vision capabilities
        vision_message = create_vision_message(
            content=image.prompt,
            image_path=file_path
        )
        
        ai_reply = generate_openai_response_with_vision([vision_message])
        
        if isinstance(ai_reply, dict):
            content_str = json.dumps(ai_reply, ensure_ascii=False)
            print("OpenAI API error:", ai_reply["error"])
        else:
            content_str = ai_reply
            print("OpenAI response:", ai_reply)

        # Save AI response to database
        ai_msg = Message(
            messageId=uuid.uuid4(),
            chatId=chat_id,
            userId=None,
            role="assistant",
            content=content_str,
            created_at=datetime.utcnow()
        )
        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)

        # Generate title for new chat if this is the first message
        existing_messages = db.query(Message).filter_by(chatId=chat_id).count()
        if existing_messages <= 2:  # Only user and assistant messages
            generated_title = f"Image Analysis: {image.prompt[:30]}..."
            chat = db.query(Chat).filter_by(chatId=chat_id).first()
            if chat:
                chat.title = generated_title
                db.commit()

        return {
            "message": "Image uploaded and processed successfully", 
            "file_path": file_path,
            "user_message": user_msg,
            "assistant_message": ai_msg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
