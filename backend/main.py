import time

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    BackgroundTasks,
    UploadFile,
    File,
    Query,
    Header
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend import models, schemas, crud
from backend.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zomato Notes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def process_time_middleware(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


def check_token(x_token: str | None = Header(default=None)):
    if x_token != "zomato-secret-token":
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token"
        )


def run_indexing(note_id: int):
    time.sleep(2)
    print(f"Indexing completed for note {note_id}")


@app.get("/")
def home():
    return {"message": "Welcome to Zomato Notes!"}


@app.post(
    "/users",
    response_model=schemas.UserResponse
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = crud.get_user_by_email(
        db,
        user.email
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return crud.create_user(db, user)


@app.post(
    "/notes",
    response_model=schemas.NoteResponse
)
def create_note(
    note: schemas.NoteCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    owner = crud.get_user_by_id(
        db,
        note.owner_id
    )

    if owner is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found"
        )

    created_note = crud.create_note(
        db,
        note
    )

    background_tasks.add_task(
        run_indexing,
        created_note.id
    )

    return created_note


@app.get(
    "/notes",
    response_model=list[schemas.NoteResponse]
)
def get_notes(
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    return crud.get_notes(
        db,
        tag
    )


@app.get(
    "/notes/{note_id}",
    response_model=schemas.NoteResponse
)
def get_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    note = crud.get_note(
        db,
        note_id
    )

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return note


@app.put(
    "/notes/{note_id}",
    response_model=schemas.NoteResponse
)
def update_note(
    note_id: int,
    note: schemas.NoteUpdate,
    db: Session = Depends(get_db)
):
    updated_note = crud.update_note(
        db,
        note_id,
        note
    )

    if updated_note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return updated_note


@app.delete(
    "/notes/{note_id}",
    dependencies=[Depends(check_token)]
)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db)
):
    deleted_note = crud.delete_note(
        db,
        note_id
    )

    if deleted_note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    return {
        "message": "Note deleted successfully"
    }


@app.post("/notes/import")
async def import_notes(
    owner_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    owner = crud.get_user_by_id(
        db,
        owner_id
    )

    if owner is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found"
        )

    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are allowed"
        )

    content = await file.read()
    text_content = content.decode("utf-8")

    lines = [
        line.strip()
        for line in text_content.splitlines()
        if line.strip()
    ]

    created_notes = []

    for line in lines:
        note = models.Note(
            title=line[:120],
            content=line,
            tag="imported",
            owner_id=owner_id
        )

        db.add(note)
        created_notes.append(note)

    db.commit()

    for note in created_notes:
        db.refresh(note)

    return {
        "message": "Notes imported successfully",
        "count": len(created_notes)
    }


@app.get("/reports/tag-summary")
def tag_summary(
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT tag, COUNT(*) AS note_count
        FROM notes
        GROUP BY tag
        HAVING COUNT(*) > 1
        ORDER BY note_count DESC
    """)

    result = db.execute(query)

    return [
        {
            "tag": row.tag,
            "note_count": row.note_count
        }
        for row in result
    ]


@app.get("/reports/long-notes")
def long_notes(
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT id, title, content, tag, owner_id
        FROM notes
        WHERE LENGTH(content) > (
            SELECT AVG(LENGTH(content))
            FROM notes
        )
    """)

    result = db.execute(query)

    return [
        {
            "id": row.id,
            "title": row.title,
            "content": row.content,
            "tag": row.tag,
            "owner_id": row.owner_id
        }
        for row in result
    ]


@app.get("/reports/user-notes")
def user_notes(
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT
            users.id,
            users.name,
            users.email,
            COUNT(notes.id) AS note_count
        FROM users
        LEFT JOIN notes
        ON users.id = notes.owner_id
        GROUP BY users.id, users.name, users.email
    """)

    result = db.execute(query)

    return [
        {
            "id": row.id,
            "name": row.name,
            "email": row.email,
            "note_count": row.note_count
        }
        for row in result
    ]

