from datetime import datetime, timedelta
from jose import jwt
from .config import settings
from .crud import verify_password, get_user_by_email, create_user
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal


ALGORITHM = settings.JWT_ALGORITHMS
SECRET_KEY = settings.JWT_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
