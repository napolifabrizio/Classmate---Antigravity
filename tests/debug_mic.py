import soundcard as sc
try:
    print("Default Microphone:", sc.default_microphone())
except Exception as e:
    print("Error getting default microphone:", e)
    import traceback
    traceback.print_exc()

try:
    print("All Microphones:", sc.all_microphones())
except Exception as e:
    print("Error getting all microphones:", e)
