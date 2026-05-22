cat > ~/friday_mobile/config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from the same folder

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID", "EXAVITQu4vr4xnSDxMaL")  # Jarvis-like voice
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
EOF
