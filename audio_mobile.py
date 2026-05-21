import speech_recognition as sr
import pyttsx3  # offline fallback
from elevenlabs import play, stream
from elevenlabs.client import ElevenLabs
import config
import io
import subprocess, json

client_eleven = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
engine_offline = pyttsx3.init()

def listen_for_wake_word(wake_word="friday"):
    print(f"Waiting for '{wake_word}'...")
    while True:
        # Call Android's built-in speech recognition
        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            text = data.get("text", "").lower()
            if wake_word in text:
                print("Wake word detected, now speak command...")
                cmd_result = subprocess.run(
                    ["termux-speech-to-text"],
                    capture_output=True, text=True, timeout=10
                )
                if cmd_result.returncode == 0:
                    cmd_data = json.loads(cmd_result.stdout)
                    command = cmd_data.get("text", "")
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
