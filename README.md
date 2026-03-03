# 🎓 ClassmatePlus

ClassmatePlus is a premium meeting transcription and review tool that leverages OpenAI's Whisper and GPT-4o models to transform raw audio into actionable insights. It captures both your microphone and your computer's system audio, making it perfect for recording virtual meetings, lectures, or interviews.

---

## 🚀 How It Works

ClassmatePlus follows a structured three-step workflow to process your meetings:

### 1. Advanced Audio Capture
The system uses a **dual-channel recording engine** built with `soundcard`.
- **Microphone:** Captures your local voice.
- **System Loopback:** Captures audio coming from your speakers (e.g., other participants in a Zoom/Teams call).
- **Merging:** Both streams are synchronized and merged into a single high-quality 16kHz mono WAV file, optimized for AI transcription.

### 2. AI Transcription (Whisper)
The merged audio is sent to OpenAI's **Whisper-1** model. Whisper provides high-accuracy, multilingual transcription that handles technical jargon and diverse accents with ease.

### 3. Intelligent Review (GPT-4o)
The raw transcript is analyzed by **GPT-4o**, which acts as an expert meeting analyst. It extracts:
- **Executive Summary:** A concise 2-4 sentence overview.
- **Key Points:** The most critical topics and decisions.
- **Action Items:** A checklist of concrete tasks identified during the conversation.

---

## 🛠 Project Structure

- `source/classmate/recorder.py`: Core logic for dual-channel audio capture.
- `source/classmate/transcriber.py`: Interface for OpenAI Whisper transcription.
- `source/classmate/reviewer.py`: GPT-4o logic for meeting analysis and JSON extraction.
- `source/classmate/storage.py`: Handles saving transcripts (TXT) and reviews (MD) to the `data/` directory.
- `source/classmate/tools/`:
    - `main.py`: CLI entry point (Record or Process files).
    - `app.py`: Modern Streamlit web interface.

---

## ⚙️ Setup

1. **Environment:** Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`.
2. **Dependencies:** Ensure you have Python 3.11 and install via Poetry:
   ```bash
   poetry install
   ```

---

## 📖 Usage

### Option A: Streamlit Web UI (Recommended)
Launch the beautiful, interactive dashboard:
```bash
poetry run streamlit run source/classmate/tools/app.py
```

### Option B: Command Line Interface
**Record Live Meeting:**
```bash
poetry run python source/classmate/tools/main.py
```
*Press Enter to stop recording and start processing.*

**Process Existing File:**
```bash
poetry run python source/classmate/tools/main.py path/to/your/audio.mp3
```

---

## 📂 Output
All processed meetings are saved in the `data/` folder with unique timestamps:
- `YYYYMMDD_HHMMSS_transcript.txt`: The full raw text.
- `YYYYMMDD_HHMMSS_review.md`: A beautifully formatted Markdown report.
