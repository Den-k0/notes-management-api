from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from src import schemas
from src.database import get_postgresql_db
from src.services import analyze_note_content

router = APIRouter()


@router.get("/", response_model=schemas.NotesAnalyticsSchema)
def get_notes_analytics(db: Session = Depends(get_postgresql_db)):
    return analyze_note_content(db=db)
