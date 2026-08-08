# Zomato Notes

A full-stack notes application built with FastAPI, SQLAlchemy, SQLite, HTML, CSS, and JavaScript.

## Features
- Create users
- Create notes
- View all notes
- Filter notes by tag
- View individual notes
- Update notes
- Delete notes with token protection
- Import notes from a .txt file
- Background indexing task
- Tag summary report
- Long notes report
- User notes report
- Frontend connected to the FastAPI backend

## Technologies Used
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- HTML
- CSS
- JavaScript
- Git
- GitHub

## Project Structure
zomato-notes/
+-- backend/
¦   +-- __init__.py
¦   +-- main.py
¦   +-- database.py
¦   +-- models.py
¦   +-- schemas.py
¦   +-- crud.py
¦   +-- seed.py
+-- frontend/
¦   +-- index.html
¦   +-- script.js
¦   +-- style.css
+-- sample_import.txt
+-- .gitignore
+-- README.md

## Running the Project

### 1. Activate the virtual environment

venv\Scripts\activate

### 2. Start the FastAPI server

uvicorn backend.main:app --reload

### 3. Open the API documentation

http://127.0.0.1:8000/docs

### 4. Open the frontend

http://127.0.0.1:5500/frontend/index.html

## API Endpoints

### Users
- POST /users

### Notes
- POST /notes
- GET /notes
- GET /notes/{note_id}
- PUT /notes/{note_id}
- DELETE /notes/{note_id}

### Import
- POST /notes/import

### Reports
- GET /reports/tag-summary
- GET /reports/long-notes
- GET /reports/user-notes

## GitHub

This project is maintained using Git and GitHub.
