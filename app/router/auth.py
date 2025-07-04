# File: app/router/auth.py
# Auth routerfor user regeistration and login
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import models
from app.db.models import user
from app.schemas.user_schema import UserCreate, User
from app.auth.schemas import Token
from app.db.session import SessionLocal
from app.auth.utils.security import get_password_hash, verify_password, create_access_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        username=user.username,
        email=user.email.lower(),
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email_input = form_data.username.lower()
    user = db.query(models.User).filter(models.User.email == email_input).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.userId)})

    first_chat_id = None
    if user.chats and len(user.chats) > 0:
        first_chat_id = str(user.chats[0].chatId)

    print(f"userId: {user.userId}, chats: {user.chats}")

    if user.chats and len(user.chats) > 0:
        print(f"first chatId: {user.chats[0].chatId}")

    return {
        "access_token": access_token,
        "user_id": str(user.userId),
        "chat_id": first_chat_id,
        "token_type": "bearer"
            }
