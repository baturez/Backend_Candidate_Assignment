from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[Role] = Role.AGENT

class UserOut(BaseModel):
    id:int
    email: EmailStr
    role: Role
    created: datetime
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class NoteCreate(BaseModel):
    raw_text: str

class NoteOut(BaseModel):
    id: int
    raw_text: str
    summary: Optional[str]
    status: str
    retries: int
    max_retries: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True