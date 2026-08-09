# Zomato Notes

Zomato Notes is a full-stack internal notes and knowledge-base application built with FastAPI, SQLAlchemy, SQLite, HTML, CSS, and JavaScript.

The project includes a Core Notes App, a Ranking Engine using explicit search and sorting algorithms, and an Intelligence Layer using semantic search and AI-assisted note suggestions.

## Features

### Core Notes App

- Create users
- Create notes
- View all notes
- View individual notes
- Update notes
- Delete notes with token protection
- Filter notes by tag
- Import notes from a .txt file
- Background indexing task
- Tag summary report
- Long notes report
- User notes report
- Frontend connected to the FastAPI backend
- Responsive frontend interface

### Ranking Engine

- Insertion sort by numeric key
- Iterative binary search
- Recursive binary search
- Linear search
- Keyword ranked search
- Date sorting
- Exact title lookup
- Quick tag lookup
- Recursive category tree
- Debounced search with a 400 ms delay
- Quick Tag Jump controls

### Intelligence Layer

- Semantic Smart Search
- Cosine similarity ranking
- Sentence Transformers embeddings
- `sentence-transformers/all-MiniLM-L6-v2`
- AI tag suggestions
- AI-generated note summaries
- Apply suggested AI tags
- Mock AI mode for local demonstration
- AI sample notes for testing

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- NumPy
- Sentence Transformers
- HTML
- CSS
- JavaScript
- Git
- GitHub

## Project Structure

zomato-notes/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── seed.py
│   ├── algorithms.py
│   ├── ranking_dataset.py
│   ├── semantic_search.py
│   └── ai_service.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── sample_import.txt
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt

## Installation

### 1. Create and activate the virtual environment

Windows:

venv\Scripts\activate

### 2. Install dependencies

pip install -r requirements.txt

## Environment Configuration

Create a `.env` file based on `.env.example`.

Example:

MOCK_AI=1
OPENAI_API_KEY=

Do not commit the `.env` file to GitHub.

## Seed the Database

Run:

python -m backend.seed

This creates the sample users and notes required for testing the application.

## Running the Project

Start the FastAPI server:

uvicorn backend.main:app --reload

## API Documentation

Open:

http://127.0.0.1:8000/docs

## Frontend

Open:

http://127.0.0.1:5500/frontend/index.html

The frontend communicates with the FastAPI backend.

## Main API Endpoints

### Users

- POST /users
- GET /users

### Notes

- POST /notes
- GET /notes
- GET /notes/{note_id}
- PUT /notes/{note_id}
- DELETE /notes/{note_id}

### Search and Ranking

- GET /notes/search
- GET /notes/lookup
- GET /notes/quick-find

### Semantic Search

- GET /notes/smart-search

### Import

- POST /notes/import

### Reports

- GET /reports/tag-summary
- GET /reports/long-notes
- GET /reports/user-notes

## Algorithms

The Ranking Engine implements the required algorithms directly in Python:

- Insertion sort
- Iterative binary search
- Recursive binary search
- Linear search

The algorithms are integrated into the FastAPI search and lookup endpoints.

## Smart Search

Smart Search uses Sentence Transformers to convert the query and notes into embeddings and compares them using cosine similarity.

The project uses:

sentence-transformers/all-MiniLM-L6-v2

The semantic search returns the most relevant notes based on similarity.

## AI Assistance

The application provides lightweight AI assistance for notes:

- Suggested tags
- Short summaries
- Apply suggested tags

The project supports mock AI mode for local demonstration without requiring an external API key.

## GitHub

This project is maintained using Git and GitHub.