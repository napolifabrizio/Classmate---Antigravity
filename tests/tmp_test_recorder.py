
from classmate.recorder import MeetingRecorder
import time
import os

def test_recorder():
    print("Initializing recorder...")
    recorder = MeetingRecorder()
    print("Starting recording for 3 seconds...")
    recorder.start()
    time.sleep(3)
    print("Stopping recording...")
    try:
        path = recorder.stop()
        print(f"Recording saved to: {path}")
        size = os.path.getsize(path)
        print(f"File size: {size} bytes")
        if size > 100:
            print("SUCCESS: Audio recorded.")
        else:
            print("FAILURE: File is empty or too small.")
        os.remove(path)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_recorder()
