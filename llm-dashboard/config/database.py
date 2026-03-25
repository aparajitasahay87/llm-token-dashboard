from supabase import create_client, Client
from config.settings import settings

class Database:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            print("Database connection created")
        return cls._instance

    @property
    def client(self) -> Client:
        return self._client


db = Database()