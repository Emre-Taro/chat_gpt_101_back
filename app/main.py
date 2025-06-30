from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.router import auth as auth_router
from app.router import chat_api as chat_router
from app.router import message_api as message_router
from app.router import openai_api as openai_router
from app.auth.utils.security import decode_access_token
from app.db import models
from app.router.auth import get_db, oauth2_scheme
from app.db import models
from app.db.models.user import User



app = FastAPI()
app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(message_router.router)
app.include_router(openai_router.router)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.userId == int(user_id)).first()
    if not user:
        # Avoids leaking information that the user ID was valid but the user is deleted.
        raise credentials_exception
    return user

@app.get("/me")
def read_me(current_user: models.User = Depends(get_current_user)):
    return {"email": current_user.email}
