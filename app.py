import threading
import pyaudio
import wave
import openai
import os
import ffmpeg
import time
import argparse
import pyperclip
from dotenv import load_dotenv

# Optional: Faster-Whisper import
try:
    from faster_whisper import WhisperModel
    HAS_LOCAL_WHISPER = True
except ImportError:
    HAS_LOCAL_WHISPER = False

# Load env vars from .env if present
load_dotenv()

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Record and transcribe audio.")
parser.add_argument("--local", action="store_true", help="Use local Faster-Whisper instead of OpenAI")
parser.add_argument("--language", type=str, default="en", help="Language code for transcription (default: en)")
args = parser.parse_args()

# Setup audio config
p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 8192
frames = []

print("Recording... Press Enter to stop.")

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
is_recording = True

def record_audio():
    global is_recording
    stream.start_stream()
    while is_recording:
        if stream.is_active():
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        time.sleep(0.01)

def stop_recording():
    global is_recording
    input()
    is_recording = False
    print("Recording stopped.")

record_thread = threading.Thread(target=record_audio)
stop_thread = threading.Thread(target=stop_recording)
record_thread.start()
stop_thread.start()
record_thread.join()
stop_thread.join()

stream.stop_stream()
stream.close()
p.terminate()

current_directory = os.getcwd()
print("Current directory:", current_directory)

# Save WAV file
with wave.open("output.wav", "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

# Convert to MP3
print("Converting WAV to MP3...")
try:
    (
        ffmpeg
        .input("output.wav")
        .output("output.mp3")
        .run(capture_stdout=True, capture_stderr=True, quiet=True, overwrite_output=True)
    )
except ffmpeg.Error as e:
    print(f"FFmpeg error: {e.stderr.decode()}")
    exit(1)

# Define transcribers
def transcribe_with_openai(audio_path):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY missing in environment or .env file.")
        exit(1)

    openai.api_key = api_key
    print("Transcribing with OpenAI (whisper-1)...")
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]

def transcribe_with_local_whisper(audio_path):
    if not HAS_LOCAL_WHISPER:
        print("Error: faster-whisper not installed. Run `pip install faster-whisper`.")
        exit(1)

    print(f"Transcribing with local Faster-Whisper (language: {args.language})...")
    model = WhisperModel("large-v3", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language=args.language)
    return " ".join(segment.text for segment in segments)

# Transcribe using selected method
if args.local:
    transcript_text = transcribe_with_local_whisper("output.mp3")
else:
    transcript_text = transcribe_with_openai("output.mp3")

# Output and copy
print("\nTranscription:\n")
print(transcript_text.strip())
pyperclip.copy(transcript_text.strip())
print("\n✅ Copied to clipboard.")

# Clean up
os.remove("output.wav")
os.remove("output.mp3")
