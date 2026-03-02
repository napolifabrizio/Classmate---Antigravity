# ClassmatePlus

Meeting transcription and review tool powered by OpenAI Whisper and GPT-4o.

## Setup

1. Copy `.env.example` to `.env` and add your OpenAI API key.
2. Install dependencies: `poetry install`

## Usage

```bash
poetry run python source/classmate/tools/main.py path/to/audio.mp3
```

Results are saved in the `data/` folder.
