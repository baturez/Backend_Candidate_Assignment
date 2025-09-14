from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
from sqlalchemy.orm import Session
from . import models, schemas, crud, auth
from .database import engine
from .deps import get_db, get_current_user
import threading
from app.workers import worker_loop
import uvicorn

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="Notes Summarizer (MSSQL + FastAPI)")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/signup",response_model=schemas.UserOut)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, email=user_in.email, password= user_in.password,role=user_in.role if user_in.role else "AGENT")
    return user
@app.post("/login",response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.email)
    if not user or not crud.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/notes", response_model=schemas.NoteOut, status_code=201)
def create_note(note_in: schemas.NoteCreate, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
    note = crud.create_note(db, user_id=current_user.id,raw_text=note_in.raw_text)
    return note

@app.get("/notes", response_model=list[schemas.NoteOut])
def list_notes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.list_notes_for_user(db, current_user.id)

@app.get("/notes/{note_id}", response_model=schemas.NoteOut)
def get_note(note_id:int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if current_user.role != models.RoleEnum.ADMIN and note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not Allowed!")
    return note

def start_worker():
    t = threading.Thread(target=worker_loop, daemon=True)
    t.start()

if __name__ == "__main__":
    # Start background worker in separate thread
    start_worker()
    # Run API
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)