from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src import schemas
from src.crud import (
    create_note,
    get_notes_list,
    get_note_by_id,
    create_new_note_version,
    restore_deleted_note,
    soft_delete_note,
    get_all_note_versions,
    get_previous_note_version,
    restore_previous_note_version,
)
from src.database import get_postgresql_db
from src.services.ai import get_summary
from src.services.analytics import analyze_note_content

app = FastAPI()


@app.post(
    "/notes/",
    response_model=schemas.NoteDetailResponseSchema,
    status_code=status.HTTP_201_CREATED
)
def create_new_note(
    request: schemas.NoteCreateRequestSchema,
    db: Session = Depends(get_postgresql_db),
):
    return create_note(db=db, note_data=request)


@app.get("/notes/", response_model=list[schemas.NoteResponseSchema])
def get_all_active_notes(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_postgresql_db),
):
    return get_notes_list(db=db, is_deleted=False, skip=skip, limit=limit)


@app.get("/notes/deleted/", response_model=list[schemas.NoteResponseSchema])
def get_all_deleted_notes(
    skip: int = Query(0),
    limit: int = Query(10),
    db: Session = Depends(get_postgresql_db),
):
    return get_notes_list(db=db, is_deleted=True, skip=skip, limit=limit)


@app.get("/notes/{note_id}/", response_model=schemas.NoteDetailResponseSchema)
def get_active_note_by_id(
    note_id: int, db: Session = Depends(get_postgresql_db)
):
    note = get_note_by_id(db=db, note_id=note_id, is_deleted=False)
    if not note:
        raise HTTPException(404, detail="Note not found")
    return note


@app.get(
    "/notes/deleted/{note_id}/",
    response_model=schemas.NoteDetailResponseSchema,
)
def get_deleted_note_by_id(
    note_id: int, db: Session = Depends(get_postgresql_db)
):
    note = get_note_by_id(db=db, note_id=note_id, is_deleted=True)
    if not note:
        raise HTTPException(404, detail="Deleted note not found")
    return note


@app.put(
    "/notes/{note_id}",
    response_model=schemas.NoteDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def update_note(
    note_id: int,
    update_data: schemas.NoteUpdateRequestSchema,
    db: Session = Depends(get_postgresql_db),
):
    return create_new_note_version(
        db=db, note_id=note_id, update_data=update_data
    )


@app.post(
    "/notes/deleted/restore/{note_id}/",
    response_model=schemas.MessageResponseSchema,
)
def restore_note(note_id: int, db: Session = Depends(get_postgresql_db)):
    note = restore_deleted_note(db=db, note_id=note_id)
    return schemas.MessageResponseSchema(
        message=f"Note with ID {note.id} has been restored"
    )


@app.delete("/notes/{note_id}/", response_model=schemas.MessageResponseSchema)
def delete_note(note_id: int, db: Session = Depends(get_postgresql_db)):
    note = soft_delete_note(db=db, note_id=note_id)
    return schemas.MessageResponseSchema(
        message=f"Note with ID {note.id} has been deleted"
    )


@app.get(
    "/notes/history/all/{note_id}/",
    response_model=list[schemas.NoteResponseSchema],
)
def get_note_history(note_id: int, db: Session = Depends(get_postgresql_db)):
    return get_all_note_versions(
        db=db, note=get_note_by_id(db=db, note_id=note_id, is_deleted=False)
    )


@app.get(
    "/notes/history/previous/{note_id}/",
    response_model=schemas.NoteDetailResponseSchema,
)
def get_previous_version(
    note_id: int, db: Session = Depends(get_postgresql_db)
):
    return get_previous_note_version(
        db=db, note=get_note_by_id(db=db, note_id=note_id, is_deleted=False)
    )


@app.post(
    "/notes/history/restore/{note_id}/",
    response_model=schemas.MessageResponseSchema,
)
def restore_previous_version(
    note_id: int, db: Session = Depends(get_postgresql_db)
):
    restore_previous_note_version(db=db, note_id=note_id)

    return schemas.MessageResponseSchema(
        message=f"Previous version of note with ID {note_id} has been restored"
    )


@app.post(
    "/notes/summary/{note_id}/",
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


@app.get("/analytics/notes/", response_model=schemas.NotesAnalyticsSchema)
def get_notes_analytics(db: Session = Depends(get_postgresql_db)):
    return analyze_note_content(db=db)
