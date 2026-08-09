const API_BASE_URL = "http://127.0.0.1:8000";

const DELETE_TOKEN = "zomato-secret-token";

const CATEGORY_TREE = {
    name: "All Tags",
    children: [
        {
            name: "Work",
            children: [
                {
                    name: "Standups",
                    children: []
                },
                {
                    name: "Retros",
                    children: []
                }
            ]
        },
        {
            name: "Personal",
            children: [
                {
                    name: "Health",
                    children: [
                        {
                            name: "Fitness",
                            children: []
                        }
                    ]
                },
                {
                    name: "Recipes",
                    children: []
                }
            ]
        },
        {
            name: "Travel",
            children: []
        }
    ]
};

const quickTags = [
    "work",
    "health",
    "recipes",
    "travel",
    "random"
];

let notes = [];
let searchTimeout = null;
let editingNoteId = null;

const noteForm = document.getElementById("note-form");
const titleInput = document.getElementById("title");
const contentInput = document.getElementById("content");
const tagInput = document.getElementById("tag");
const ownerIdInput = document.getElementById("owner-id");

const formTitle = document.getElementById("form-title");
const formError = document.getElementById("form-error");
const saveButton = document.getElementById("save-button");
const cancelButton = document.getElementById("cancel-button");

const notesContainer = document.getElementById("notes-container");
const loadingMessage = document.getElementById("loading-message");
const errorMessage = document.getElementById("error-message");
const searchMessage = document.getElementById("search-message");

const searchInput = document.getElementById("search-input");
const sortSelect = document.getElementById("sort-select");

const refreshButton = document.getElementById("refresh-button");

const tagFilterInput = document.getElementById("tag-filter-input");
const tagFilterButton = document.getElementById("tag-filter-button");
const showAllButton = document.getElementById("show-all-button");

const exactTitleInput = document.getElementById("exact-title-input");
const binaryAlgorithm = document.getElementById("binary-algorithm");
const exactTitleButton = document.getElementById("exact-title-button");

const quickTagButtons = document.getElementById("quick-tag-buttons");

const categoryTreeContainer = document.getElementById("category-tree");

const smartSearchInput = document.getElementById("smart-search-input");
const smartSearchButton = document.getElementById("smart-search-button");
const smartSearchResults = document.getElementById("smart-search-results");
const smartSearchError = document.getElementById("smart-search-error");

async function fetchNotes(tag = "") {
    let url = `${API_BASE_URL}/notes`;

    if (tag) {
        url += `?tag=${encodeURIComponent(tag)}`;
    }

    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`Failed to fetch notes: ${response.status}`);
    }

    return await response.json();
}

async function createNote(noteData) {
    const response = await fetch(`${API_BASE_URL}/notes`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(noteData)
    });

    if (!response.ok) {
        let errorMessageText = "Failed to create note";

        try {
            const errorData = await response.json();
            errorMessageText = errorData.detail || errorMessageText;
        } catch (error) {
            errorMessageText = `Failed to create note: ${response.status}`;
        }

        throw new Error(errorMessageText);
    }

    return await response.json();
}

async function updateNote(id, noteData) {
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(noteData)
    });

    if (!response.ok) {
        let errorMessageText = "Failed to update note";

        try {
            const errorData = await response.json();
            errorMessageText = errorData.detail || errorMessageText;
        } catch (error) {
            errorMessageText = `Failed to update note: ${response.status}`;
        }

        throw new Error(errorMessageText);
    }

    return await response.json();
}

async function deleteNote(id) {
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
        method: "DELETE",
        headers: {
            "x-token": DELETE_TOKEN
        }
    });

    if (!response.ok) {
        let errorMessageText = "Failed to delete note";

        try {
            const errorData = await response.json();
            errorMessageText = errorData.detail || errorMessageText;
        } catch (error) {
            errorMessageText = `Failed to delete note: ${response.status}`;
        }

        throw new Error(errorMessageText);
    }

    return await response.json();
}

function clearMessages() {
    formError.textContent = "";
    errorMessage.textContent = "";
    searchMessage.textContent = "";
}

function validateNoteForm() {
    const title = titleInput.value.trim();
    const content = contentInput.value.trim();
    const tag = tagInput.value.trim();
    const ownerId = ownerIdInput.value.trim();

    if (!title) {
        formError.textContent = "Title cannot be empty.";
        return false;
    }

    if (!content) {
        formError.textContent = "Content cannot be empty.";
        return false;
    }

    if (!tag) {
        formError.textContent = "Tag cannot be empty.";
        return false;
    }

    if (!ownerId || Number(ownerId) < 1) {
        formError.textContent = "Please enter a valid owner ID.";
        return false;
    }

    if (title.length > 120) {
        formError.textContent = "Title must not exceed 120 characters.";
        return false;
    }

    return true;
}

