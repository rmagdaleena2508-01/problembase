from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    groq_api_key: str
    reddit_client_id: str = "x"
    reddit_client_secret: str = "x"
    reddit_user_agent: str = "problembase/1.0"
    github_token: str
    app_name: str = "ProblemBase"
    app_version: str = "1.0.0"
    debug: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
