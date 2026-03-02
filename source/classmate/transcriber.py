"""
transcriber.py
--------------
Transcribes an audio file using the OpenAI Whisper API.
"""

from pathlib import Path
from openai import OpenAI


def transcribe(audio_path: str, client: OpenAI | None = None) -> str:
    """
    Send *audio_path* to OpenAI Whisper and return the full transcript text.

    Parameters
    ----------
    audio_path : str
        Absolute or relative path to the audio file
        (supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm).
    client : OpenAI | None
        Pre-configured OpenAI client. If None, one is created from the
        OPENAI_API_KEY environment variable.

    Returns
    -------
    str
        The transcribed text.
    """
    if client is None:
        client = OpenAI()

    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    with open(path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
        )

    return transcription
