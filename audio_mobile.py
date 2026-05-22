cat > ~friday_mobile/audio_mobile.py << 'EOF'
import subprocess
import json
import config
from elevenlabs import play
from elevenlabs.client import ElevenLabs

client_eleven = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)

def listen_for_wake_word(wake_word="friday"):
    """Use Android built-in speech recognizer via Termux:API."""
    print(f"Waiting for wake word '{wake_word}'...")
    while True:
        try:
            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                continue
            data = json.loads(result.stdout)
            text = data.get("text", "").lower()
        except (subprocess.TimeoutExpired, json.JSONDecodeError):
            continue

        if wake_word in text:
            print("Wake word detected. Speak your command...")
            try:
                cmd_result = subprocess.run(
                    ["termux-speech-to-text"],
                    capture_output=True, text=True, timeout=10
                )
                if cmd_result.returncode == 0:
                    cmd_data = json.loads(cmd_result.stdout)
                    command = cmd_data.get("text", "")
                    print(f"Command: {command}")
                    return command
            except Exception as e:
                print("Error capturing command:", e)
                continue

def speak(text):
    """Use ElevenLabs, fallback to Android TTS."""
    try:
        audio = client_eleven.generate(text=text, voice=config.VOICE_ID)
        play(audio)
    except Exception as e:
        print("ElevenLabs failed, using Android TTS:", e)
        subprocess.run(["termux-tts-speak", text])
EOF