function createNoteCard(note) {
    const card = document.createElement("article");
    card.className = "note-card";
    card.dataset.noteId = note.id;

    const idText = document.createElement("p");
    idText.className = "note-id";
    idText.textContent = `Note ID: ${note.id}`;

    const title = document.createElement("h3");
    title.textContent = note.title;

    const content = document.createElement("p");
    content.textContent = note.content;

    const tag = document.createElement("span");
    tag.className = "note-tag";
    tag.textContent = note.tag;

    const owner = document.createElement("p");
    owner.textContent = `Owner ID: ${note.owner_id}`;

    const actions = document.createElement("div");
    actions.className = "note-actions";

    const editButton = document.createElement("button");
    editButton.className = "edit-button";
    editButton.textContent = "Edit";
    editButton.type = "button";

    editButton.addEventListener("click", () => {
        startEditing(note);
    });

    const deleteButton = document.createElement("button");
    deleteButton.className = "delete-button";
    deleteButton.textContent = "Delete";
    deleteButton.type = "button";

    deleteButton.addEventListener("click", async () => {
        await handleDelete(note.id, card);
    });

    actions.appendChild(editButton);
    actions.appendChild(deleteButton);

    card.appendChild(idText);
    card.appendChild(title);
    card.appendChild(content);
    card.appendChild(tag);
    card.appendChild(owner);
    card.appendChild(actions);

    if (
        note.ai_suggestion &&
        Array.isArray(note.ai_suggestion.tags) &&
        typeof note.ai_suggestion.summary === "string"
    ) {
        addAISuggestion(card, note);
    }

    return card;
}

function addAISuggestion(card, note) {
    const panel = document.createElement("div");
    panel.className = "ai-panel";

    const heading = document.createElement("h4");
    heading.textContent = "AI Suggests";

    const tagsTitle = document.createElement("p");
    tagsTitle.textContent = "Suggested Tags:";

    const tagsContainer = document.createElement("div");
    tagsContainer.className = "ai-tags";

    note.ai_suggestion.tags.forEach((suggestedTag) => {
        const tag = document.createElement("span");
        tag.className = "ai-tag";
        tag.textContent = suggestedTag;
        tagsContainer.appendChild(tag);
    });

    const summary = document.createElement("p");
    summary.textContent = `Summary: ${note.ai_suggestion.summary}`;

    const applyButton = document.createElement("button");
    applyButton.className = "apply-tag-button";
    applyButton.type = "button";
    applyButton.textContent = "Apply as tag";

    applyButton.addEventListener("click", async () => {
        if (
            !note.ai_suggestion ||
            !Array.isArray(note.ai_suggestion.tags) ||
            note.ai_suggestion.tags.length === 0
        ) {
            return;
        }

        const suggestedTag = note.ai_suggestion.tags[0];

        applyButton.disabled = true;

        try {
            const updated = await updateNote(note.id, {
                title: note.title,
                content: note.content,
                tag: suggestedTag
            });

            notes = notes.map((existingNote) => {
                if (existingNote.id === note.id) {
                    return {
                        ...existingNote,
                        tag: updated.tag
                    };
                }

                return existingNote;
            });

            renderNotes(notes);
            searchMessage.textContent =
                `Applied AI tag "${suggestedTag}" to note ${note.id}.`;
        } catch (error) {
            errorMessage.textContent = error.message;
            applyButton.disabled = false;
        }
    });

    panel.appendChild(heading);
    panel.appendChild(tagsTitle);
    panel.appendChild(tagsContainer);
    panel.appendChild(summary);
    panel.appendChild(applyButton);

    card.appendChild(panel);
}

function renderNotes(notesToRender) {
    notesContainer.innerHTML = "";

    if (notesToRender.length === 0) {
        const emptyMessage = document.createElement("p");
        emptyMessage.textContent = "No notes found.";
        notesContainer.appendChild(emptyMessage);
        return;
    }

    notesToRender.forEach((note) => {
        const card = createNoteCard(note);
        notesContainer.appendChild(card);
    });
}

async function loadNotes(tag = "") {
    loadingMessage.style.display = "block";
    errorMessage.textContent = "";

    try {
        notes = await fetchNotes(tag);
        renderNotes(notes);
    } catch (error) {
        errorMessage.textContent = error.message;
        notesContainer.innerHTML = "";
    } finally {
        loadingMessage.style.display = "none";
    }
}

