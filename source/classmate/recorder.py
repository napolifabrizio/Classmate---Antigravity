"""
recorder.py
-----------
Records audio from the default microphone until the user presses Enter,
then saves the result as a temporary WAV file ready to be transcribed.
"""

from __future__ import annotations
import tempfile
import threading
from pathlib import Path

import numpy as np
import soundcard as sc
import soundfile as sf


# Recording parameters
_SAMPLE_RATE = 16_000   # Whisper works best at 16 kHz
_CHANNELS = 1           # Mono is enough and halves the file size


def record_until_enter() -> str:
    """
    Start recording the microphone and system audio loopback. Returns the path 
    to a temporary WAV file that contains the full recording once the user presses Enter.

    Returns
    -------
    str
        Absolute path to the temporary WAV file.
    """
    return record_meeting()


def record_meeting() -> str:
    """
    High-level wrapper: starts recording, waits for Enter, stops, returns path.
    This function is meant to be called from the CLI.
    """
    mic = sc.default_microphone()
    speaker = sc.default_speaker()
    
    try:
        loopback = sc.get_microphone(id=speaker.id, include_loopback=True)
    except TypeError:
        # Fallback for older soundcard versions
        loopback = sc.get_microphone(id=str(speaker.id))

    stop_event = threading.Event()
    mic_data: list[np.ndarray] = []
    spk_data: list[np.ndarray] = []

    def _record_mic() -> None:
        try:
            with mic.recorder(samplerate=_SAMPLE_RATE, channels=_CHANNELS) as recorder:
                while not stop_event.is_set():
                    mic_data.append(recorder.record(numframes=_SAMPLE_RATE // 10))
        except Exception:
            pass

    def _record_spk() -> None:
        try:
            with loopback.recorder(samplerate=_SAMPLE_RATE, channels=_CHANNELS) as recorder:
                while not stop_event.is_set():
                    spk_data.append(recorder.record(numframes=_SAMPLE_RATE // 10))
        except Exception:
            pass

    t_mic = threading.Thread(target=_record_mic)
    t_spk = threading.Thread(target=_record_spk)
    t_mic.start()
    t_spk.start()

    input()  # blocks until user presses Enter
    stop_event.set()
    
    t_mic.join()
    t_spk.join()

    if not mic_data and not spk_data:
        raise RuntimeError("No audio was recorded.")

    m_arr = np.concatenate(mic_data, axis=0) if mic_data else np.zeros((0, 1), dtype=np.float32)
    s_arr = np.concatenate(spk_data, axis=0) if spk_data else np.zeros((0, 1), dtype=np.float32)

    # Pad the shorter array with zeros
    max_len = max(len(m_arr), len(s_arr))
    if len(m_arr) < max_len:
        m_arr = np.pad(m_arr, ((0, max_len - len(m_arr)), (0, 0)), mode='constant')
    if len(s_arr) < max_len:
        s_arr = np.pad(s_arr, ((0, max_len - len(s_arr)), (0, 0)), mode='constant')

    # Sum Mic and Speakers to create a single Mono track
    audio = m_arr + s_arr

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    sf.write(tmp.name, audio, _SAMPLE_RATE)

    return tmp.name
