const API_URL = "http://127.0.0.1:8000";

let editingNoteId = null;
let allNotes = [];
let searchTimer = null;

async function saveNote() {
    const title = document.getElementById("title").value.trim();
    const content = document.getElementById("content").value.trim();
    const tag = document.getElementById("tag").value.trim();
    const formError = document.getElementById("form-error");

    formError.textContent = "";

    if (title === "" || content === "" || tag === "") {
        formError.textContent = "Please enter title, content, and tag.";
        return;
    }

    try {
        let response;

        if (editingNoteId === null) {
            response = await fetch(API_URL + "/notes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title: title,
                    content: content,
                    tag: tag,
                    owner_id: 1
                })
            });
        } else {
            response = await fetch(API_URL + "/notes/" + editingNoteId, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title: title,
                    content: content,
                    tag: tag
                })
            });
        }

        if (!response.ok) {
            const data = await response.json();
            formError.textContent = data.detail || "Failed to save note.";
            return;
        }

        clearForm();
        await getNotes();

    } catch (error) {
        console.error(error);
        formError.textContent = "Unable to connect to the backend.";
    }
}

async function getNotes() {
    const notesContainer = document.getElementById("notes-container");
    const loadingMessage = document.getElementById("loading-message");
    const errorMessage = document.getElementById("error-message");

    loadingMessage.style.display = "block";
    errorMessage.textContent = "";

    try {
        const response = await fetch(API_URL + "/notes");

        if (!response.ok) {
            throw new Error("Could not get notes");
        }

        const notes = await response.json();

        allNotes = notes;

        loadingMessage.style.display = "none";

        renderNotes(notes);

    } catch (error) {
        console.error(error);

        loadingMessage.style.display = "none";
        errorMessage.textContent = "Unable to connect to the backend.";
    }
}

async function filterByTag() {
    const tag = document.getElementById("tag-filter-input").value.trim();

    if (tag === "") {
        renderNotes(allNotes);
        return;
    }

    const loadingMessage = document.getElementById("loading-message");
    const errorMessage = document.getElementById("error-message");

    loadingMessage.style.display = "block";
    errorMessage.textContent = "";

    try {
        const response = await fetch(
            API_URL + "/notes?tag=" + encodeURIComponent(tag)
        );

        if (!response.ok) {
            throw new Error("Could not filter notes");
        }

        const notes = await response.json();

        loadingMessage.style.display = "none";

        renderNotes(notes);

    } catch (error) {
        console.error(error);

        loadingMessage.style.display = "none";
        errorMessage.textContent = "Unable to filter notes.";
    }
}

function showAllNotes() {
    document.getElementById("tag-filter-input").value = "";
    renderNotes(allNotes);
}

function renderNotes(notes) {
    const notesContainer = document.getElementById("notes-container");

    notesContainer.innerHTML = "";

    if (notes.length === 0) {
        notesContainer.innerHTML = "<p>No notes found.</p>";
        return;
    }

    notes.forEach(function(note) {
        const noteDiv = document.createElement("div");
        noteDiv.className = "note-card";

        const title = document.createElement("h3");
        title.textContent = note.title;

        const content = document.createElement("p");
        content.textContent = note.content;

        const tag = document.createElement("p");
        tag.textContent = "Tag: " + note.tag;

        const editButton = document.createElement("button");
        editButton.textContent = "Edit";

        editButton.addEventListener("click", function() {
            startEdit(
                note.id,
                note.title,
                note.content,
                note.tag
            );
        });

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";

        deleteButton.addEventListener("click", function() {
            deleteNote(note.id);
        });

        noteDiv.appendChild(title);
        noteDiv.appendChild(content);
        noteDiv.appendChild(tag);
        noteDiv.appendChild(editButton);
        noteDiv.appendChild(deleteButton);

        notesContainer.appendChild(noteDiv);
    });
}

function startEdit(id, title, content, tag) {
    editingNoteId = id;

    document.getElementById("title").value = title;
    document.getElementById("content").value = content;
    document.getElementById("tag").value = tag;

    document.getElementById("form-title").textContent = "Edit Note";
    document.getElementById("save-button").textContent = "Update Note";
    document.getElementById("cancel-button").style.display = "inline-block";

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}

function cancelEdit() {
    clearForm();
}

function clearForm() {
    editingNoteId = null;

    document.getElementById("title").value = "";
    document.getElementById("content").value = "";
    document.getElementById("tag").value = "";
    document.getElementById("form-error").textContent = "";

    document.getElementById("form-title").textContent = "Add a Note";
    document.getElementById("save-button").textContent = "Add Note";
    document.getElementById("cancel-button").style.display = "none";
}

async function deleteNote(id) {
    const errorMessage = document.getElementById("error-message");

    try {
        const response = await fetch(API_URL + "/notes/" + id, {
            method: "DELETE",
            headers: {
                "X-Token": "zomato-secret-token"
            }
        });

        if (!response.ok) {
            const data = await response.json();
            errorMessage.textContent =
                data.detail || "Failed to delete note.";
            return;
        }

        await getNotes();

    } catch (error) {
        console.error(error);
        errorMessage.textContent =
            "Unable to connect to the backend.";
    }
}

function searchNotes() {
    const searchValue =
        document.getElementById("search-input")
        .value
        .trim()
        .toLowerCase();

    if (searchValue === "") {
        renderNotes(allNotes);
        return;
    }

    const filteredNotes = allNotes.filter(function(note) {
        return (
            note.title.toLowerCase().includes(searchValue) ||
            note.content.toLowerCase().includes(searchValue) ||
            note.tag.toLowerCase().includes(searchValue)
        );
    });

    renderNotes(filteredNotes);
}

document
    .getElementById("save-button")
    .addEventListener("click", saveNote);

document
    .getElementById("cancel-button")
    .addEventListener("click", cancelEdit);

document
    .getElementById("refresh-button")
    .addEventListener("click", getNotes);

document
    .getElementById("tag-filter-button")
    .addEventListener("click", filterByTag);

document
    .getElementById("show-all-button")
    .addEventListener("click", showAllNotes);

document
    .getElementById("search-input")
    .addEventListener("input", function() {

        clearTimeout(searchTimer);

        searchTimer = setTimeout(function() {
            searchNotes();
        }, 400);
    });

getNotes();