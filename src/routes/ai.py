from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from src import schemas
from src.crud import get_note_by_id
from src.database import get_postgresql_db
from src.services import get_summary

router = APIRouter()


@router.post(
    "/summary/{note_id}/",
    response_model=schemas.NoteDetailResponseSchema,
)
def get_note_summary(note_id: int, db: Session = Depends(get_postgresql_db)):
    note = get_note_by_id(db=db, note_id=note_id, is_deleted=False)
    if not note:
        raise HTTPException(404, detail="Note not found")

    note.summary = get_summary(note.content)

    db.commit()
    db.refresh(note)
    return note