async function handleDelete(id, card) {
    try {
        await deleteNote(id);
        card.remove();
        notes = notes.filter((note) => note.id !== id);
    } catch (error) {
        errorMessage.textContent = error.message;
    }
}

function startEditing(note) {
    editingNoteId = note.id;

    formTitle.textContent = "Edit Note";
    saveButton.textContent = "Update Note";
    cancelButton.classList.remove("hidden");

    titleInput.value = note.title;
    contentInput.value = note.content;
    tagInput.value = note.tag;
    ownerIdInput.value = note.owner_id;

    document.getElementById("add-note").scrollIntoView({
        behavior: "smooth"
    });
}

function cancelEditing() {
    editingNoteId = null;

    formTitle.textContent = "Add a Note";
    saveButton.textContent = "Add Note";
    cancelButton.classList.add("hidden");

    noteForm.reset();
    ownerIdInput.value = "1";
    formError.textContent = "";
}

async function handleFormSubmit(event) {
    event.preventDefault();

    formError.textContent = "";
    searchMessage.textContent = "";

    if (!validateNoteForm()) {
        return;
    }

    const noteData = {
        title: titleInput.value.trim(),
        content: contentInput.value.trim(),
        tag: tagInput.value.trim(),
        owner_id: Number(ownerIdInput.value)
    };

    saveButton.disabled = true;

    try {
        if (editingNoteId === null) {
            const createdNote = await createNote(noteData);

            notes.push(createdNote);
            renderNotes(notes);

            if (
                createdNote.ai_suggestion &&
                Array.isArray(createdNote.ai_suggestion.tags)
            ) {
                searchMessage.textContent =
                    "Note created successfully with AI suggestions.";
            } else {
                searchMessage.textContent =
                    "Note created successfully. No AI suggestion was returned.";
            }

            cancelEditing();
        } else {
            const updatedNote = await updateNote(
                editingNoteId,
                {
                    title: noteData.title,
                    content: noteData.content,
                    tag: noteData.tag
                }
            );

            notes = notes.map((note) =>
                note.id === editingNoteId ? updatedNote : note
            );

            renderNotes(notes);

            searchMessage.textContent = "Note updated successfully.";

            cancelEditing();
        }
    } catch (error) {
        formError.textContent = error.message;
    } finally {
        saveButton.disabled = false;
    }
}

function renderCategoryTree(tree, parentElement) {
    const list = document.createElement("ul");

    const item = document.createElement("li");

    const node = document.createElement("span");
    node.className = "category-node";
    node.textContent = tree.name;

    item.appendChild(node);

    if (tree.children && tree.children.length > 0) {
        const childrenContainer = document.createElement("div");
        childrenContainer.className = "category-children";

        tree.children.forEach((child) => {
            renderCategoryTree(child, childrenContainer);
        });

        node.addEventListener("click", () => {
            childrenContainer.classList.toggle("collapsed");
        });

        item.appendChild(childrenContainer);
    }

    list.appendChild(item);
    parentElement.appendChild(list);
}

function renderQuickTagButtons() {
    quickTagButtons.innerHTML = "";

    quickTags.forEach((tag) => {
        const button = document.createElement("button");

        button.type = "button";
        button.className = "quick-tag-button";
        button.textContent = tag;

        button.addEventListener("click", () => {
            quickFindTag(tag);
        });

        quickTagButtons.appendChild(button);
    });
}

function filterLocalNotes(value) {
    const searchValue = value.trim().toLowerCase();

    if (!searchValue) {
        renderNotes(notes);
        return;
    }

    const filtered = notes.filter((note) => {
        return (
            note.title.toLowerCase().includes(searchValue) ||
            note.content.toLowerCase().includes(searchValue) ||
            note.tag.toLowerCase().includes(searchValue)
        );
    });

    renderNotes(filtered);
}

async function performRankedSearch() {
    const keyword = searchInput.value.trim();

    if (!keyword) {
        renderNotes(notes);
        searchMessage.textContent = "";
        return;
    }

    const sortBy = sortSelect.value;

    try {
        const params = new URLSearchParams();

        if (sortBy === "date") {
            params.set("sort_by", "date");
        } else {
            params.set("keyword", keyword);
        }

        const response = await fetch(
            `${API_BASE_URL}/notes/search?${params.toString()}`
        );

        if (!response.ok) {
            throw new Error(`Search failed: ${response.status}`);
        }

        const results = await response.json();

        renderNotes(results);
        searchMessage.textContent = `Found ${results.length} result(s).`;
    } catch (error) {
        filterLocalNotes(keyword);
        searchMessage.textContent =
            "Backend ranked search is not available yet.";
    }
}

