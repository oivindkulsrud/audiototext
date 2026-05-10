import threading
import pyaudio
import wave
import openai
import os
import ffmpeg
import time
import argparse
import pyperclip
import shutil
from array import array
from datetime import datetime
from pathlib import Path
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
parser.add_argument(
    "--debug-save-recording",
    action="store_true",
    help="Save a timestamped copy of the recorded MP3 before cleanup",
)
parser.add_argument(
    "--debug-recording-dir",
    type=Path,
    default=Path("debug_recordings"),
    help="Directory for --debug-save-recording files (default: debug_recordings)",
)
parser.add_argument(
    "--list-devices",
    action="store_true",
    help="List available audio input devices and exit",
)
parser.add_argument(
    "--input-device-index",
    type=int,
    default=None,
    help="PyAudio input device index to use for recording",
)
parser.add_argument(
    "--gain-db",
    type=float,
    default=0.0,
    help="Apply audio gain during MP3 conversion, for example --gain-db 12",
)
args = parser.parse_args()

# Setup audio config
p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 8192
frames = []

def list_input_devices():
    print("Available audio input devices:")
    for index in range(p.get_device_count()):
        device = p.get_device_info_by_index(index)
        if int(device.get("maxInputChannels", 0)) > 0:
            default_marker = " (default)" if index == p.get_default_input_device_info().get("index") else ""
            print(f"  {index}: {device.get('name')}{default_marker}")

if args.list_devices:
    list_input_devices()
    p.terminate()
    exit(0)

print("Recording... Press Enter to stop.")

try:
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=args.input_device_index,
        frames_per_buffer=CHUNK,
    )
except OSError as e:
    print(f"Could not open microphone: {e}")
    list_input_devices()
    p.terminate()
    exit(1)

sample_width = p.get_sample_size(FORMAT)
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

samples = array("h")
samples.frombytes(b"".join(frames))
if samples:
    peak = max(abs(sample) for sample in samples)
    rms = (sum(sample * sample for sample in samples) / len(samples)) ** 0.5
    print(f"Recorded level: peak {peak / 32768:.1%}, rms {rms / 32768:.1%}")
    if peak < 500:
        print("Recorded signal is very low. Try another MIC index or raise Windows input volume.")

# Save WAV file
with wave.open("output.wav", "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

# Convert to MP3
print("Converting WAV to MP3...")
try:
    audio = ffmpeg.input("output.wav")
    if args.gain_db:
        audio = audio.filter("volume", f"{args.gain_db}dB")
    audio.output("output.mp3").run(capture_stdout=True, capture_stderr=True, quiet=True, overwrite_output=True)
except FileNotFoundError:
    print("FFmpeg executable not found. Install ffmpeg and open a new terminal so PATH is updated.")
    print("Windows: winget install Gyan.FFmpeg")
    exit(1)
except ffmpeg.Error as e:
    print(f"FFmpeg error: {e.stderr.decode()}")
    exit(1)

if args.debug_save_recording:
    args.debug_recording_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    debug_audio_path = args.debug_recording_dir / f"recording_{timestamp}.mp3"
    shutil.copy2("output.mp3", debug_audio_path)
    print(f"Saved debug recording: {debug_audio_path}")

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
