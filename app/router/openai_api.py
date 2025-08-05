# File: app/router/message_api.py
from unittest import result
import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.db import models
from app.schemas.message_schema import MessageSchema, MessageInputSchema
from app.db.models.user import User
from app.auth.utils.security import get_password_hash, verify_password, create_access_token
from app.db.session import get_db
from app.openAPI.openai import generate_openai_response
from app.openAPI.title_generator import generate_title_from_message
from datetime import datetime
from typing import List

from app.router.chat_api import user_exists

router = APIRouter()