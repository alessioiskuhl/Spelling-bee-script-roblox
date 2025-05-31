import subprocess
def execute_in_terminal():
    subprocess.run(['pip', 'install', 'pyaudio'], check=True)
    subprocess.run(['pip', 'install', 'sounddevice'], check=True)
    subprocess.run(['pip', 'install', 'scipy'], check=True)

if __name__ == "__main__":
    execute_in_terminal()

import speech_recognition as sr
import re
import pyperclip
import keyboard
import pyaudio
import sounddevice as sd
import numpy as np
import io
import scipy.io.wavfile as wav
import speech_recognition as sr
import psutil, os, threading, time


def monitor_memory(interval=1):
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / (1024 ** 2)  # MB
        print(f"🧠 Memory Usage: {mem:.2f} MB")
        time.sleep(interval)

def process_command(text):
    match = re.search(r'\bcopy\s+(\w+)', text, re.IGNORECASE)
    if match:
        word = match.group(1)
        pyperclip.copy(word)
        print(f"[✅ Copied] {word}")
        keyboard.press_and_release('ctrl+v') 


duration = 5
sample_rate = 44100

print("Available Microphones:")
for i, dev in enumerate(sd.query_devices()):
    print(f"{i}: {dev['name']} - {dev['hostapi']}")

device_index = int(input("\nEnter the device index of your microphone or virtual cable: "))

try:
    print(f"✅ Using input device #{device_index}")
except OSError as e:
    print(f"❌ Could not access microphone/desktop audio: {e}")

threading.Thread(target=monitor_memory, daemon=True).start()

print("🔴 Recording...")
audio_data = sd.rec(int(sample_rate * duration),
                    samplerate=sample_rate,
                    channels=2,
                    dtype='float32',
                    device=device_index)
sd.wait()

audio_data_int16 = np.int16(audio_data * 32767)
mem_wav = io.BytesIO()
wav.write(mem_wav, sample_rate, audio_data_int16)
mem_wav.seek(0)

recognizer = sr.Recognizer()
with sr.AudioFile(mem_wav) as source:
    audio = recognizer.record(source)
    print("🎤 Calibrating for ambient noise...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("✅ Ready. Say something like 'copy password'.")

    try:
        while True:
            print("🎧 Listening...")
            audio = recognizer.listen(source)
            print("🔄 Processing...")
            try:
                text = recognizer.recognize_google(audio)
                print(f"🗣 Heard: {text}")
                process_command(text)
            except sr.UnknownValueError:
                print("❌ Could not understand.")
            except sr.RequestError as e:
                print(f"❌ API error: {e}")
    except KeyboardInterrupt:
        print("\n👋 See you soon. Goodbye!")
