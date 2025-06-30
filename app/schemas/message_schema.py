from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class MessageSchema(BaseModel):
    messageId: UUID
    chatId: UUID
    userId: UUID
    content: str
    chatname: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True