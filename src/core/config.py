from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional # <-- IMPORT Optional

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    ALPHA_VANTAGE_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None  # <-- MAKE THIS LINE OPTIONAL
    GROQ_API_KEY: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
