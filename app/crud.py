from sqlalchemy.orm import Session
from . import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, password: str,role: str="AGENT"):
    hashed_password = pwd_context.hash(password)
    user = models.User(email=email, password_hash=hashed_password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_note(db: Session, user_id:int, raw_text:str):
    note = models.Note(user_id=user_id, raw_text=raw_text)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def get_note(db: Session, note_id:int):
    return db.query(models.Note).filter(models.Note.id == note_id).first()


def list_notes_for_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.role == models.RoleEnum.ADMIN:
        return db.query(models.Note).order_by(models.Note.created_at.desc()).all()
    return db.query(models.Note).filter(models.Note.user_id == user.id).order_by(models.Note.created_at.desc()).all()

def claim_note_for_processing(db: Session, note_id:int):
    res = db.query(models.Note).filter(models.Note.id ==note_id, models.Note.status ==models.NoteStatus.QUEUED).update({"status":models.NoteStatus.PROCESSING},synchronize_session=False
                                                                                                                       )
    db.commit()
    return res

def set_note_done(db: Session, note_id:int,summary:str):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    note.summary = summary
    note.status = models.NoteStatus.DONE
    db.commit()
    db.refresh(note)
    return note



def set_note_failed_and_increment(db: Session, note_id: int):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    note.retries = (note.retries or 0) + 1
    if note.retries >= note.max_retries:
        note.status = models.NoteStatus.FAILED.value
    else:
        note.status = models.NoteStatus.QUEUED.value
    db.commit()
    db.refresh(note)
    return note
