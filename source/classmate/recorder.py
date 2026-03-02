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


class MeetingRecorder:
    def __init__(self, sample_rate: int = _SAMPLE_RATE, channels: int = _CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self.stop_event = threading.Event()
        self.mic_data: list[np.ndarray] = []
        self.spk_data: list[np.ndarray] = []
        self.mic = sc.default_microphone()
        self.speaker = sc.default_speaker()
        try:
            self.loopback = sc.get_microphone(id=self.speaker.id, include_loopback=True)
        except TypeError:
            self.loopback = sc.get_microphone(id=str(self.speaker.id))

    def _record_mic(self) -> None:
        try:
            with self.mic.recorder(samplerate=self.sample_rate, channels=self.channels) as recorder:
                while not self.stop_event.is_set():
                    self.mic_data.append(recorder.record(numframes=self.sample_rate // 10))
        except Exception:
            pass

    def _record_spk(self) -> None:
        try:
            with self.loopback.recorder(samplerate=self.sample_rate, channels=self.channels) as recorder:
                while not self.stop_event.is_set():
                    self.spk_data.append(recorder.record(numframes=self.sample_rate // 10))
        except Exception:
            pass

    def start(self) -> None:
        self.stop_event.clear()
        self.mic_data = []
        self.spk_data = []
        self.t_mic = threading.Thread(target=self._record_mic)
        self.t_spk = threading.Thread(target=self._record_spk)
        self.t_mic.start()
        self.t_spk.start()

    def stop(self) -> str:
        self.stop_event.set()
        self.t_mic.join()
        self.t_spk.join()

        if not self.mic_data and not self.spk_data:
            raise RuntimeError("No audio was recorded.")

        m_arr = np.concatenate(self.mic_data, axis=0) if self.mic_data else np.zeros((0, 1), dtype=np.float32)
        s_arr = np.concatenate(self.spk_data, axis=0) if self.spk_data else np.zeros((0, 1), dtype=np.float32)

        max_len = max(len(m_arr), len(s_arr))
        if len(m_arr) < max_len:
            m_arr = np.pad(m_arr, ((0, max_len - len(m_arr)), (0, 0)), mode='constant')
        if len(s_arr) < max_len:
            s_arr = np.pad(s_arr, ((0, max_len - len(s_arr)), (0, 0)), mode='constant')

        audio = m_arr + s_arr
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        sf.write(tmp.name, audio, self.sample_rate)
        return tmp.name


def record_meeting() -> str:
    """
    High-level wrapper for CLI: starts recording, waits for Enter, stops, returns path.
    """
    recorder = MeetingRecorder()
    recorder.start()
    input()  # blocks until user presses Enter
    return recorder.stop()


def record_until_enter() -> str:
    """Legacy wrapper."""
    return record_meeting()
