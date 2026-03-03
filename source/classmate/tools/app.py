import streamlit as st
import os
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Add source to path
_SOURCE_DIR = Path(__file__).resolve().parents[2]
if str(_SOURCE_DIR) not in sys.path:
    sys.path.append(str(_SOURCE_DIR))

from classmate.transcriber import transcribe
from classmate.reviewer import review
from classmate.storage import save, format_review
from datetime import datetime
from streamlit_mic_recorder import mic_recorder

# Load environment variables
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(_PROJECT_ROOT / ".env")

# Page Configuration
st.set_page_config(
    page_title="ClassmatePlus",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a premium look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #262730;
        color: white;
        border: 1px solid #4a4a4a;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff4b4b;
        border-color: #ff4b4b;
    }
    .stTextInput>div>div>input {
        background-color: #262730;
        color: white;
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e1e1e;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'review' not in st.session_state:
    st.session_state.review = None

def process_audio(audio_path, delete_after=False):
    client = OpenAI()
    
    with st.status("Processing meeting...", expanded=True) as status:
        st.write("Transcribing audio...")
        transcript = transcribe(audio_path, client=client)
        st.session_state.transcript = transcript
        
        st.write("Analyzing content...")
        meeting_review = review(transcript, client=client)
        st.session_state.review = meeting_review
        
        st.write("Review complete!")
        # We don't save to the data/ folder if running in Streamlit
        # transcript_path, review_path = save(transcript, meeting_review, audio_path)
        
        status.update(label="Process complete!", state="complete", expanded=False)
    
    if delete_after:
        try:
            os.remove(audio_path)
        except:
            pass
    
    st.success("Meeting processed! You can now download the results below.")

# Sidebar
with st.sidebar:
    st.title("🎓 ClassmatePlus")
    st.markdown("---")
    st.info("Record your meetings and get AI-powered reviews instantly.")
    
    # Check OpenAI API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("API Key detected")
    else:
        st.error("API Key missing! Check your .env file.")
    
    st.markdown("---")
    st.caption("v0.1.0-beta")

# Main Page
st.title("Meeting Reviewer")

tabs = st.tabs(["🎤 Record Meeting", "📁 Upload Audio"])

with tabs[0]:
    st.subheader("Live Recording")
    st.info("💡 Recording happens in your browser. Note: System audio capture is limited in browser-side recording.")
    
    audio_data = mic_recorder(
        start_prompt="🔴 Start Recording",
        stop_prompt="⏹️ Stop & Process",
        just_once=True,
        use_container_width=True,
        format="wav",
        key="browser_recorder"
    )
    
    if audio_data:
        # Save browser recorded bytes to a temporary file
        temp_audio = "browser_recording.wav"
        with open(temp_audio, "wb") as f:
            f.write(audio_data['bytes'])
        
        st.session_state.audio_path = temp_audio
        process_audio(temp_audio, delete_after=True)

with tabs[1]:
    st.subheader("Process Audio File")
    uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a'])
    
    if uploaded_file is not None:
        if st.button("🚀 Process Uploaded File"):
            # Save uploaded file to temp
            with st.spinner("Uploading..."):
                with open("temp_upload.wav", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                process_audio("temp_upload.wav", delete_after=True)

# Results Display
if st.session_state.transcript or st.session_state.review:
    if st.session_state.review:
        st.markdown("---")
        st.subheader("📊 AI Review")
        
        review_data = st.session_state.review
        st.markdown(f"### Summary\n{review_data.get('summary', '')}")
        
        action_items = review_data.get('action_items', [])
        
        if action_items:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Key Points")
                for point in review_data.get('key_points', []):
                    st.markdown(f"- {point}")
            
            with col2:
                st.markdown("### Action Items")
                for item in action_items:
                    st.markdown(f"- [ ] {item}")
        else:
            st.markdown("### Key Points")
            for point in review_data.get('key_points', []):
                st.markdown(f"- {point}")
    
    st.markdown("---")
    st.subheader("📥 Download Results")
    down_col1, down_col2 = st.columns(2)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_name = Path(st.session_state.audio_path).stem if st.session_state.audio_path else "meeting"
    
    with down_col1:
        if st.session_state.transcript:
            st.download_button(
                label="📄 Download Transcript",
                data=st.session_state.transcript,
                file_name=f"{timestamp}_{audio_name}_transcript.txt",
                mime="text/plain"
            )
            
    with down_col2:
        if st.session_state.review:
            review_md = format_review(st.session_state.review, timestamp, st.session_state.audio_path or "N/A")
            st.download_button(
                label="📊 Download Review (Markdown)",
                data=review_md,
                file_name=f"{timestamp}_{audio_name}_review.md",
                mime="text/markdown"
            )