async function performTagFilter() {
    const tag = tagFilterInput.value.trim();

    if (!tag) {
        await loadNotes();
        return;
    }

    await loadNotes(tag);
}

async function performExactTitleSearch() {
    const title = exactTitleInput.value.trim();

    if (!title) {
        searchMessage.textContent = "Enter an exact title.";
        return;
    }

    const algorithm = binaryAlgorithm.value;

    try {
        const params = new URLSearchParams({
            title,
            algo: algorithm
        });

        const response = await fetch(
            `${API_BASE_URL}/notes/lookup?${params.toString()}`
        );

        if (!response.ok) {
            if (response.status === 404) {
                searchMessage.textContent = "Note title not found.";
                return;
            }

            throw new Error(`Lookup failed: ${response.status}`);
        }

        const result = await response.json();

        renderNotes([result]);

        const card = document.querySelector(
            `.note-card[data-note-id="${result.id}"]`
        );

        if (card) {
            card.classList.add("quick-highlight");

            setTimeout(() => {
                card.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
            }, 100);
        }
    } catch (error) {
        const localResult = notes.find(
            (note) => note.title === title
        );

        if (localResult) {
            renderNotes([localResult]);
            searchMessage.textContent = "Exact title found.";
        } else {
            searchMessage.textContent = error.message;
        }
    }
}

async function quickFindTag(tag) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/notes/quick-find?tag=${encodeURIComponent(tag)}`
        );

        if (!response.ok) {
            if (response.status === 404) {
                searchMessage.textContent =
                    `No note found for tag: ${tag}`;
                return;
            }

            throw new Error(`Quick find failed: ${response.status}`);
        }

        const result = await response.json();

        renderNotes([result]);

        const card = document.querySelector(
            `.note-card[data-note-id="${result.id}"]`
        );

        if (card) {
            card.classList.add("quick-highlight");

            card.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
        }
    } catch (error) {
        const localResult = notes.find(
            (note) => note.tag.toLowerCase() === tag.toLowerCase()
        );

        if (localResult) {
            renderNotes([localResult]);
            searchMessage.textContent =
                `Found first note with tag: ${tag}`;
        } else {
            searchMessage.textContent = error.message;
        }
    }
}

async function performSmartSearch() {
    const query = smartSearchInput.value.trim();

    smartSearchError.textContent = "";
    smartSearchResults.innerHTML = "";

    if (!query) {
        smartSearchError.textContent = "Enter a search query.";
        return;
    }

    smartSearchButton.disabled = true;

    try {
        const response = await fetch(
            `${API_BASE_URL}/notes/smart-search?q=${encodeURIComponent(query)}`
        );

        if (!response.ok) {
            throw new Error(`Smart Search failed: ${response.status}`);
        }

        const results = await response.json();

        renderSmartResults(results);
    } catch (error) {
        smartSearchError.textContent = error.message;
    } finally {
        smartSearchButton.disabled = false;
    }
}

function renderSmartResults(results) {
    smartSearchResults.innerHTML = "";

    if (!results.length) {
        const message = document.createElement("p");
        message.textContent = "No semantic results found.";
        smartSearchResults.appendChild(message);
        return;
    }

    results.forEach((result) => {
        const card = document.createElement("article");
        card.className = "smart-result";

        const title = document.createElement("h3");
        title.textContent = result.title;

        const content = document.createElement("p");
        content.textContent = result.content;

        const score = document.createElement("p");
        score.className = "similarity-score";
        score.textContent =
            `Similarity: ${Number(result.similarity).toFixed(4)}`;

        card.appendChild(title);
        card.appendChild(content);
        card.appendChild(score);

        smartSearchResults.appendChild(card);
    });
}

noteForm.addEventListener("submit", handleFormSubmit);

cancelButton.addEventListener("click", cancelEditing);

refreshButton.addEventListener("click", () => {
    loadNotes();
});

tagFilterButton.addEventListener("click", () => {
    performTagFilter();
});

showAllButton.addEventListener("click", () => {
    tagFilterInput.value = "";
    loadNotes();
});

searchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);

    searchTimeout = setTimeout(() => {
        performRankedSearch();
    }, 400);
});

sortSelect.addEventListener("change", () => {
    if (searchInput.value.trim()) {
        performRankedSearch();
    }
});

exactTitleButton.addEventListener("click", () => {
    performExactTitleSearch();
});

smartSearchButton.addEventListener("click", () => {
    performSmartSearch();
});

smartSearchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        performSmartSearch();
    }
});

renderCategoryTree(CATEGORY_TREE, categoryTreeContainer);
renderQuickTagButtons();
loadNotes();

