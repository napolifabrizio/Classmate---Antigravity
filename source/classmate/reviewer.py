"""
reviewer.py
-----------
Generates a structured review from a meeting transcript
using the OpenAI GPT-4o model.
"""

import json
from openai import OpenAI

_SYSTEM_PROMPT = """\
You are an expert meeting analyst. You will receive the raw transcript of a meeting.
Your job is to produce a concise, structured review in JSON format with exactly these keys:

{
  "summary": "<2-4 sentence high-level summary of the meeting>",
  "key_points": ["<point 1>", "<point 2>", ...],
  "action_items": ["<action 1>", "<action 2>", ...]
}

Rules:
- Be concise and factual.
- key_points: the most important topics or decisions discussed (3-7 items).
- action_items: concrete tasks that were mentioned or decided (can be empty list if none).
- Return ONLY the raw JSON object — no markdown, no extra text.
"""


def review(transcript: str, client: OpenAI | None = None) -> dict:
    """
    Generate a structured review dict from *transcript* using GPT-4o.

    Parameters
    ----------
    transcript : str
        The full text of the meeting transcript.
    client : OpenAI | None
        Pre-configured OpenAI client. If None, one is created from the
        OPENAI_API_KEY environment variable.

    Returns
    -------
    dict
        A dict with keys: "summary", "key_points", "action_items".
    """
    if client is None:
        client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0.3,
    )

    raw = response.choices[0].message.content
    return json.loads(raw)
