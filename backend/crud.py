from sqlalchemy.orm import Session

from backend import models, schemas


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=user.password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_users(db: Session):
    return db.query(models.User).all()


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(
        models.User.id == user_id
    ).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(
        models.User.email == email
    ).first()


def create_note(db: Session, note: schemas.NoteCreate):
    db_note = models.Note(
        title=note.title,
        content=note.content,
        tag=note.tag,
        owner_id=note.owner_id
    )

    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    return db_note


def get_notes(db: Session, tag: str | None = None):
    query = db.query(models.Note)

    if tag:
        query = query.filter(models.Note.tag == tag)

    return query.all()


def get_note(db: Session, note_id: int):
    return db.query(models.Note).filter(
        models.Note.id == note_id
    ).first()


def update_note(
    db: Session,
    note_id: int,
    note: schemas.NoteUpdate
):
    db_note = db.query(models.Note).filter(
        models.Note.id == note_id
    ).first()

    if db_note is None:
        return None

    db_note.title = note.title
    db_note.content = note.content
    db_note.tag = note.tag

    db.commit()
    db.refresh(db_note)

    return db_note


def delete_note(db: Session, note_id: int):
    db_note = db.query(models.Note).filter(
        models.Note.id == note_id
    ).first()

    if db_note is None:
        return None

    db.delete(db_note)
    db.commit()

    return db_note