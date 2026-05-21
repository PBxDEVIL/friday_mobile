import speech_recognition as sr
import pyttsx3  # offline fallback
from elevenlabs import play, stream
from elevenlabs.client import ElevenLabs
import config
import io

client_eleven = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
engine_offline = pyttsx3.init()

def listen_for_wake_word(wake_word="friday"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"Waiting for '{wake_word}'...")
        while True:
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
                text = r.recognize_google(audio).lower()
                if wake_word in text:
                    print("Wake word detected.")
                    audio_cmd = r.listen(source, timeout=5, phrase_time_limit=8)
                    command = r.recognize_google(audio_cmd)
                    print(f"Command: {command}")
                    return command
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue

def speak(text):
    try:
        audio = client_eleven.generate(text=text, voice=config.VOICE_ID)
        play(audio)
    except Exception as e:
        print("ElevenLabs failed, using offline TTS:", e)
        engine_offline.say(text)
        engine_offline.runAndWait()
