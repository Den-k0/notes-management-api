from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src import schemas
from src.models import Note


# crud
def create_note(db: Session, note_data: schemas.NoteCreateRequestSchema):
    """
    Create a new note in the database.

    Args:
        db (Session): SQLAlchemy database session.
        note_data (schemas.NoteCreateRequestSchema): Data required to create a new note.

    Returns:
        Note: The newly created note object.

    Raises:
        HTTPException: If there is a database error.
    """
    try:
        new_note = Note(title=note_data.title, content=note_data.content)
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return new_note

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))


def get_notes_list(db: Session, is_deleted: bool, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of notes from the database.

    Args:
        db (Session): SQLAlchemy database session.
        is_deleted (bool): Filter for deleted or active notes.
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 10.

    Returns:
        list[Note]: List of notes matching the filter criteria.
    """
    # return db.query(Note).filter(
    #     Note.is_current, Note.is_deleted == is_deleted
    # ).offset(skip).limit(limit).all()
    return db.execute(
        select(Note).where(and_(Note.is_current, Note.is_deleted == is_deleted))
        .offset(skip).limit(limit)
    ).scalars().all()


def get_note_by_id(db: Session, note_id: int, is_deleted: bool):
    """
    Retrieve a note by its ID from the database.
    It returns only active (current) notes by default.

    Args:
        db (Session): SQLAlchemy database session.
        note_id (int): ID of the note to retrieve.
        is_deleted (bool): Filter for deleted or active notes.

    Returns:
        Note: The note object if found, otherwise None.
    """
    # return db.query(Note).filter(
    #     Note.id == note_id, Note.is_current, Note.is_deleted == is_deleted
    # ).first()
    return db.execute(
        select(Note).where(and_(Note.id == note_id, Note.is_current, Note.is_deleted == is_deleted))
    ).scalars().first()


def create_new_note_version(db: Session, note_id: int, update_data: schemas.NoteUpdateRequestSchema):
    """
    Create a new version of an existing note.
    Make the previous version inactive and
    create a new version with the updated data.

    Args:
        db (Session): SQLAlchemy database session.
        note_id (int): ID of the note to update.
        update_data (schemas.NoteUpdateRequestSchema): Data for the updated note.

    Returns:
        Note: The newly created note version.

    Raises:
        HTTPException: If the note is not found or if there is a database error.
    """
    try:
        old_note = get_note_by_id(db=db, note_id=note_id, is_deleted=False)

        if not old_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note with ID {note_id} not found or not the current version"
            )

        old_note.is_current = False

        updated_note = Note(
            title=update_data.title,
            content=update_data.content,
            version=old_note.version + 1,
            previous_version_id=old_note.id,
            is_current=True
        )

        db.add(updated_note)
        db.commit()
        db.refresh(updated_note)
        return updated_note

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))


def restore_deleted_note(db: Session, note_id: int):
    """
    Restore a deleted note by setting its is_deleted flag to False.

    Args:
        db (Session): SQLAlchemy database session.
        note_id (int): ID of the note to restore.

    Returns:
        Note: The restored note object.

    Raises:
        HTTPException: If the note is not found or if there is a database error.
    """
    try:
        note = get_note_by_id(db=db, note_id=note_id, is_deleted=True)

        if not note:
            raise HTTPException(404, detail="Deleted note not found")

        note.is_deleted = False
        db.commit()
        db.refresh(note)
        return note

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))


def soft_delete_note(db: Session, note_id: int):
    """
    Soft delete a note by setting its is_deleted flag to True.

    Args:
        db (Session): SQLAlchemy database session.
        note_id (int): ID of the note to delete.

    Returns:
        Note: The soft-deleted note object.

    Raises:
        HTTPException: If the note is not found or if there is a database error.
    """
    try:
        note = get_note_by_id(db=db, note_id=note_id, is_deleted=False)
        if not note:
            raise HTTPException(404, detail="Note not found")

        note.is_deleted = True
        db.commit()
        db.refresh(note)
        return note

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))


# versions
def get_previous_note_version(db: Session, note: Note):
    """
    Retrieve the previous version of a note from the database.

    Args:
        db (Session): SQLAlchemy database session.
        note (Note): The current note object.

    Returns:
        Note: The previous version of the note if found.

    Raises:
        HTTPException: If no previous version is found.
    """
    if not note.previous_version_id:
        raise HTTPException(404, detail="No previous version found")
    return db.execute(
        select(Note).where(Note.id == note.previous_version_id)
    ).scalars().first()
    # return db.query(Note).filter(Note.id == note.previous_version_id).first()  # sqlalchemy v1


def get_all_note_versions(db: Session, note: Note):
    """
    Retrieve all versions of a note from the database.

    Args:
        db (Session): SQLAlchemy database session.
        note (Note): The current note object.

    Returns:
        list[Note]: A list of all versions of the note, starting from the current version.
    """
    history = []
    current = note

    while current:
        history.append(current)
        if not current.previous_version_id:
            break
        current = get_previous_note_version(db=db, note=current)

    return history


def restore_previous_note_version(db: Session, note_id: int):
    """
    Restore the previous version of a note by making
    the current version inactive (is_current = False)
    and the previous version active (is_current = True).

    Args:
        db (Session): SQLAlchemy database session.
        note_id (int): ID of the note to restore to its previous version.

    Returns:
        Note: The restored previous version of the note.

    Raises:
        HTTPException: If the current or previous version of the note
                       is not found, or if there is a database error.
    """
    try:
        current_note = get_note_by_id(db=db, note_id=note_id, is_deleted=False)
        previous_note = get_previous_note_version(db=db, note=current_note)

        current_note.is_current = False
        previous_note.is_current = True

        db.commit()
        return previous_note

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(500, detail=str(e))
