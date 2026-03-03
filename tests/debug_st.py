import streamlit as st
import soundcard as sc
import ctypes

st.title("Soundcard Debug")

if st.button("Check Microphone"):
    try:
        mic = sc.default_microphone()
        st.success(f"Default Microphone: {mic}")
    except Exception as e:
        st.error(f"Error: {e}")
        import traceback
        st.code(traceback.format_exc())

if st.button("Check Microphone with CoInitialize"):
    try:
        ctypes.windll.ole32.CoInitialize(0)
        mic = sc.default_microphone()
        st.success(f"Default Microphone: {mic}")
    except Exception as e:
        st.error(f"Error (with CoInit): {e}")
        import traceback
        st.code(traceback.format_exc())
