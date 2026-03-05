from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .dependencies import get_db, get_current_user

router = APIRouter(
    prefix="/notes",
    tags=["Notes"]
)

@router.post("/")
def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_note = models.Note(
        title=note.title,
        content=note.content,
        user_id=current_user.id
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.get("/")
def get_notes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(models.Note).filter(
        models.Note.user_id == current_user.id
    ).all()


@router.patch("/{note_id}")
def update_note(
    note_id: int,
    note: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == current_user.id
    ).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note


@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_note = db.query(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == current_user.id
    ).first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted"}