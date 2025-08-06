# File: app/router/image_upload_api.py
import os
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from app.db.models.chat import Chat
from app.db.models.message import Message
from app.db.models.user import User
from app.db.session import get_db
from app.openAPI.openai import generate_openai_response_with_vision, create_vision_message
from app.openAPI.title_generator import generate_title_from_message
from datetime import datetime
from typing import List
import base64
from pydantic import BaseModel

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed image file types
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

class ImageUpload(BaseModel):
    image_data: str
    chatId: str
    userId: str
    prompt: str = "What do you see in this image?"  # Default prompt for image analysis

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

@router.post("/{user_id}/{chat_id}/upload_image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    user_id: str,
    chat_id: str,
    file: UploadFile = File(...),
    prompt: str = Form("What do you see in this image?"),
    user: User = Depends(get_user_dependency),
    db: Session = Depends(get_db)    
):
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Validate file size (max 10MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File size too large. Maximum size is 10MB")
        
        # Convert string IDs to UUID
        try:
            user_uuid = uuid.UUID(user_id)
            chat_uuid = uuid.UUID(chat_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Verify user owns the chat
        chat = db.query(Chat).filter_by(chatId=chat_uuid, userId=user_uuid).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found or access denied")
        
        # Save the uploaded file
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Create user message with image
        user_msg = Message(
            messageId=uuid.uuid4(),
            chatId=chat_uuid,
            userId=user_uuid,
            content=prompt,  # Use the provided prompt
            role="user",
            imageFilename=filename,
            created_at=datetime.utcnow()
        )
        db.add(user_msg)
        db.commit()
        db.refresh(user_msg)

        # Generate AI response using vision capabilities
        vision_message = create_vision_message(
            content=prompt,
            image_path=file_path
        )
        
        if isinstance(vision_message, dict) and "error" in vision_message:
            raise HTTPException(status_code=500, detail=f"Error creating vision message: {vision_message['error']}")
        
        ai_reply = generate_openai_response_with_vision([vision_message])
        
        if isinstance(ai_reply, dict) and "error" in ai_reply:
            content_str = json.dumps(ai_reply, ensure_ascii=False)
            print("OpenAI API error:", ai_reply["error"])
            # Still save the error message to database for debugging
        else:
            content_str = ai_reply
            print("OpenAI response:", ai_reply)

        # Save AI response to database
        ai_msg = Message(
            messageId=uuid.uuid4(),
            chatId=chat_uuid,
            userId=None,
            role="assistant",
            content=content_str,
            created_at=datetime.utcnow()
        )
        db.add(ai_msg)
        db.commit()
        db.refresh(ai_msg)

        # Generate title for new chat if this is the first message
        existing_messages = db.query(Message).filter_by(chatId=chat_uuid).count()
        if existing_messages <= 2:  # Only user and assistant messages
            generated_title = f"Image Analysis: {prompt[:30]}..."
            chat.title = generated_title
            db.commit()

        return {
            "message": "Image uploaded and processed successfully", 
            "file_path": file_path,
            "user_message": user_msg,
            "assistant_message": ai_msg
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
    