# defines the schema for chat response
from pydantic import BaseModel
import uuid
from datetime import datetime

class UserResponse(BaseModel):
    chatId: uuid.UUID
    chatname: str
    userId: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ChatResponse(BaseModel):
    chats: list[UserResponse]

    class Config:
        orm_mode = True  # This allows the model to work with ORM objects