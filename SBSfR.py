import speech_recognition as sr
import re
import pyperclip
import keyboard
import pyaudio

def process_command(text):
    match = re.search(r'\bcopy\s+(\w+)', text, re.IGNORECASE)
    if match:
        word = match.group(1)
        pyperclip.copy(word)
        print(f"[✅ Copied] {word}")
        keyboard.press_and_release('ctrl+v')  

def listen_microphone():
    recognizer = sr.Recognizer()
    print("Available Microphones:")
    def get_valid_input_devices():
        p = pyaudio.PyAudio()
        valid_devices = []
    
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                valid_devices.append((i, info["name"]))
        p.terminate()
        return valid_devices
    valid_mics = get_valid_input_devices()
    for idx, name in valid_mics:
        print(f"{idx}: {name}")
    device_index = int(input("\nEnter the device index of your microphone or virtual cable: "))
    try:
        mic = sr.Microphone(device_index=device_index)
        print(f"✅ Using input device #{device_index}")
    except OSError as e:
        print(f"❌ Could not access microphone: {e}")
        return

    with mic as source:
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
            print("\n👋 Exiting gracefully. Goodbye!")

listen_microphone()
