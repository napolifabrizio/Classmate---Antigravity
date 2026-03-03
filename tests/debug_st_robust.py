import streamlit as st
import ctypes
import soundcard as sc

st.title("Soundcard Robust Debug")

# Try to initialize at top level
try:
    if hasattr(ctypes.windll, 'ole32'):
        ctypes.windll.ole32.CoInitialize(0)
    st.write("Top-level CoInitialize called.")
except Exception as e:
    st.write(f"Top-level CoInitialize failed: {e}")

def get_mic():
    try:
        if hasattr(ctypes.windll, 'ole32'):
            ctypes.windll.ole32.CoInitialize(0)
        return sc.default_microphone()
    except Exception as e:
        return f"Error: {e}"

if st.button("Check Mic (with func)"):
    st.write(f"Result: {get_mic()}")

if st.button("Check Mic (direct)"):
    try:
        st.write(f"Result: {sc.default_microphone()}")
    except Exception as e:
        st.write(f"Error: {e}")
