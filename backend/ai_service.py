import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATE = """
Instructions:
Read the note content and generate useful tags and a short summary.

Context:
The note belongs to an internal knowledge-base application used by support engineers.

Input:
{note_content}

Constraints:
Return only a JSON object with exactly two keys:
"tags": a list of 1–3 short lowercase keyword strings.
"summary": one sentence containing at most 20 words.
No text may surround the JSON object.

Output Format:
{{
"tags": ["keyword1", "keyword2"],
"summary": "A short summary of the note."
}}
"""

def get_mock_response(user_message: str) -> str:
    words = user_message.replace(".", "").replace(",", "").split()

    significant_words = []

    for word in words:
        word = word.lower()

        if len(word) >= 4 and word not in significant_words:
            significant_words.append(word)

        if len(significant_words) == 3:
            break

    first_sentence = user_message.split(".")[0].strip()
    summary_words = first_sentence.split()[:20]
    summary = " ".join(summary_words)

    if summary and not summary.endswith("."):
        summary += "."

    return json.dumps({
        "tags": significant_words,
        "summary": summary
    })


def get_ai_response(user_message: str, system_prompt: str) -> str:
    if os.getenv("MOCK_AI") == "1":
        return get_mock_response(user_message)

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"]