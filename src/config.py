from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Keys (No default means it will throw an error if missing from .env)
    openai_api_key: str

    # Model Configurations
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    # Paths (Using defaults for local development)
    chroma_persist_dir: str = "../chroma_db"
    data_file_path: str = "../data/insurance_knowledge.json"

    # Pydantic v2 configuration for loading the .env file
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

# Instantiate a global settings object to be imported anywhere
settings = Settings()