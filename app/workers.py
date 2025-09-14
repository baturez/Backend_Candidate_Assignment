import time
import traceback
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models, crud
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')
SLEEP_INTERVAL = 3

def summarize_text_lsa(text: str, sentences_count=2) -> str:
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return " ".join(str(sentence) for sentence in summary)

def worker_loop():
    print("Worker started, polling for queued notes...")
    while True:
        db: Session = SessionLocal()
        try:
            note = db.query(models.Note)\
                     .filter(models.Note.status == models.NoteStatus.QUEUED.value)\
                     .order_by(models.Note.created_at)\
                     .first()
            if not note:
                db.close()
                time.sleep(SLEEP_INTERVAL)
                continue

            updated = db.query(models.Note)\
                        .filter(models.Note.id == note.id, models.Note.status == models.NoteStatus.QUEUED.value)\
                        .update({"status": models.NoteStatus.PROCESSING.value}, synchronize_session=False)
            db.commit()

            if updated == 0:
                db.close()
                continue

            note = db.query(models.Note).filter(models.Note.id == note.id).first()

            try:
                summary = summarize_text_lsa(note.raw_text, sentences_count=2)
                crud.set_note_done(db, note.id, summary)
                print(f"Note {note.id} processed -> DONE")

            except Exception as e:
                traceback.print_exc()
                crud.set_note_failed_and_increment(db, note.id)
                print(f"Note {note.id} failed -> error: {e}")

        except Exception as e:
            print("Worker error!", e)
            traceback.print_exc()
        finally:
            db.close()
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    worker_loop()
