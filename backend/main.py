import json
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
from backend.ai_service import get_ai_response, PROMPT_TEMPLATE
from backend.algorithms import (
    insertion_sort_by_key,
    binary_search_iterative,
    binary_search_recursive,
    linear_search
)
from backend.semantic_search import semantic_search

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


def build_ai_suggestion(note):
    if not note.ai_tags and not note.ai_summary:
        return None

    tags = []

    if note.ai_tags:
        try:
            tags = json.loads(note.ai_tags)
        except Exception:
            tags = []

    return {
        "tags": tags,
        "summary": note.ai_summary or ""
    }


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

    ai_suggestion = None

    try:
        system_prompt = PROMPT_TEMPLATE.format(
            note_content=note.content
        )

        ai_response = get_ai_response(
            note.content,
            system_prompt
        )

        parsed_response = json.loads(ai_response)

        if (
            isinstance(parsed_response, dict)
            and "tags" in parsed_response
            and "summary" in parsed_response
        ):
            ai_tags = parsed_response["tags"]
            ai_summary = parsed_response["summary"]

            created_note.ai_tags = json.dumps(ai_tags)
            created_note.ai_summary = ai_summary

            db.commit()
            db.refresh(created_note)

            ai_suggestion = {
                "tags": ai_tags,
                "summary": ai_summary
            }

    except Exception as error:
        print(f"AI response parsing failed: {error}")

    background_tasks.add_task(
        run_indexing,
        created_note.id
    )

    return {
        "id": created_note.id,
        "title": created_note.title,
        "content": created_note.content,
        "tag": created_note.tag,
        "owner_id": created_note.owner_id,
        "created_at": created_note.created_at,
        "ai_suggestion": ai_suggestion
    }


@app.get("/notes/search")
def search_notes(
    keyword: str | None = Query(default=None),
    sort_by: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    notes = crud.get_notes(db)

    note_data = [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "created_at": note.created_at,
            "score": 0,
            "created_at_epoch": note.created_at.timestamp()
        }
        for note in notes
    ]

    if keyword:
        keyword_lower = keyword.lower()

        matched_notes = []

        for item in note_data:
            content_lower = item["content"].lower()
            score = content_lower.count(keyword_lower)

            if score > 0:
                item["score"] = score
                matched_notes.append(item)

        ranked_notes = insertion_sort_by_key(
            matched_notes,
            "score"
        )

        return ranked_notes[:5]

    if sort_by == "date":
        return insertion_sort_by_key(
            note_data,
            "created_at_epoch"
        )

    return note_data


@app.get("/notes/lookup")
def lookup_note(
    title: str,
    algo: str = Query(default="iterative"),
    db: Session = Depends(get_db)
):
    if algo not in ["iterative", "recursive"]:
        raise HTTPException(
            status_code=400,
            detail="algo must be iterative or recursive"
        )

    query = db.query(models.Note).order_by(
        models.Note.title.asc()
    )

    sorted_notes = query.all()

    sorted_titles = [
        note.title.lower()
        for note in sorted_notes
    ]

    target = title.lower()

    if algo == "recursive":
        index = binary_search_recursive(
            sorted_titles,
            target,
            0,
            len(sorted_titles) - 1
        )
    else:
        index = binary_search_iterative(
            sorted_titles,
            target
        )

    if index == -1:
        raise HTTPException(
            status_code=404,
            detail="Note title not found"
        )

    note = sorted_notes[index]

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "tag": note.tag,
        "owner_id": note.owner_id,
        "created_at": note.created_at,
        "ai_suggestion": build_ai_suggestion(note)
    }


@app.get("/notes/quick-find")
def quick_find(
    tag: str,
    db: Session = Depends(get_db)
):
    notes = crud.get_notes(
        db,
        tag
    )

    items = [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "created_at": note.created_at,
            "ai_suggestion": build_ai_suggestion(note)
        }
        for note in notes
    ]

    result = linear_search(
        items,
        "tag",
        tag
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No note found for this tag"
        )

    return result


@app.get("/notes/smart-search")
def smart_search(
    q: str = Query(min_length=1),
    db: Session = Depends(get_db)
):
    notes = crud.get_notes(
        db,
        "ai-demo"
    )

    return semantic_search(
        q,
        notes,
        top_k=3
    )


@app.get(
    "/notes",
    response_model=list[schemas.NoteResponse]
)
def get_notes(
    tag: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    notes = crud.get_notes(
        db,
        tag
    )

    return [
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "created_at": note.created_at,
            "ai_suggestion": build_ai_suggestion(note)
        }
        for note in notes
    ]


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

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "tag": note.tag,
        "owner_id": note.owner_id,
        "created_at": note.created_at,
        "ai_suggestion": build_ai_suggestion(note)
    }


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

    return {
        "id": updated_note.id,
        "title": updated_note.title,
        "content": updated_note.content,
        "tag": updated_note.tag,
        "owner_id": updated_note.owner_id,
        "created_at": updated_note.created_at,
        "ai_suggestion": build_ai_suggestion(updated_note)
    }


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

    if not file.filename or not file.filename.lower().endswith(".txt"):
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
