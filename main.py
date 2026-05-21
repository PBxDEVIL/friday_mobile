from audio_mobile import listen_for_wake_word, speak
from brain_mobile import chat
from memory_mobile import add_conversation
import config

conversation_history = []

def main():
    print("FRIDAY Mobile Lite online. Say 'Friday' to start.")
    while True:
        try:
            cmd = listen_for_wake_word()
            if cmd:
                conversation_history.append({"role": "user", "content": cmd})
                response = chat(conversation_history)
                print(f"FRIDAY: {response}")
                speak(response)
                conversation_history.append({"role": "assistant", "content": response})
                add_conversation(cmd, response)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    main()
