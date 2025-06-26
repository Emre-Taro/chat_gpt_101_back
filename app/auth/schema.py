# defines the schema for user creation and token response
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
