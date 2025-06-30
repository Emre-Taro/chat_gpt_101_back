# defines the schema for user
from pydantic import BaseModel
import uuid
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class User(BaseModel):
    userId: uuid.UUID
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True  # This allows the model to work with ORM objects