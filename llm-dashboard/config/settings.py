import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.SUPABASE_URL = os.getenv("SUPABASE_URL", "")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_REAL_KEY = os.getenv("OPENAI_REAL_KEY", "")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.APP_TITLE = "LLM Token Dashboard"
        self.REFRESH_INTERVAL = 3600
        self.DEBUG = True
        self.FREE_PROVIDERS = ["groq", "gemini", "mistral"]
        self.PAID_PROVIDERS = ["openai", "anthropic"]

settings = Settings()