from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str

    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    chroma_persist_dir: str = "../chroma_db"
    data_file_path: str = "../data/insurance_knowledge.json"

    api_stream_url: str = "http://127.0.0.1:8000/api/v1/chat/stream"

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()