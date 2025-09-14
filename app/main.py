

# for local
# from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from fastapi import Request
# import os
# from sqlalchemy.orm import Session
# from . import models, schemas, crud, auth
# from .database import engine
# from .deps import get_db, get_current_user
#
# models.Base.metadata.create_all(bind=engine)
# app = FastAPI(title="Notes Summarizer (MSSQL + FastAPI)")
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
# @app.get("/", response_class=HTMLResponse)
# def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})
# @app.post("/signup",response_model=schemas.UserOut)
# def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
#     existing = crud.get_user_by_email(db, user_in.email)
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     user = crud.create_user(db, email=user_in.email, password= user_in.password,role=user_in.role if user_in.role else "AGENT")
#     return user
# @app.post("/login",response_model=schemas.Token)
# def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
#     user = crud.get_user_by_email(db, form_data.email)
#     if not user or not crud.verify_password(form_data.password, user.password_hash):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     token = auth.create_access_token({"sub": str(user.id)})
#     return {"access_token": token, "token_type": "bearer"}
#
#
# @app.post("/notes", response_model=schemas.NoteOut, status_code=201)
# def create_note(note_in: schemas.NoteCreate, db: Session = Depends(get_db),current_user: models.User = Depends(get_current_user)):
#     note = crud.create_note(db, user_id=current_user.id,raw_text=note_in.raw_text)
#     return note
#
# @app.get("/notes", response_model=list[schemas.NoteOut])
# def list_notes(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     return crud.list_notes_for_user(db, current_user.id)
#
# @app.get("/notes/{note_id}", response_model=schemas.NoteOut)
# def get_note(note_id:int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     note = crud.get_note(db, note_id)
#     if not note:
#         raise HTTPException(status_code=404, detail="Note not found")
#     if current_user.role != models.RoleEnum.ADMIN and note.user_id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not Allowed!")
#     return note
#

# for render
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os
from sqlalchemy.orm import Session
from . import models, schemas, crud, auth
from .database import engine, SessionLocal
from .deps import get_db, get_current_user
from .workers import summarize_text_lsa
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes Summarizer (Postgres + FastAPI)")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/signup", response_model=schemas.UserOut)
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(
        db,
        email=user_in.email,
        password=user_in.password,
        role=user_in.role if user_in.role else "AGENT",
    )
    return user


@app.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.email)
    if not user or not crud.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/notes", response_model=schemas.NoteOut, status_code=201)
def create_note(
    note_in: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
):
    note = crud.create_note(db, user_id=current_user.id, raw_text=note_in.raw_text)

    background_tasks.add_task(process_note, note.id)

    return note


@app.get("/notes", response_model=list[schemas.NoteOut])
def list_notes(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.list_notes_for_user(db, current_user.id)


@app.get("/notes/{note_id}", response_model=schemas.NoteOut)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if current_user.role != models.RoleEnum.ADMIN and note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not Allowed!")
    return note


def process_note(note_id: int):
    db = SessionLocal()
    try:
        note = db.query(models.Note).get(note_id)
        if not note:
            return
        summary = summarize_text_lsa(note.raw_text, sentences_count=2)
        crud.set_note_done(db, note.id, summary)
        print(f"[Worker] Note {note.id} processed")
    except Exception as e:
        crud.set_note_failed_and_increment(db, note.id)
        print(f"[Worker] Note {note_id} failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
