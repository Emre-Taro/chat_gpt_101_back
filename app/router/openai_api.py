# File: app/router/openai_api.py
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import models
from app.schemas import chat_schema
from app.db.models.user import User
from app.auth.utils.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from datetime import datetime

from app.router.chat_api import user_exists

router = APIRouter()