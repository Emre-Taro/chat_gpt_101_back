from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class MessageSchema(BaseModel):
    messageId: UUID
    chatId: UUID
    userId: UUID | None
    content: str
    role: str 
    chatname: str | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MessageInputSchema(BaseModel):
    chatId: UUID
    userId: UUID
    content: str
    chatname: str | None = None
    role: str

    class Config:
        from_attributes = True
        orm_mode = True  # This allows the model to work with ORM objects directly