
import os
from dotenv import load_dotenv

# Load từ file .env nếu có
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-nano")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
