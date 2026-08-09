from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def semantic_search(query, notes, top_k=5):
    query_embedding = model.encode(query)

    results = []

    for note in notes:
        note_text = f"{note.title} {note.content}"
        note_embedding = model.encode(note_text)

        similarity = cosine_similarity(
            query_embedding,
            note_embedding
        )

        results.append({
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "tag": note.tag,
            "owner_id": note.owner_id,
            "similarity": float(similarity)
        })

    results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return results[:top_k]

