# defines the schema for user creation and token response
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    chat_id: str | None = None