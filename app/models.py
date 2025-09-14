from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    AGENT = "AGENT"

class NoteStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True,index=True)
    email = Column(String(255), unique=True,nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum),default=RoleEnum.AGENT,nullable=False )
    created = Column(DateTime, default=datetime.utcnow)

    notes = relationship("Note",back_populates="owner")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True,index=True)
    user_id = Column(Integer, ForeignKey("user.id"),nullable=False,index=True)
    raw_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(Enum(NoteStatus),default=NoteStatus.QUEUED,nullable=False)
    retries = Column(Integer,default=0)
    max_retries = Column(Integer,default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User",back_populates="notes")





