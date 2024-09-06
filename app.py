import threading
import pyaudio
import wave
import io
import openai
import os
from pydub import AudioSegment
import time
import pyperclip

p = pyaudio.PyAudio()

# Set recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 8192  # Increased chunk size

print("Recording... Press Enter to stop.")
frames = []

stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=None)

is_recording = True

def record_audio():
    global is_recording
    stream.start_stream()
    while is_recording:
        if stream.is_active():
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        time.sleep(0.01)  # Small sleep to prevent busy-waiting

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

print("Saving to WAV file")
with wave.open("output.wav", "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print("Converting WAV to MP3")
audio = AudioSegment.from_wav("output.wav")
audio.export("output.mp3", format="mp3")

openai.api_key = os.getenv("OPENAI_API_KEY")

print("Transcribing audio")
with open("output.mp3", "rb") as audio_file:
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

print("Transcription:")
print(transcript['text'])

pyperclip.copy(transcript['text'])

# cleanup
os.remove("output.wav")
os.remove("output.mp3")